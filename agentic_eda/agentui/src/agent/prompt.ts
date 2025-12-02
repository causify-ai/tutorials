import {
  extractMentionMetadata,
  replaceMentionsWithPaths
} from '../ui/mentions.js';
import { routePrompt, type RouteDecision, type PromptIntent } from './router.js';
import { NOTEBOOK_BEST_PRACTICES } from './notebook-tips.js';

const formatMetadataBlock = (title: string, lines: string[]) => {
  const body = lines.map((line) => `- ${line}`).join('\n');
  return `[${title}]\n${body}`;
};

export interface PreparedAgentInput {
  content: string;
  decision: RouteDecision;
  includedNotebookTips: boolean;
  mentionedFiles: string[];
}

export interface PrepareAgentInputOptions {
  lastIntent?: PromptIntent | null;
  notebookTipsShown?: boolean;
}

export const prepareAgentInput = (
  prompt: string,
  workspaceRoot: string,
  options: PrepareAgentInputOptions = {}
): PreparedAgentInput => {
  const mentionMetadata = extractMentionMetadata(prompt, workspaceRoot);
  const normalized = replaceMentionsWithPaths(prompt, workspaceRoot);
  const decision = routePrompt(prompt, {
    hasMention: Boolean(mentionMetadata),
    lastIntent: options.lastIntent ?? null
  });
  const shouldIncludeNotebookTips = decision.intent === 'notebook' && !options.notebookTipsShown;

  const metadataBlocks: string[] = [];
  metadataBlocks.push(
    formatMetadataBlock('Intent', [
      `category: ${decision.intent}`,
      `confidence: ${(decision.confidence * 100).toFixed(0)}%`,
      `reason: ${decision.reason}`,
      `instruction: ${decision.instructions}`
    ])
  );

  if (shouldIncludeNotebookTips) {
    const guardrailLines = NOTEBOOK_BEST_PRACTICES.split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
    metadataBlocks.push(formatMetadataBlock('Notebook guardrails', guardrailLines));
  }

  if (mentionMetadata) {
    metadataBlocks.push(
      formatMetadataBlock(
        'Mentioned files',
        mentionMetadata.mentioned_files.map((file) => file)
      )
    );
  }

  const content =
    metadataBlocks.length > 0
      ? `${normalized}\n\n${metadataBlocks.join('\n\n')}`
      : normalized;

  return {
    content,
    decision,
    includedNotebookTips: shouldIncludeNotebookTips,
    mentionedFiles: mentionMetadata?.mentioned_files ?? []
  };
};
