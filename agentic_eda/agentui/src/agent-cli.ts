#!/usr/bin/env tsx
import process from 'node:process';
import { loadConfig } from './config/index.js';
import { createAgentRunner, type AgentMessage } from './agent/index.js';
import { prepareAgentInput } from './agent/prompt.js';
import { streamAgentEvents } from './agent/events.js';
import type { MessageAction } from './state/session.js';
import { formatActionSummary, formatActionDigest } from './utils/actions.js';
import { splitReasoningAndAnswer } from './utils/messages.js';
import { maybeExecuteFsCommand } from './fs/shortcuts.js';
import { loadImageAttachments } from './utils/images.js';

const main = async () => {
  const prompt = process.argv.slice(2).join(' ').trim();
  if (!prompt) {
    console.error('Usage: npm run agent -- "prompt"');
    process.exit(1);
  }

  const config = loadConfig();
  const runner = createAgentRunner(config);
  const root = process.cwd();
  const shortcut = await maybeExecuteFsCommand(prompt, root);
  if (shortcut) {
    console.log(shortcut);
    return;
  }

  const prepared = prepareAgentInput(prompt, root);
  const images = await loadImageAttachments(root, prepared.mentionedFiles);
  const messages: AgentMessage[] = [{ role: 'user', content: prepared.content, images }];
  const finalState = await streamAgentEvents(runner, messages, () => {});
  const sections = splitReasoningAndAnswer(finalState.answer);
  const reasoning = sections.reasoning || finalState.reasoning.trim();
  const actions = finalState.actions;
  const showReasoning =
    (finalState.showReasoning ?? sections.visible ?? false) && reasoning.trim().length > 0;

  const actionDigest = formatActionDigest(actions);
  const actionLines = actions
    .filter((a) => a.status === 'success')
    .map((a) => a.detail?.trim())
    .filter(Boolean) as string[];

  let modelAnswer = sections.answer?.trim();
  const lastUserMessage = messages[messages.length - 1]?.content ?? '';
  const isGenericAllSet = modelAnswer && /all set\.\s*let me know/i.test(modelAnswer);
  const isGreeting = /\b(hi|hello|hey|thanks|thank you|how are you)\b/i.test(lastUserMessage);

  const looksLikeDigest = modelAnswer && /completed actions/i.test(modelAnswer);
  if (!modelAnswer || looksLikeDigest) {
    try {
      const summary = await runner.summarize(messages, {
        actions: actionDigest,
        fallbackReasoning: reasoning,
        lastUser: lastUserMessage
      });
      modelAnswer = summary.text?.trim();
    } catch {
      modelAnswer = '';
    }
  }

  if (!actions.length && (!modelAnswer || isGenericAllSet)) {
    if (/\b(thanks|thank you)\b/i.test(lastUserMessage)) {
      modelAnswer = 'You’re welcome!';
    } else if (/\b(how are you)\b/i.test(lastUserMessage)) {
      modelAnswer = 'I’m doing well—ready to help. How can I assist?';
    } else if (isGreeting) {
      modelAnswer = 'Hi there! What can I help you with?';
    } else if (!modelAnswer) {
      modelAnswer = lastUserMessage ? `Got it: ${lastUserMessage}` : 'How can I help?';
    }
  }

  let finalAnswer = modelAnswer?.trim() || '';
  if (!finalAnswer) {
    if (actionLines.length) {
      finalAnswer = `Here’s what I found:\n- ${actionLines.join('\n- ')}`;
    } else if (actionDigest) {
      finalAnswer = actionDigest;
    } else {
      finalAnswer = modelAnswer || 'How can I help?';
    }
  }

  finalAnswer = stripStructuredNoise(finalAnswer);

  if (showReasoning) {
    console.log('Reasoning:');
    console.log(reasoning.trim());
  }
  if (actions.length) {
    console.log(showReasoning ? '\nActions:' : 'Actions:');
    actions.forEach((action: MessageAction) => {
      console.log(formatActionSummary(action));
    });
  }
  console.log('\nAnswer:');
  console.log(finalAnswer.trim());
};

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
  const stripStructuredNoise = (answer: string) => {
    if (!answer) return '';
    let cleaned = answer.replace(/ReasoningVisible:.*\n?/gi, '');
    cleaned = cleaned.replace(/Plan:\n[\s\S]*?(?=\n\n|Actions:|Answer:|$)/gi, '');
    cleaned = cleaned.replace(/Actions:\n[\s\S]*?(?=\n\n|Answer:|$)/gi, '');
    cleaned = cleaned.replace(/Completed actions.*$/gim, '').trim();
    return cleaned.trim();
  };
