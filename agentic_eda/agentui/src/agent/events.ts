import type { AgentMessage, AgentRunner } from './index.js';
import type { MessageAction } from '../state/session.js';
import type { TokenUsage } from '../state/usage.js';
import { formatActionDigest } from '../utils/actions.js';
import {
  splitReasoningAndAnswer,
  stripReasoningVisibilityLine
} from '../utils/messages.js';
import { describeToolAction } from '../utils/tool-summaries.js';
import { formatToolDetail } from '../utils/text.js';

export type PlanSource = 'llm' | 'todos';

export type AgentStructuredEvent =
  | { kind: 'plan'; text: string; source: PlanSource }
  | { kind: 'action'; action: MessageAction }
  | { kind: 'usage'; usage: TokenUsage }
  | { kind: 'model'; model: string }
  | { kind: 'reasoning_visibility'; visible: boolean }
  | { kind: 'answer'; text: string };

export interface AgentStreamState {
  reasoning: string;
  answer: string;
  actions: MessageAction[];
  usage?: TokenUsage | null;
  model?: string;
  showReasoning?: boolean;
}

const normalizeContent = (value: unknown): string => {
  if (!value) return '';
  if (typeof value === 'string') {
    return value;
  }
  if (Array.isArray(value)) {
    return value.map((entry) => normalizeContent(entry)).join('');
  }
  if (typeof value === 'object') {
    if ('text' in (value as Record<string, unknown>)) {
      const maybe = (value as { text?: string }).text;
      return typeof maybe === 'string' ? maybe : '';
    }
    try {
      return JSON.stringify(value);
    } catch {
      return '';
    }
  }
  return String(value);
};

const getChunkContent = (chunk: any): unknown => {
  if (!chunk) return '';
  if ('content' in chunk && chunk.content !== undefined) {
    return chunk.content;
  }
  if ('kwargs' in chunk && chunk.kwargs && 'content' in chunk.kwargs) {
    return chunk.kwargs.content;
  }
  return '';
};

const extractUsageFromChunk = (chunk: any): TokenUsage | null => {
  const usage =
    chunk?.usage_metadata ??
    chunk?.response_metadata?.usage ??
    chunk?.kwargs?.response_metadata?.usage;
  if (!usage) return null;
  const inputTokens = usage.prompt_tokens ?? usage.promptTokens ?? 0;
  const outputTokens = usage.completion_tokens ?? usage.completionTokens ?? 0;
  const totalTokens =
    usage.total_tokens ?? usage.totalTokens ?? inputTokens + outputTokens;
  if (!inputTokens && !outputTokens && !totalTokens) {
    return null;
  }
  return { inputTokens, outputTokens, totalTokens };
};

const VISIBILITY_REGEX = /ReasoningVisible:\s*(yes|no)/i;
const STRUCTURED_SECTION_REGEX = /(Actions:|Answer:)/i;
const TODO_REGEX = /"update"\s*:\s*{[^}]*"content"\s*:\s*"([^"]+)"[^}]*}/i;
const NORMALIZE_WS = (value: string) => value.replace(/\s+/g, ' ').trim();

const pruneAnswerFromReasoning = (reasoning: string, answer: string) => {
  if (!reasoning || !answer) return reasoning;
  const normalizedAnswer = NORMALIZE_WS(answer);
  if (!normalizedAnswer) return reasoning;
  let pruned = reasoning;
  if (NORMALIZE_WS(reasoning).includes(normalizedAnswer)) {
    const escaped = answer.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    pruned = pruned.replace(new RegExp(escaped, 'g'), '').trim();
  }
  const answerLines = answer
    .split('\n')
    .map(NORMALIZE_WS)
    .filter(Boolean);
  const reasoningLines = pruned
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => {
      const norm = NORMALIZE_WS(line);
      if (!norm) return false;
      return !answerLines.includes(norm);
    });
  return reasoningLines.join('\n').trim();
};

const formatPlanText = (raw: unknown): string => {
  if (!raw) return '';
  if (typeof raw === 'string') {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object') {
        const maybeUpdate = (parsed as any).update?.content;
        if (typeof maybeUpdate === 'string') return maybeUpdate;
      }
    } catch {
      // ignore
    }
    const match = TODO_REGEX.exec(raw);
    if (match?.[1]) return match[1];
    return raw;
  }
  try {
    const stringified = JSON.stringify(raw);
    const match = TODO_REGEX.exec(stringified);
    if (match?.[1]) return match[1];
    return stringified;
  } catch {
    return String(raw);
  }
};

const unwrapToolOutput = (output: unknown) => {
  if (output && typeof output === 'object' && 'content' in (output as Record<string, unknown>)) {
    const content = (output as { content?: unknown }).content;
    if (typeof content === 'string') return content;
  }
  return output;
};

export const streamAgentEvents = async (
  runner: AgentRunner,
  messages: AgentMessage[],
  onEvent: (event: AgentStructuredEvent) => void
): Promise<AgentStreamState> => {
  const state: AgentStreamState = {
    reasoning: '',
    answer: '',
    actions: [],
    showReasoning: undefined
  };
  const actionsMap = new Map<string, MessageAction>();
  const planToolRunIds = new Set<string>();
  const stream = runner.stream(messages);
  let visibilityBuffer = '';
  let pendingReasoning = '';
  const modelTextParts: string[] = [];
  const seenAnswerChunks: string[] = [];
  let lastPlanText = '';

  const recordModelText = (value: string) => {
    if (!value) return;
    const cleaned = stripReasoningVisibilityLine(value).text;
    if (cleaned && cleaned.trim().length > 0) {
      modelTextParts.push(cleaned);
    }
  };

  const truncatePlanText = (value: string) => {
    const idx = value.search(STRUCTURED_SECTION_REGEX);
    if (idx === -1) return value;
    return value.slice(0, idx).trim();
  };

  const emitPlan = (text: string, source: PlanSource) => {
    const cleaned = truncatePlanText(text.trim());
    if (NORMALIZE_WS(cleaned) === NORMALIZE_WS(lastPlanText)) {
      return;
    }
    lastPlanText = cleaned;
    state.reasoning = cleaned;
    onEvent({ kind: 'plan', text: state.reasoning, source });
  };

  const flushPendingPlan = (text: string) => emitPlan(text, 'llm');

  const consumeVisibilitySignal = (chunkText: string): string => {
    if (state.showReasoning !== undefined) {
      return chunkText;
    }
    visibilityBuffer += chunkText;
    const match = VISIBILITY_REGEX.exec(visibilityBuffer);
    if (!match) {
      return '';
    }
    state.showReasoning = match[1].toLowerCase() === 'yes';
    onEvent({ kind: 'reasoning_visibility', visible: state.showReasoning });
    const before = visibilityBuffer.slice(0, match.index);
    const after = visibilityBuffer
      .slice(match.index + match[0].length)
      .replace(/^\s*/, '');
    pendingReasoning += `${before}${after}`;
    visibilityBuffer = '';
    if (state.showReasoning) {
      const toFlush = pendingReasoning;
      pendingReasoning = '';
      flushPendingPlan(toFlush);
    } else {
      pendingReasoning = '';
    }
    return '';
  };

  for await (const raw of stream) {
    const event = raw ?? {};
    if (event.event === 'on_chat_model_stream') {
      let chunkText = normalizeContent(getChunkContent(event?.data?.chunk));
      if (!chunkText) continue;
      recordModelText(chunkText);
      chunkText = consumeVisibilitySignal(chunkText);
      if (state.showReasoning) {
        if (!chunkText) continue;
        emitPlan(`${state.reasoning}${chunkText}`, 'llm');
      }
    } else if (event.event === 'on_chat_model_end') {
      const chunk = event?.data?.output;
      let chunkText = normalizeContent(getChunkContent(chunk));
      if (chunkText) {
        recordModelText(chunkText);
        chunkText = consumeVisibilitySignal(chunkText);
        if (state.showReasoning) {
          if (chunkText) {
            emitPlan(`${state.reasoning}${chunkText}`, 'llm');
            seenAnswerChunks.push(chunkText);
          }
        } else {
          pendingReasoning += chunkText;
        }
      }
      if (state.showReasoning === undefined) {
        state.showReasoning = false;
        onEvent({ kind: 'reasoning_visibility', visible: false });
        pendingReasoning = '';
      }
      if (state.showReasoning && pendingReasoning) {
        state.reasoning = truncatePlanText(
          `${state.reasoning}${pendingReasoning}`.trim()
        );
        pendingReasoning = '';
      }
      const usage = extractUsageFromChunk(chunk);
      if (usage) {
        state.usage = usage;
        onEvent({ kind: 'usage', usage });
      }
      const modelName =
        typeof event?.metadata?.ls_model_name === 'string'
          ? (event.metadata.ls_model_name as string)
          : undefined;
      if (modelName) {
        state.model = modelName;
        onEvent({ kind: 'model', model: modelName });
      }
    } else if (event.event === 'on_tool_start') {
      const id = event?.run_id ?? `tool-${Date.now()}`;
      const name = typeof event?.name === 'string' ? event.name : 'tool';
      if (name === 'write_todos') {
        planToolRunIds.add(id);
        continue;
      }
      const detail = describeToolAction(name, event?.data?.input, undefined, 'running');
      const action: MessageAction = {
        id,
        name,
        status: 'running',
        detail,
        meta: { input: event?.data?.input }
      };
      actionsMap.set(id, action);
      state.actions = Array.from(actionsMap.values());
      onEvent({ kind: 'action', action });
    } else if (event.event === 'on_tool_end') {
      const runId = event?.run_id ?? '';
      if (planToolRunIds.has(runId)) {
        planToolRunIds.delete(runId);
        const rawOutput = formatToolDetail(event?.data?.output);
        const formatted = formatPlanText(rawOutput);
        if (formatted) {
          state.reasoning = formatted;
          if (state.showReasoning !== false) {
            onEvent({ kind: 'plan', text: state.reasoning.trim(), source: 'todos' });
          }
        }
        continue;
      }
      const existing = actionsMap.get(runId);
      const inputMeta = existing?.meta?.input ?? event?.data?.input;
      const detail = describeToolAction(
        existing?.name ?? event?.name,
        inputMeta,
        unwrapToolOutput(event?.data?.output),
        'success'
      );
      traceLog('tool_end', {
        name: existing?.name ?? event?.name,
        runId,
        rawOutput: event?.data?.output,
        rawOutputType: typeof event?.data?.output,
        rawOutputKeys:
          event?.data?.output && typeof event?.data?.output === 'object'
            ? Object.keys(event.data.output as Record<string, unknown>)
            : null,
        detail
      });
      const action: MessageAction = {
        id: runId || existing?.id || `tool-${Date.now()}`,
        name: existing?.name ?? (typeof event?.name === 'string' ? event.name : 'tool'),
        status: 'success',
        detail: detail || existing?.detail,
        meta: { input: inputMeta }
      };
      actionsMap.set(action.id, action);
      state.actions = Array.from(actionsMap.values());
      onEvent({ kind: 'action', action });
    } else if (event.event === 'on_tool_error') {
      const runId = event?.run_id ?? '';
      const existing = actionsMap.get(runId);
      const inputMeta = existing?.meta?.input ?? event?.data?.input;
      const detail = describeToolAction(
        existing?.name ?? event?.name,
        inputMeta,
        unwrapToolOutput(event?.data ?? event?.error),
        'error'
      );
      traceLog('tool_error', {
        name: existing?.name ?? event?.name,
        runId,
        rawOutput: event?.data ?? event?.error,
        rawOutputType: typeof (event?.data ?? event?.error),
        detail
      });
      const action: MessageAction = {
        id: runId || existing?.id || `tool-${Date.now()}`,
        name: existing?.name ?? (typeof event?.name === 'string' ? event.name : 'tool'),
        status: 'error',
        detail: detail || existing?.detail,
        meta: { input: inputMeta }
      };
      actionsMap.set(action.id, action);
      state.actions = Array.from(actionsMap.values());
      onEvent({ kind: 'action', action });
    }
  }

  const combinedModelText = modelTextParts.join('');
  const sections = splitReasoningAndAnswer(combinedModelText);
  if (sections.visible !== undefined && state.showReasoning === undefined) {
    state.showReasoning = sections.visible;
    onEvent({ kind: 'reasoning_visibility', visible: sections.visible });
  }
  if (sections.reasoning?.trim()) {
    state.reasoning = truncatePlanText(sections.reasoning.trim());
  }
  const { text: cleanedAnswer } = stripReasoningVisibilityLine(
    sections.answer?.trim() || seenAnswerChunks.join('').trim() || state.answer || ''
  );
  state.answer = cleanedAnswer.trim();
  if (state.answer.startsWith('Plan:') && seenAnswerChunks.length) {
    state.answer = seenAnswerChunks.join('').trim();
  }

  if (!state.answer?.trim()) {
    const digest = formatActionDigest(state.actions);
    state.answer = digest || '';
  }

  state.reasoning = pruneAnswerFromReasoning(state.reasoning, state.answer);
  const normReasoning = NORMALIZE_WS(state.reasoning);
  const normAnswer = NORMALIZE_WS(state.answer);
  const backupAnswer = NORMALIZE_WS(seenAnswerChunks.join(' '));
  if (normAnswer && (normReasoning === normAnswer || normReasoning.includes(normAnswer))) {
    state.reasoning = '';
  } else if (!normAnswer && backupAnswer && (normReasoning === backupAnswer || normReasoning.includes(backupAnswer))) {
    state.reasoning = '';
  }
  if (state.answer && state.reasoning) {
    const trimmed = state.reasoning.trim().toLowerCase();
    if (trimmed.startsWith('plan:') && state.reasoning.length < 120 && !/\n/.test(state.reasoning)) {
      state.reasoning = '';
    }
  }

  state.reasoning = truncatePlanText(state.reasoning.trim());
  onEvent({ kind: 'answer', text: state.answer });
  return state;
};
const TRACE_ACTIONS = process.env.AGEN_TUI_ACTION_TRACE === '1';
const traceLog = (...parts: unknown[]) => {
  if (TRACE_ACTIONS) {
    console.log('[action-trace]', ...parts);
  }
};
