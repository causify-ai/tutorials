import { ChatOpenAI } from '@langchain/openai';
import { createAgent, todoListMiddleware, summarizationMiddleware } from 'langchain';
import {
  createFilesystemMiddleware,
  createSubAgentMiddleware,
  createPatchToolCallsMiddleware,
  FilesystemBackend
} from 'deepagents';
import type { BaseMessage } from '@langchain/core/messages';
import type { AppConfig } from '../config/index.js';
import type { UsageMetadata } from '../state/usage.js';
import { buildTools } from '../tools/index.js';
import type { ImageAttachment } from '../utils/images.js';

const parsedLimit = Number(process.env.AGEN_TUI_RECURSION_LIMIT ?? '100');
const DEFAULT_RECURSION_LIMIT = Number.isFinite(parsedLimit) && parsedLimit > 0 ? parsedLimit : 100;

export type AgentRole = 'user' | 'assistant' | 'system';
export interface AgentMessage {
  role: AgentRole;
  content: string;
  images?: ImageAttachment[];
}

export interface AgentResult {
  text: string;
  finalMessage?: BaseMessage;
  usage?: UsageMetadata | null;
  model?: string;
}

export interface AgentRunner {
  run: (messages: AgentMessage[]) => Promise<AgentResult>;
  stream: (messages: AgentMessage[], options?: any) => AsyncIterable<any>;
  summarize: (
    messages: AgentMessage[],
    context: { actions?: string; fallbackReasoning?: string; lastUser?: string }
  ) => Promise<AgentResult>;
}

export const createAgentRunner = (config: AppConfig): AgentRunner => {
  const model = new ChatOpenAI({
    apiKey: config.openAIApiKey,
    model: config.openAIModel
  });

  const workspaceRoot = process.cwd();
  const backend = new FilesystemBackend({
    rootDir: workspaceRoot,
    virtualMode: false
  });
  const customTools = buildTools(workspaceRoot);

  const makeAgent = () => {
    const finalSystemPrompt = `${config.systemPrompt}\n\nIn order to complete the objective that the user asks of you, you have access to a number of standard tools.`;
    const middleware = [
      todoListMiddleware(),
      createFilesystemMiddleware({ backend }),
      createSubAgentMiddleware({
        defaultModel: model,
        defaultTools: customTools,
        defaultMiddleware: [
          todoListMiddleware(),
          createFilesystemMiddleware({ backend }),
          summarizationMiddleware({
            model,
            trigger: { tokens: 170_000 },
            keep: { messages: 6 }
          }),
          createPatchToolCallsMiddleware()
        ],
        generalPurposeAgent: true
      }),
      summarizationMiddleware({
        model,
        trigger: { tokens: 170_000 },
        keep: { messages: 6 }
      }),
      createPatchToolCallsMiddleware()
    ];

    return createAgent({
      model,
      systemPrompt: finalSystemPrompt,
      tools: customTools,
      middleware
    });
  };

  const agent = makeAgent();

  const toDeepMessage = (message: AgentMessage) => {
    if (message.images && message.images.length > 0) {
      const parts: Array<{ type: 'text' | 'image_url'; text?: string; image_url?: { url: string } }> = [];
      if (message.content && message.content.trim().length) {
        parts.push({ type: 'text', text: message.content });
      }
      message.images.forEach((img) => {
        parts.push({ type: 'image_url', image_url: { url: img.dataUrl } });
      });
      return { role: message.role, content: parts };
    }
    return message;
  };

  const run = async (messages: AgentMessage[]): Promise<AgentResult> => {
    const result = await agent.invoke(
      { messages: messages.map(toDeepMessage) },
      { recursionLimit: DEFAULT_RECURSION_LIMIT }
    );
    const finalMessage = result.messages[result.messages.length - 1];
    let text = '';
    const content = finalMessage?.content;
    if (typeof content === 'string') {
      text = content;
    } else if (Array.isArray(content)) {
      text = content
        .map((part) => {
          if (typeof part === 'string') return part;
          if (typeof part === 'object' && part !== null && 'text' in part) {
            const maybeText = (part as { text?: string }).text;
            return maybeText ?? '';
          }
          return JSON.stringify(part);
        })
        .join('\n');
    } else if (content && typeof content === 'object') {
      text = JSON.stringify(content);
    }

    const usage = extractUsage(finalMessage);
    const actualModel = extractModelIdentifier(finalMessage);
    return { text, finalMessage, usage, model: actualModel };
  };

  const stream = (messages: AgentMessage[], options?: Parameters<typeof agent.streamEvents>[2]) =>
    agent.streamEvents(
      { messages: messages.map(toDeepMessage) },
      { recursionLimit: DEFAULT_RECURSION_LIMIT },
      options
    );

  const summarize = async (
    messages: AgentMessage[],
    context: { actions?: string; fallbackReasoning?: string; lastUser?: string }
  ): Promise<AgentResult> => {
    const lastUserText = context.lastUser ?? messages.slice().reverse().find((m) => m.role === 'user')?.content ?? '';
    const prompt: AgentMessage[] = [
      {
        role: 'system',
        content:
          'You are a concise, friendly assistant. Respond conversationally. If actions/results are provided, weave them into a one-sentence/short paragraph answer. Do NOT repeat raw action logs or headings. Avoid canned phrases like "All set". If no actions exist, answer the user plainly.'
      },
      {
        role: 'user',
        content: `Request: ${lastUserText}\nActions/Results: ${context.actions ?? 'none'}\nNotes: ${context.fallbackReasoning ?? ''}`
      }
    ];
    return run(prompt);
  };

  return { run, stream, summarize };
};

const extractModelIdentifier = (message?: BaseMessage | null): string | undefined => {
  if (!message) return undefined;
  const metadata = message.response_metadata as
    | {
        model?: string;
        model_name?: string;
        response?: { model?: string };
      }
    | undefined;
  return metadata?.model ?? metadata?.model_name ?? metadata?.response?.model;
};

const extractUsage = (message?: BaseMessage | null): UsageMetadata | null => {
  if (!message) return null;
  const maybeUsage = (message as BaseMessage & { usage_metadata?: UsageMetadata }).usage_metadata;
  if (maybeUsage) return maybeUsage;
  const metadata = message.response_metadata as
    | { tokenUsage?: { promptTokens?: number; completionTokens?: number; totalTokens?: number } }
    | undefined;
  const tokenUsage = metadata?.tokenUsage;
  if (!tokenUsage) return null;
  return {
    input_tokens: tokenUsage.promptTokens ?? undefined,
    output_tokens: tokenUsage.completionTokens ?? undefined,
    total_tokens: tokenUsage.totalTokens ?? undefined
  };
};
