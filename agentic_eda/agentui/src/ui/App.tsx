import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Box, Text, useApp, useStdout, useStdin, useInput } from 'ink';
import Spinner from 'ink-spinner';
import stringWidth from 'string-width';
import fs from 'fs';
import { spawn } from 'child_process';
import path from 'path';
import os from 'os';
import { createAgentRunner, type AgentMessage, type AgentRunner } from '../agent/index.js';
import type { PromptIntent } from '../agent/router.js';
import type { AppConfig } from '../config/index.js';
import { useSessionState, type Message, type SystemSeverity, type MessageAction } from '../state/session.js';
import type { TokenUsage } from '../state/usage.js';
import { getModelContextWindow, getKnownModels } from '../models.js';
import { parseSlashCommand } from '../commands/index.js';
import {
  detectMentionContext,
  formatMentionValue,
  getMentionRanges
} from './mentions.js';
import { formatActionDigest } from '../utils/actions.js';
import {
  renderComposerView,
  sanitizeComposerText,
  type DisplayLine
} from './composer-renderer.js';
import { maybeExecuteFsCommand } from '../fs/shortcuts.js';
import { prepareAgentInput } from '../agent/prompt.js';
import { streamAgentEvents, type AgentStructuredEvent } from '../agent/events.js';
import { formatActionSummary } from '../utils/actions.js';
import { splitReasoningAndAnswer } from '../utils/messages.js';
import { loadImageAttachments } from '../utils/images.js';

const BRAND_COLOR = 'magenta';
const SIDEBAR_MIN_WIDTH = 110;
const PRODUCT_NAME = 'AEDA';
const PRODUCT_VERSION = '0.0.1';
const BUSY_MESSAGE = 'Agent is finishing the previous turn. Please wait…';
const EXPLORER_WIDTH = 32;
const SIDEBAR_WIDTH = 32;
const MAX_TREE_DEPTH = 6;
const EXPLORER_VISIBLE_ROWS = 24;
const MAX_MENTION_SUGGESTIONS = 10;

const stripStructuredNoise = (answer: string) => {
  if (!answer) return '';
  let cleaned = answer.replace(/ReasoningVisible:.*\n?/gi, '');
  cleaned = cleaned.replace(/Plan:\n[\s\S]*?(?=\n\n|Actions:|Answer:|$)/gi, '');
  cleaned = cleaned.replace(/Actions:\n[\s\S]*?(?=\n\n|Answer:|$)/gi, '');
  cleaned = cleaned.replace(/Completed actions.*$/gim, '').trim();
  return cleaned.trim();
};

const roleLabel: Record<Message['speaker'], string> = {
  user: 'You',
  agent: 'Agent',
  system: 'System'
};

const roleAccent: Record<Message['speaker'], string> = {
  user: 'cyan',
  agent: BRAND_COLOR,
  system: 'green'
};

const noticeColor: Record<SystemSeverity, string> = {
  success: 'green',
  info: 'yellow',
  warning: 'yellow',
  error: 'red'
};

const noticeIcon: Record<SystemSeverity, string> = {
  success: '✓',
  info: 'ℹ',
  warning: '⚠',
  error: '!'
};

const SLASH_COMMANDS = [
  { name: 'model', description: 'Switch language models' },
  { name: 'new', description: 'Start a new chat' },
  { name: 'undo', description: 'Undo the last turn' },
  { name: 'files', description: 'Toggle filesystem explorer' },
  { name: 'quit', description: 'Exit AgenTUI' },
  { name: 'exit', description: 'Exit AgenTUI' }
];

type ModelAvailabilityResult =
  | { ok: true; resolvedId: string }
  | { ok: false; reason: string };

type FileNode = {
  path: string;
  name: string;
  type: 'file' | 'dir';
  children?: FileNode[];
};

type MentionOption = {
  value: string;
  type: 'file' | 'dir';
};

export interface AppProps {
  agent: AgentRunner;
  config: AppConfig;
}

export const App: React.FC<AppProps> = ({ agent, config }) => {
  const { exit } = useApp();
  const columns = useTerminalColumns();
  const sidebarVisible = columns >= SIDEBAR_MIN_WIDTH;
  const { isRawModeSupported } = useStdin();
  const [runtimeConfig, setRuntimeConfig] = useState(config);
  const [agentRunner, setAgentRunner] = useState<AgentRunner>(() => agent);
  const [effectiveModel, setEffectiveModel] = useState(config.openAIModel);
  const [modelMenuOpen, setModelMenuOpen] = useState(false);
  const modelOptions = useMemo(() => getKnownModels(), []);
  const workspaceRoot = useMemo(() => process.cwd(), []);
  const contextWindow = useMemo(() => getModelContextWindow(effectiveModel), [effectiveModel]);
  const formattedCwd = useMemo(() => formatWorkingDirectory(workspaceRoot), [workspaceRoot]);
  const availabilityCache = useRef(new Map<string, { resolvedId: string }>());
  const lastToolIntentRef = useRef<PromptIntent | null>(null);
  const notebookTipsShownRef = useRef(false);

  const ensureModelAvailable = useCallback(
    async (modelId: string): Promise<ModelAvailabilityResult> => {
      const cached = availabilityCache.current.get(modelId);
      if (cached) {
        return { ok: true, resolvedId: cached.resolvedId };
      }
      if (!runtimeConfig.openAIApiKey) {
        return { ok: false, reason: 'OpenAI API key is missing.' };
      }
      try {
        const response = await fetch(`https://api.openai.com/v1/models/${modelId}`, {
          headers: {
            Authorization: `Bearer ${runtimeConfig.openAIApiKey}`,
            'Content-Type': 'application/json'
          }
        });
        if (response.ok) {
          const payload = (await response.json().catch(() => undefined)) as { id?: string } | undefined;
          const resolvedId = payload?.id ?? modelId;
          availabilityCache.current.set(modelId, { resolvedId });
          return { ok: true, resolvedId };
        }
        let errorReason = response.statusText || 'Model unavailable.';
        try {
          const errorPayload = (await response.json()) as { error?: { message?: string } };
          errorReason = errorPayload?.error?.message ?? errorReason;
        } catch {
          // Ignore JSON parse failures.
        }
        return { ok: false, reason: errorReason };
      } catch (error) {
        return {
          ok: false,
          reason: error instanceof Error ? error.message : 'Unknown error verifying model.'
        };
      }
    },
    [runtimeConfig.openAIApiKey]
  );

  const [state, dispatch] = useSessionState();
  const isThinking = state.status === 'thinking';

  const { tree: fileTree, refresh: refreshFileTree } = useFilesystemTree(workspaceRoot);
  const [filesVisible, setFilesVisible] = useState(true);
  const [activePane, setActivePane] = useState<'composer' | 'explorer'>('composer');
  const composerFocused = activePane === 'composer' && !modelMenuOpen;
  const sidebarWidth = sidebarVisible ? SIDEBAR_WIDTH : 0;
  const composerWidth = Math.max(20, columns - (filesVisible ? EXPLORER_WIDTH : 0) - sidebarWidth - 6);
  const mentionOptions = useMemo(() => collectMentionOptions(fileTree, workspaceRoot), [fileTree, workspaceRoot]);

  useInput(
    (input, key) => {
      if (key.ctrl && input?.toLowerCase() === 'f') {
        if (!filesVisible) {
          setFilesVisible(true);
          setActivePane('explorer');
        } else {
          setActivePane((prev) => (prev === 'explorer' ? 'composer' : 'explorer'));
        }
      }
    },
    { isActive: true }
  );

  const addSystemMessage = useCallback(
    (content: string, severity: SystemSeverity = 'info') => {
      dispatch({
        type: 'ADD_MESSAGE',
        message: {
          id: `system-${Date.now()}`,
          speaker: 'system',
          content,
          timestamp: new Date().toLocaleTimeString(),
          severity
        }
      });
    },
    [dispatch]
  );

  const applyModel = useCallback(
    async (modelId: string) => {
      if (!modelOptions.includes(modelId)) {
        addSystemMessage(`Unknown model "${modelId}".`, 'error');
        return false;
      }
      const availability = await ensureModelAvailable(modelId);
      if (!availability.ok) {
        addSystemMessage(`Unable to switch to ${modelId}: ${availability.reason}`, 'error');
        return false;
      }
      const nextConfig = { ...runtimeConfig, openAIModel: modelId };
      setRuntimeConfig(nextConfig);
      setAgentRunner(createAgentRunner(nextConfig));
      setEffectiveModel(modelId);
      setModelMenuOpen(false);
      dispatch({ type: 'RESET_USAGE' });
      addSystemMessage(`Switched model to ${availability.resolvedId}.`, 'success');
      return true;
    },
    [addSystemMessage, dispatch, ensureModelAvailable, modelOptions, runtimeConfig]
  );

  const handleSlashCommand = useCallback(
    async (raw: string): Promise<boolean> => {
      if (isThinking) {
        addSystemMessage(BUSY_MESSAGE, 'warning');
        return false;
      }
      const parsed = parseSlashCommand(raw);
      if (!parsed) {
        addSystemMessage(`Unknown command: ${raw}`, 'error');
        return true;
      }
      switch (parsed.type) {
        case 'model':
          if (parsed.value) {
            return applyModel(parsed.value);
          }
          if (isRawModeSupported) {
            setModelMenuOpen(true);
          } else {
            addSystemMessage(`Available models: ${modelOptions.join(', ')}. Use /model <name> to switch.`);
          }
          return true;
        case 'new':
          dispatch({ type: 'RESET_SESSION' });
          lastToolIntentRef.current = null;
          notebookTipsShownRef.current = false;
          addSystemMessage('Started a new chat.', 'success');
          return true;
        case 'undo':
          if (!state.messages.length) {
            addSystemMessage('Nothing to undo.', 'info');
            return true;
          }
          dispatch({ type: 'UNDO_LAST_TURN', contextWindow });
          return true;
        case 'files':
          setFilesVisible((prev) => {
            const next = !prev;
            addSystemMessage(next ? 'Showing files panel.' : 'Hiding files panel.', 'info');
            if (!next && activePane === 'explorer') {
              setActivePane('composer');
            }
            return next;
          });
          return true;
        case 'quit':
        case 'exit':
          exit();
          return true;
        default:
          return false;
      }
    },
    [activePane, addSystemMessage, applyModel, contextWindow, dispatch, exit, isRawModeSupported, isThinking, modelOptions, state.messages.length]
  );

  const [input, setInput] = useState('');
  const [inputCursor, setInputCursor] = useState(0);

  useEffect(() => {
    setInputCursor((prev) => Math.min(prev, input.length));
  }, [input]);
  const [slashSuggestionIndex, setSlashSuggestionIndex] = useState(0);
  const [mentionSuggestionIndex, setMentionSuggestionIndex] = useState(0);

  const trimmedForSuggestions = input.replace(/\s+$/, '');
  const slashCommandMode = trimmedForSuggestions.startsWith('/') && !trimmedForSuggestions.includes(' ');
  const filteredSuggestions = useMemo(() => {
    if (!slashCommandMode) return [];
    const term = trimmedForSuggestions.slice(1).toLowerCase();
    const matches = SLASH_COMMANDS.filter((cmd) => cmd.name.startsWith(term));
    return matches.length > 0 ? matches : SLASH_COMMANDS;
  }, [slashCommandMode, trimmedForSuggestions]);
  const showSuggestions = slashCommandMode && filteredSuggestions.length > 0;
  const renderSuggestions = showSuggestions && trimmedForSuggestions === input && !modelMenuOpen;
  const mentionContext = useMemo(() => detectMentionContext(input, inputCursor), [input, inputCursor]);
  const mentionSuggestionResult = useMemo(() => {
    if (!mentionContext || !mentionContext.query) {
      return { matches: [], overflow: 0 };
    }
    if (!mentionOptions.length) return { matches: [], overflow: 0 };
    const term = mentionContext.query.toLowerCase();
    const filtered = mentionOptions
      .filter((opt) => opt.value.toLowerCase().includes(term))
      .sort((a, b) => {
        const depthA = a.value.split('/').filter(Boolean).length;
        const depthB = b.value.split('/').filter(Boolean).length;
        if (depthA !== depthB) return depthA - depthB;
        return a.value.localeCompare(b.value);
      });
    const matches = filtered.slice(0, MAX_MENTION_SUGGESTIONS);
    const overflow = Math.max(filtered.length - matches.length, 0);
    return { matches, overflow };
  }, [mentionContext, mentionOptions]);
  const mentionSuggestions = mentionSuggestionResult.matches;
  const mentionOverflow = mentionSuggestionResult.overflow;
  const showMentionSuggestions = Boolean(
    mentionContext && mentionContext.query.length > 0 && mentionSuggestions.length > 0 && !modelMenuOpen
  );

  useEffect(() => {
    if (!renderSuggestions) {
      setSlashSuggestionIndex(0);
    } else {
      setSlashSuggestionIndex((prev) => Math.min(prev, filteredSuggestions.length - 1));
    }
  }, [renderSuggestions, filteredSuggestions.length]);

  useEffect(() => {
    if (!showMentionSuggestions) {
      setMentionSuggestionIndex(0);
    } else {
      setMentionSuggestionIndex((prev) => Math.min(prev, mentionSuggestions.length - 1));
    }
  }, [showMentionSuggestions, mentionSuggestions.length]);

  const insertMentionSelection = useCallback(
    (valueToInsert: string) => {
      if (!mentionContext) return;
      const formatted = formatMentionValue(valueToInsert);
      const before = input.slice(0, mentionContext.start);
      const after = input.slice(inputCursor);
      const insertion = `@${formatted} `;
      const nextValue = `${before}${insertion}${after}`;
      const nextCursor = before.length + insertion.length;
      setInput(nextValue);
      setInputCursor(nextCursor);
      setMentionSuggestionIndex(0);
    },
    [input, inputCursor, mentionContext]
  );

  useInput(
    (_input, key) => {
      if (!renderSuggestions || !isRawModeSupported) {
        return;
      }
      if (key.downArrow) {
        setSlashSuggestionIndex((prev) => (prev + 1) % filteredSuggestions.length);
        return;
      }
      if (key.upArrow) {
        setSlashSuggestionIndex((prev) => (prev - 1 + filteredSuggestions.length) % filteredSuggestions.length);
        return;
      }
      if (key.tab) {
        const label = `/${filteredSuggestions[slashSuggestionIndex].name} `;
        setInput(label);
        setInputCursor(label.length);
        setSlashSuggestionIndex(0);
        return;
      }
      if (key.return) {
        const command = `/${filteredSuggestions[slashSuggestionIndex].name}`;
        void (async () => {
          const executed = await handleSlashCommand(command);
          if (executed) {
            setInput('');
            setInputCursor(0);
          }
        })();
        setSlashSuggestionIndex(0);
        return;
      }
      if (key.escape) {
        setSlashSuggestionIndex(0);
      }
    },
    { isActive: isRawModeSupported && renderSuggestions }
  );

  useInput(
    (_input, key) => {
      if (!showMentionSuggestions || !isRawModeSupported) {
        return;
      }
      if (key.downArrow) {
        setMentionSuggestionIndex((prev) => (prev + 1) % mentionSuggestions.length);
        return;
      }
      if (key.upArrow) {
        setMentionSuggestionIndex((prev) => (prev - 1 + mentionSuggestions.length) % mentionSuggestions.length);
        return;
      }
      if (key.tab || key.return) {
        const option = mentionSuggestions[mentionSuggestionIndex];
        if (option) {
          insertMentionSelection(option.value);
        }
        return;
      }
      if (key.escape) {
        setMentionSuggestionIndex(0);
      }
    },
    { isActive: isRawModeSupported && showMentionSuggestions }
  );

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed) {
      return;
    }
    if (isThinking) {
      addSystemMessage(BUSY_MESSAGE, 'warning');
      return;
    }
    if (trimmed.startsWith('/')) {
      const executed = await handleSlashCommand(trimmed);
      if (executed) {
        setInput('');
        setInputCursor(0);
      }
      return;
    }
    if (modelMenuOpen) {
      return;
    }
    const timestamp = new Date().toLocaleTimeString();
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      speaker: 'user',
      content: trimmed,
      timestamp
    };

    const shortcutResult = await maybeExecuteFsCommand(trimmed, workspaceRoot);
    if (shortcutResult) {
      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        speaker: 'agent',
        content: shortcutResult,
        status: 'complete',
        timestamp: new Date().toLocaleTimeString()
      };
      setInput('');
      setInputCursor(0);
      dispatch({ type: 'ADD_MESSAGE', message: userMessage });
      dispatch({ type: 'ADD_MESSAGE', message: agentMessage });
      return;
    }

    const prepared = prepareAgentInput(trimmed, workspaceRoot, {
      lastIntent: lastToolIntentRef.current,
      notebookTipsShown: notebookTipsShownRef.current
    });
    const imageAttachments = await loadImageAttachments(workspaceRoot, prepared.mentionedFiles);
    const agentMessage: Message = {
      id: `agent-${Date.now()}`,
      speaker: 'agent',
      content: '',
      status: 'pending',
      timestamp
    };

    setInput('');
    setInputCursor(0);
    dispatch({ type: 'ADD_MESSAGE', message: { ...userMessage, images: imageAttachments } });
    dispatch({ type: 'ADD_MESSAGE', message: agentMessage });
    dispatch({ type: 'SET_STATUS', status: 'thinking' });

    const convo: Message[] = [...state.messages, { ...userMessage, images: imageAttachments }];
    if (prepared.decision.intent === 'conversation') {
      lastToolIntentRef.current = null;
    } else {
      lastToolIntentRef.current = prepared.decision.intent;
    }
    if (prepared.includedNotebookTips) {
      notebookTipsShownRef.current = true;
    }
    const transcript: AgentMessage[] = convo
      .filter((msg) => msg.speaker !== 'system')
      .map((msg) => ({
        role: msg.speaker === 'agent' ? 'assistant' : msg.speaker,
        content: msg.id === userMessage.id ? prepared.content : msg.content,
        images: msg.id === userMessage.id ? imageAttachments : msg.images
      }));

    let reasoningBuffer = '';
    let finalText = '';
    let latestUsage: TokenUsage | null = null;
    let actualModel: string | undefined;
    let actions: MessageAction[] = [];
    let reasoningVisible: boolean | undefined = undefined;

    const patchMessage = (patch: Partial<Message>) => {
      dispatch({ type: 'UPDATE_MESSAGE', id: agentMessage.id, patch });
    };

    const upsertAction = (next: MessageAction) => {
      const index = actions.findIndex((action) => action.id === next.id);
      if (index === -1) {
        actions = [...actions, next];
      } else {
        const clone = [...actions];
        clone[index] = next;
        actions = clone;
      }
      patchMessage({ actions });
    };

    const handleEvent = (event: AgentStructuredEvent) => {
      if (event.kind === 'plan') {
        reasoningBuffer = event.text;
        patchMessage({
          reasoning: reasoningBuffer,
          showReasoning: reasoningVisible ?? undefined
        });
      } else if (event.kind === 'action') {
        upsertAction(event.action);
      } else if (event.kind === 'usage') {
        latestUsage = event.usage;
      } else if (event.kind === 'model') {
        actualModel = event.model;
      } else if (event.kind === 'answer') {
        finalText = event.text;
      } else if (event.kind === 'reasoning_visibility') {
        reasoningVisible = event.visible;
        patchMessage({ showReasoning: reasoningVisible });
      }
    };

    try {
      const result = await streamAgentEvents(agentRunner, transcript, handleEvent);
      const reasoning = result.reasoning || reasoningBuffer;
      const answerText = result.answer || finalText || '';
      const sections = splitReasoningAndAnswer(answerText);
      if (sections.visible !== undefined) {
        reasoningVisible = sections.visible;
      }
      const reasoningSection = (sections.reasoning || reasoning || '').trim();
      const resolvedActions = result.actions ?? actions;
      const actionDigest = formatActionDigest(resolvedActions);
      const actionLines = resolvedActions
        .filter((a) => a.status === 'success')
        .map((a) => a.detail?.trim())
        .filter(Boolean) as string[];
      const hasActions = resolvedActions.length > 0;

      let modelAnswer = sections.answer?.trim() || answerText?.trim();
      const lastUserMessage = transcript.slice().reverse().find((m) => m.role === 'user')?.content ?? '';
      const isGenericAllSet = modelAnswer && /all set\.\s*let me know/i.test(modelAnswer);
      const isGreeting = /\b(hi|hello|hey|thanks|thank you|how are you)\b/i.test(lastUserMessage);
      const contaminated = modelAnswer && /ReasoningVisible|Plan:|Actions:/i.test(modelAnswer);
      const looksLikeDigest = modelAnswer && /completed actions/i.test(modelAnswer);
      if (contaminated) {
        modelAnswer = '';
      }

      if (!modelAnswer || looksLikeDigest) {
        try {
          const summary = await agentRunner.summarize(transcript, {
            actions: actionDigest,
            fallbackReasoning: reasoningSection,
            lastUser: lastUserMessage
          });
          modelAnswer = summary.text?.trim() || '';
        } catch {
          modelAnswer = '';
        }
      }

      if (!hasActions && (!modelAnswer || isGenericAllSet)) {
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

      let combinedAnswer = modelAnswer?.trim() || '';
      if (!combinedAnswer) {
        if (hasActions && actionLines.length) {
          combinedAnswer = `Here’s what I found:\n- ${actionLines.join('\n- ')}`;
        } else if (hasActions && actionDigest) {
          combinedAnswer = actionDigest;
        } else {
          combinedAnswer = modelAnswer || (lastUserMessage ? `Got it: ${lastUserMessage}` : 'I’m here whenever you’re ready.');
        }
      }
      combinedAnswer = stripStructuredNoise(combinedAnswer);

      const showReasoningFlag =
        (reasoningVisible ?? result.showReasoning ?? sections.visible ?? false) &&
        Boolean(reasoningSection && reasoningSection.trim().length > 0);
      reasoningVisible = showReasoningFlag;
      patchMessage({
        content: combinedAnswer,
        reasoning: reasoningSection,
        answer: combinedAnswer,
        actions: resolvedActions,
        showReasoning: showReasoningFlag,
        status: 'complete',
        timestamp: new Date().toLocaleTimeString()
      });
      if (result.model || actualModel) {
        setEffectiveModel(result.model ?? actualModel ?? effectiveModel);
      }
      const usageToRecord = result.usage ?? latestUsage;
      if (usageToRecord) {
        dispatch({ type: 'UPDATE_USAGE', delta: usageToRecord, contextWindow });
      }
      dispatch({ type: 'SET_STATUS', status: 'idle' });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      patchMessage({
        reasoning: reasoningBuffer,
        answer: `! ${message}`,
        actions,
        status: 'error',
        content: `! ${message}`,
        timestamp: new Date().toLocaleTimeString()
      });
      dispatch({ type: 'SET_STATUS', status: 'error', error: message });
      addSystemMessage(message, 'error');
    }
  }, [
    addSystemMessage,
    agentRunner,
    contextWindow,
    dispatch,
    effectiveModel,
    handleSlashCommand,
    input,
    isThinking,
    modelMenuOpen,
    runtimeConfig.openAIModel,
    state.messages,
    workspaceRoot
  ]);

  const stats = useMemo(() => {
    const userTurns = state.messages.filter((msg) => msg.speaker === 'user').length;
    return {
      turns: userTurns,
      status: state.status,
      lastMessageAt: state.messages[state.messages.length - 1]?.timestamp ?? '—'
    };
  }, [state.messages, state.status]);

      return (
    <Box flexDirection="column" height="100%" paddingX={1} paddingY={1}>
      <Box flexGrow={1} flexDirection="row" marginBottom={1}>
        {filesVisible && (
          <Box flexDirection="column" justifyContent="flex-end" width={EXPLORER_WIDTH} flexShrink={0}>
            <FileExplorer
              root={fileTree}
              active={activePane === 'explorer'}
              onExit={() => setActivePane('composer')}
              onRefresh={refreshFileTree}
              onOpenFile={openFileWithDefaultApp}
              onOpenFolder={openDirectory}
            />
          </Box>
        )}
        <Box flexDirection="column" flexGrow={1} marginX={1}>
          <Box alignSelf="center" marginBottom={1}>
            <StartupSplash model={effectiveModel} directory={formattedCwd} />
          </Box>
          <Box flexGrow={1}>
            <Transcript messages={state.messages} />
          </Box>
        </Box>
        {sidebarVisible && (
          <Box flexDirection="column" justifyContent="flex-end" width={SIDEBAR_WIDTH} flexShrink={0}>
            <Sidebar model={effectiveModel} systemPrompt={runtimeConfig.systemPrompt} stats={stats} />
          </Box>
        )}
      </Box>
      {modelMenuOpen && isRawModeSupported && (
        <ModelMenu
          options={modelOptions}
          currentModel={effectiveModel}
          onConfirm={(value) => {
            void applyModel(value);
          }}
          onCancel={() => setModelMenuOpen(false)}
        />
      )}
      <Footer
        input={input}
        cursor={inputCursor}
        onChange={setInput}
        onCursorChange={setInputCursor}
        onSubmit={sendMessage}
        disabled={modelMenuOpen}
        focusComposer={composerFocused}
        submitDisabled={renderSuggestions || showMentionSuggestions}
        contextPercent={state.contextPercent}
        suggestions={filteredSuggestions}
        suggestionIndex={slashSuggestionIndex}
        showSuggestions={renderSuggestions}
        suggestionsInteractive={isRawModeSupported && activePane === 'composer'}
        mentionSuggestions={mentionSuggestions}
        mentionSuggestionIndex={mentionSuggestionIndex}
        showMentionSuggestions={showMentionSuggestions}
        mentionSuggestionsInteractive={isRawModeSupported && activePane === 'composer'}
        mentionOverflow={mentionOverflow}
        composerWidth={composerWidth}
      />
    </Box>
  );
};

const useTerminalColumns = () => {
  const { stdout } = useStdout();
  const [columns, setColumns] = useState(stdout?.columns ?? 80);

  useEffect(() => {
    if (!stdout) return;
    const handleResize = () => setColumns(stdout.columns);
    stdout.on('resize', handleResize);
    return () => {
      stdout.off('resize', handleResize);
    };
  }, [stdout]);

  return columns;
};

const Transcript: React.FC<{ messages: Message[] }> = ({ messages }) => {
  if (messages.length === 0) {
    return (
      <Box flexDirection="column" paddingX={1} paddingY={1}>
        <Text dimColor>
          Welcome! Ask a question!
        </Text>
      </Box>
    );
  }
  return (
    <Box flexDirection="column">
      {messages.map((message, index) => {
        if (message.hidden) return null;
        return (
          <Box key={message.id} marginBottom={index === messages.length - 1 ? 0 : 1}>
            <MessageCard message={message} />
          </Box>
        );
      })}
    </Box>
  );
};

const MessageCard: React.FC<{ message: Message }> = ({ message }) => {
  if (message.speaker === 'system') {
    const severity = message.severity ?? 'info';
    return (
      <Text color={noticeColor[severity]}>
        {noticeIcon[severity]} {message.content}
      </Text>
    );
  }

  const accent = roleAccent[message.speaker];
  const rows: React.ReactNode[] = [
    <Text wrap="wrap">
      <Text color={accent} bold>
        {roleLabel[message.speaker]}
      </Text>
      <Text dimColor>{message.timestamp ? ` · ${message.timestamp}` : ''}</Text>
      {message.status === 'pending' && (
        <Text color="cyan"> · <Spinner type="dots" /></Text>
      )}
      {message.status === 'error' && <Text color="red"> · error</Text>}
    </Text>
  ];

  const hasStructured =
    Boolean(message.reasoning && message.reasoning.trim().length > 0) ||
    Boolean(message.actions && message.actions.length > 0) ||
    Boolean(message.answer && message.answer.trim().length > 0);

  if (!hasStructured) {
    message.content.split('\n').forEach((line) => {
      rows.push(<Text wrap="wrap">{renderLineWithPaths(line)}</Text>);
    });
    return <Bubble rows={rows} accent={accent} />;
  }

  const reasoning = message.reasoning?.trim();
  const answer = message.answer?.trim();
  const actions = message.actions ?? [];

  const shouldShowReasoning = message.showReasoning !== false && reasoning && message.status !== 'pending';
  const showPlaceholder = message.status === 'pending' && message.showReasoning !== false;
  const activitySummary = useMemo(() => {
    const running = actions.find((a) => a.status === 'running');
    if (running?.detail) return running.detail;
    if (running?.name) return running.name.replace(/_/g, ' ');
    return 'Working…';
  }, [actions]);

  if (shouldShowReasoning) {
    const reasoningLines =
      renderMultilineText(reasoning, { color: '#949494', dim: false, italic: true }) ?? [];
    rows.push(...reasoningLines);
  }
  if (!shouldShowReasoning && showPlaceholder) {
    rows.push(<ShimmerLine label={activitySummary} />);
  }
  if (actions.length > 0) {
    rows.push(<Text dimColor>Actions Taken</Text>);
    actions.slice(-8).forEach((action) => {
      rows.push(
        <Text
          key={action.id}
          wrap="wrap"
          color={
            action.status === 'success' ? 'green' : action.status === 'error' ? 'red' : 'yellow'
          }
        >
          {formatActionSummary(action)}
        </Text>
      );
    });
    if (actions.length > 8) {
      rows.push(<Text dimColor>… {actions.length - 8} earlier action(s)</Text>);
    }
  }
  if (answer) {
    if (rows.length > 1) {
      rows.push(<Text> </Text>);
    }
    const answerLines = renderMultilineText(answer) ?? [];
    rows.push(...answerLines);
  }

  return <Bubble rows={rows} accent={accent} />;
};

const Bubble = ({ rows, accent }: { rows: React.ReactNode[]; accent: string }) => (
  <Box flexDirection="column">
    {rows.map((row, idx) => {
      const isFirst = idx === 0;
      const isLast = idx === rows.length - 1;
      const glyph = isFirst ? '┌' : isLast ? '└' : '│';
      return (
        <Box key={idx} flexDirection="row">
          <Text color={accent}>{glyph} </Text>
          <Box flexDirection="column" flexGrow={1}>
            {row}
          </Box>
        </Box>
      );
    })}
  </Box>
);

const shimmerFrames = ['   ', '.  ', '.. ', '...', ' ..', '  .'];
const ShimmerLine: React.FC<{ label: string }> = ({ label }) => {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    const id = setInterval(() => {
      setIndex((prev) => (prev + 1) % shimmerFrames.length);
    }, 140);
    return () => clearInterval(id);
  }, []);
  const dots = shimmerFrames[index];
  return (
    <Text dimColor>
      • {label || 'Working'} {dots}
    </Text>
  );
};

const PATH_FILE_EXTENSIONS = [
  'md',
  'markdown',
  'mdx',
  'txt',
  'log',
  'json',
  'ts',
  'tsx',
  'js',
  'jsx',
  'py',
  'rb',
  'go',
  'rs',
  'java',
  'c',
  'cpp',
  'h',
  'css',
  'scss',
  'yaml',
  'yml',
  'toml',
  'ini',
  'cfg',
  'ipynb',
  'csv',
  'sh'
];
const FILE_REGEX = new RegExp(`\\b[\\w@./-]+\\.(${PATH_FILE_EXTENSIONS.join('|')})\\b`, 'gi');
const ABS_PATH_REGEX = /(?:@|~|\.{1,2}|\/)[\w@.-]*(?:\/[\w@.-]+)+/g;
const MENTION_PATH_REGEX = /@(?:"[^"\n]+"|[A-Za-z0-9@._/-]+)/g;

type PathMatch = { start: number; end: number };

const collectMatches = (line: string): PathMatch[] => {
  const matches: PathMatch[] = [];
  const run = (regex: RegExp, filter?: (match: PathMatch) => boolean) => {
    regex.lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = regex.exec(line)) !== null) {
      const next: PathMatch = { start: match.index, end: match.index + match[0].length };
      if (filter && !filter(next)) continue;
      matches.push(next);
    }
  };
  run(MENTION_PATH_REGEX);
  run(ABS_PATH_REGEX, (match) => {
    if (match.start === 0) return true;
    const prev = line[match.start - 1];
    const nextTwo = line.slice(match.start, match.start + 2);
    if (prev === ':' && nextTwo === '//') {
      return false;
    }
    return true;
  });
  run(FILE_REGEX);

  matches.sort((a, b) => (b.end - b.start) - (a.end - a.start));
  const taken = new Array(line.length).fill(false);
  const selected: PathMatch[] = [];
  matches.forEach((match) => {
    let overlaps = false;
    for (let i = match.start; i < match.end; i++) {
      if (taken[i]) {
        overlaps = true;
        break;
      }
    }
    if (overlaps) return;
    for (let i = match.start; i < match.end; i++) {
      taken[i] = true;
    }
    selected.push(match);
  });
  return selected.sort((a, b) => a.start - b.start);
};

const renderLineWithPaths = (line: string) => {
  const matches = collectMatches(line);
  if (!matches.length) {
    return line;
  }
  const segments: React.ReactNode[] = [];
  let lastIndex = 0;
  matches.forEach((match, index) => {
    if (match.start > lastIndex) {
      segments.push(line.slice(lastIndex, match.start));
    }
    segments.push(
      <Text key={`${match.start}-${index}`} color="cyan">
        {line.slice(match.start, match.end)}
      </Text>
    );
    lastIndex = match.end;
  });
  if (lastIndex < line.length) {
    segments.push(line.slice(lastIndex));
  }
  return segments.length ? segments : line;
};

const renderMultilineText = (
  text: string,
  options: { color?: string; dim?: boolean; italic?: boolean } = {}
) => {
  if (!text) return null;
  const { color, dim, italic } = options;
  const dimColor = dim ?? false;
  return text.split('\n').map((line, idx) => (
    <Text key={idx} wrap="wrap" color={color} dimColor={dimColor} italic={italic}>
      {renderLineWithPaths(line)}
    </Text>
  ));
};

const Sidebar: React.FC<{
  model: string;
  systemPrompt: string;
  stats: { turns: number; status: string; lastMessageAt: string };
}> = ({ model, systemPrompt, stats }) => (
  <Box
    width={SIDEBAR_WIDTH}
    borderStyle="single"
    borderColor="gray"
    flexDirection="column"
    paddingX={1}
    paddingY={1}
  >
    <SidebarSection title="Session">
      <Text dimColor>Model</Text>
      <Text>{model}</Text>
      <Text dimColor>Turns</Text>
      <Text>{stats.turns}</Text>
      <Text dimColor>Last Msg</Text>
      <Text>{stats.lastMessageAt}</Text>
    </SidebarSection>
    <SidebarSection title="Status">
      <Text color={stats.status === 'thinking' ? 'cyan' : 'green'}>
        {stats.status === 'thinking' ? 'Working' : 'Idle'}
      </Text>
    </SidebarSection>
    <SidebarSection title="System Prompt">
      <Text wrap="truncate-end">{systemPrompt}</Text>
    </SidebarSection>
  </Box>
);

const SidebarSection: React.FC<{ title: string; children: React.ReactNode }> = ({
  title,
  children
}) => (
  <Box flexDirection="column" marginBottom={1}>
    <Text color={BRAND_COLOR} bold>
      {title}
    </Text>
    <Box flexDirection="column">{children}</Box>
  </Box>
);

interface FooterProps {
  input: string;
  cursor: number;
  onChange: (value: string) => void;
  onCursorChange: (value: number) => void;
  onSubmit: () => void;
  disabled: boolean;
  focusComposer: boolean;
  submitDisabled: boolean;
  contextPercent: number | null;
  suggestions: typeof SLASH_COMMANDS;
  suggestionIndex: number;
  showSuggestions: boolean;
  suggestionsInteractive: boolean;
  mentionSuggestions: MentionOption[];
  mentionSuggestionIndex: number;
  showMentionSuggestions: boolean;
  mentionSuggestionsInteractive: boolean;
  mentionOverflow: number;
  composerWidth: number;
}

type ComposerInputProps = {
  value: string;
  cursor: number;
  onChange: (value: string) => void;
  onCursorChange: (cursor: number) => void;
  onSubmit: () => void;
  focus: boolean;
  disabled: boolean;
  submitDisabled: boolean;
  placeholder?: string;
  width: number;
  highlightMentions?: boolean;
};

const Footer: React.FC<FooterProps> = ({
  input,
  cursor,
  onChange,
  onCursorChange,
  onSubmit,
  disabled,
  focusComposer,
  submitDisabled,
  contextPercent,
  suggestions,
  suggestionIndex,
  showSuggestions,
  suggestionsInteractive,
  mentionSuggestions,
  mentionSuggestionIndex,
  showMentionSuggestions,
  mentionSuggestionsInteractive,
  mentionOverflow,
  composerWidth
}) => (
  <Box flexDirection="column">
    <Box flexDirection="column" borderStyle="single" borderColor="gray" padding={1}>
      <Box>
        <Text color="cyan">❯ </Text>
        <ComposerInput
          value={input}
          cursor={cursor}
          onChange={onChange}
          onCursorChange={onCursorChange}
          onSubmit={onSubmit}
          focus={!disabled && focusComposer}
          disabled={disabled}
          submitDisabled={submitDisabled}
          placeholder="Ask a question"
          width={Math.max(4, composerWidth)}
          highlightMentions
        />
      </Box>
      <Box justifyContent="space-between" marginTop={1}>
        <ContextMeter percent={contextPercent} />
        <Box>
          <KeyHint combo="↵" label="Send" />
          <Text> </Text>
          <KeyHint combo="⌃C" label="Exit" />
          <Text> </Text>
          <KeyHint combo="⌃J" label="Newline" />
        </Box>
      </Box>
    </Box>
    {showSuggestions && (
      <CommandSuggestions
        suggestions={suggestions}
        selectedIndex={suggestionIndex}
        interactive={suggestionsInteractive}
      />
    )}
    {showMentionSuggestions && (
      <MentionSuggestions
        suggestions={mentionSuggestions}
        selectedIndex={mentionSuggestionIndex}
        interactive={mentionSuggestionsInteractive}
        overflow={mentionOverflow}
      />
    )}
  </Box>
);

const KeyHint: React.FC<{ combo: string; label: string }> = ({ combo, label }) => (
  <Text dimColor>
    [<Text bold>{combo}</Text>] {label}
  </Text>
);


const CommandSuggestions: React.FC<{ suggestions: typeof SLASH_COMMANDS; selectedIndex: number; interactive: boolean }> = ({ suggestions, selectedIndex, interactive }) => (
  <Box flexDirection="column" marginTop={0}>
    {suggestions.map((cmd, idx) => (
      <Text key={cmd.name} color={interactive && idx === selectedIndex ? 'cyan' : undefined}>
        {interactive ? (idx === selectedIndex ? '❯ ' : '  ') : '- '}
        /{cmd.name} – {cmd.description}
      </Text>
    ))}
  </Box>
);

const MentionSuggestions: React.FC<{
  suggestions: MentionOption[];
  selectedIndex: number;
  interactive: boolean;
  overflow: number;
}> = ({ suggestions, selectedIndex, interactive, overflow }) => (
  <Box flexDirection="column" marginTop={0}>
    {suggestions.map((option, idx) => (
      <Text key={`${option.value}-${idx}`} color={interactive && idx === selectedIndex ? 'cyan' : undefined}>
        {interactive ? (idx === selectedIndex ? '❯ ' : '  ') : '- '}
        {option.value}
        <Text dimColor> {option.type}</Text>
      </Text>
    ))}
    {overflow > 0 && (
      <Text dimColor>… {overflow} more</Text>
    )}
  </Box>
);

const ContextMeter: React.FC<{ percent: number | null }> = ({ percent }) => {
  if (percent === null || Number.isNaN(percent)) {
    return <Text dimColor> </Text>;
  }
  const meterText = `${percent}% context left`;
  if (percent <= 10) {
    return <Text color="red">{meterText}</Text>;
  }
  return <Text dimColor>{meterText}</Text>;
};

const StartupSplash: React.FC<{ model: string; directory: string }> = ({ model, directory }) => {
  const labelWidth = 11;
  const formatLabel = (label: string) => `${label}:`.padEnd(labelWidth, ' ');
  return (
    <Box borderStyle="round" borderColor="gray" paddingX={2} paddingY={1} marginBottom={1} flexDirection="column">
      <Text>
        <Text color={BRAND_COLOR}>{`>_ ${PRODUCT_NAME}`}</Text>
        <Text dimColor>{` (${PRODUCT_VERSION})`}</Text>
      </Text>
      <Box>
        <Text dimColor>{formatLabel('model')}</Text>
        <Text>{model}</Text>
        <Text>   </Text>
        <Text color="cyan">/model to change</Text>
      </Box>
      <Box>
        <Text dimColor>{formatLabel('directory')}</Text>
        <Text>{directory}</Text>
      </Box>
    </Box>
  );
};

const FileExplorer: React.FC<{
  root: FileNode | null;
  active: boolean;
  onExit: () => void;
  onRefresh: () => void;
  onOpenFile: (filePath: string) => void;
  onOpenFolder: (dir: string) => void;
}> = ({ root, active, onExit, onRefresh, onOpenFile, onOpenFolder }) => {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [selection, setSelection] = useState(0);

  useEffect(() => {
    if (root) {
      setExpanded((prev) => {
        const next = new Set(prev);
        next.add(root.path);
        return next;
      });
    }
  }, [root?.path]);

  const flatEntries = useMemo(() => {
    if (!root) return [];
    return flattenTree(root, expanded);
  }, [root, expanded]);

  const visibleWindow = useMemo(() => {
    if (flatEntries.length <= EXPLORER_VISIBLE_ROWS) {
      return { entries: flatEntries, offset: 0 };
    }
    const half = Math.floor(EXPLORER_VISIBLE_ROWS / 2);
    let start = active ? Math.max(0, selection - half) : 0;
    if (start + EXPLORER_VISIBLE_ROWS > flatEntries.length) {
      start = flatEntries.length - EXPLORER_VISIBLE_ROWS;
    }
    return { entries: flatEntries.slice(start, start + EXPLORER_VISIBLE_ROWS), offset: start };
  }, [flatEntries, selection, active]);

  useEffect(() => {
    setSelection((prev) => {
      if (flatEntries.length === 0) {
        return 0;
      }
      if (prev >= flatEntries.length) {
        return flatEntries.length - 1;
      }
      return prev;
    });
  }, [flatEntries.length]);

  const togglePath = useCallback((target: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(target)) {
        next.delete(target);
      } else {
        next.add(target);
      }
      return next;
    });
  }, []);

  useInput(
    (input, key) => {
      if (!active) return;
      if (key.shift && key.return) {
        const entry = flatEntries[selection];
        if (entry?.node.type === 'dir') {
          onOpenFolder(entry.node.path);
        }
        return;
      }
      if (key.downArrow) {
        setSelection((prev) => {
          if (flatEntries.length === 0) return 0;
          return prev >= flatEntries.length - 1 ? 0 : prev + 1;
        });
      } else if (key.upArrow) {
        setSelection((prev) => {
          if (flatEntries.length === 0) return 0;
          return prev <= 0 ? flatEntries.length - 1 : prev - 1;
        });
      } else if (key.return) {
        const entry = flatEntries[selection];
        if (!entry) return;
        if (entry.node.type === 'dir') {
          togglePath(entry.node.path);
        } else {
          onOpenFile(entry.node.path);
        }
      } else if (key.escape) {
        onExit();
      } else if (input?.toLowerCase() === 'r') {
        onRefresh();
      }
    },
    { isActive: active }
  );

  const renderEntry = (entry: { node: FileNode; depth: number }, idx: number) => {
    const isSelected = active && idx === selection;
    const indent = ' '.repeat(entry.depth * 2);
    const isDir = entry.node.type === 'dir';
    const isExpanded = expanded.has(entry.node.path);
    const glyph = isDir ? (isExpanded ? '▾' : '▸') : ' ';
    return (
      <Box key={entry.node.path} paddingX={1}>
        <Text
          backgroundColor={isSelected ? BRAND_COLOR : undefined}
          color={isSelected ? 'black' : undefined}
        >
          {indent}{glyph} {entry.node.name}
        </Text>
      </Box>
    );
  };

  return (
    <Box
      width={EXPLORER_WIDTH}
      borderStyle="round"
      borderColor="gray"
      flexDirection="column"
      paddingX={1}
      paddingY={1}
    >
      <Text color={BRAND_COLOR} bold>Files</Text>
      <Box flexDirection="column" flexGrow={1} marginTop={1}>
        {root ? visibleWindow.entries.map((entry, idx) => renderEntry(entry, idx + visibleWindow.offset)) : <Text dimColor>Loading…</Text>}
      </Box>
      <Text dimColor>Ctrl+F focus · /files hide</Text>
    </Box>
  );
};

const ModelMenu: React.FC<{ options: string[]; currentModel: string; onConfirm: (value: string) => void; onCancel: () => void }> = ({ options, currentModel, onConfirm, onCancel }) => {
  const initialIndex = Math.max(0, options.indexOf(currentModel));
  const [index, setIndex] = useState(initialIndex);
  const { isRawModeSupported } = useStdin();

  useEffect(() => {
    setIndex(Math.max(0, options.indexOf(currentModel)));
  }, [currentModel, options]);

  useInput(
    (input, key) => {
      if (!isRawModeSupported) {
        return;
      }
      if (key.downArrow) {
        setIndex((prev) => (prev + 1) % options.length);
      } else if (key.upArrow) {
        setIndex((prev) => (prev - 1 + options.length) % options.length);
      } else if (key.return) {
        onConfirm(options[index]);
      } else if (key.escape) {
        onCancel();
      }
    },
    { isActive: isRawModeSupported }
  );

  if (!isRawModeSupported) {
    return null;
  }

  return (
    <Box borderStyle="single" borderColor="cyan" flexDirection="column" padding={1} marginBottom={1}>
      <Text color="cyan" bold>
        Select a model
      </Text>
      {options.map((option, idx) => (
        <Text key={option} color={idx === index ? 'cyan' : undefined}>
          {idx === index ? '❯ ' : '  '}
          {option}
        </Text>
      ))}
      <Text dimColor>Enter to confirm · Esc to cancel</Text>
    </Box>
  );
};

const formatWorkingDirectory = (dir: string) => {
  const home = os.homedir();
  if (dir.startsWith(home)) {
    return dir.replace(home, '~');
  }
  return dir;
};

const buildFileTree = (dir: string, depth = 0): FileNode => {
  const name = depth === 0 ? formatWorkingDirectory(dir) : path.basename(dir) || dir;
  const node: FileNode = { path: dir, name, type: 'dir' };
  if (depth >= MAX_TREE_DEPTH) {
    return node;
  }
  let entries: FileNode['children'] = [];
  try {
    const dirents = fs.readdirSync(dir, { withFileTypes: true });
    const sorted = dirents.sort((a, b) => {
      if (a.isDirectory() && !b.isDirectory()) return -1;
      if (!a.isDirectory() && b.isDirectory()) return 1;
      return a.name.localeCompare(b.name);
    });
    entries = sorted.map((entry) => {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        return buildFileTree(full, depth + 1);
      }
      return { path: full, name: entry.name, type: 'file' } as FileNode;
    });
  } catch {
    entries = [];
  }
  node.children = entries;
  return node;
};

const useFilesystemTree = (root: string) => {
  const [tree, setTree] = useState<FileNode | null>(null);
  const refresh = useCallback(() => {
    try {
      setTree(buildFileTree(root));
    } catch {
      setTree(null);
    }
  }, [root]);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 2000);
    return () => clearInterval(interval);
  }, [refresh]);
  return { tree, refresh };
};

const openFileWithDefaultApp = (filePath: string) => {
  const platform = process.platform;
  let child;
  if (platform === 'darwin') {
    child = spawn('open', [filePath], { stdio: 'ignore', detached: true });
  } else if (platform === 'win32') {
    child = spawn('cmd', ['/c', 'start', '', filePath], { stdio: 'ignore', detached: true });
  } else {
    child = spawn('xdg-open', [filePath], { stdio: 'ignore', detached: true });
  }
  child.unref();
};

const flattenTree = (node: FileNode, expanded: Set<string>, depth = 0): Array<{ node: FileNode; depth: number }> => {
  const result: Array<{ node: FileNode; depth: number }> = [{ node, depth }];
  if (node.type === 'dir' && expanded.has(node.path)) {
    node.children?.forEach((child) => {
      result.push(...flattenTree(child, expanded, depth + 1));
    });
  }
  return result;
};

const collectMentionOptions = (node: FileNode | null, root: string): MentionOption[] => {
  if (!node) return [];
  const entries: MentionOption[] = [];
  const visit = (current: FileNode) => {
    if (current.path !== root) {
      const rel = path.relative(root, current.path) || path.basename(current.path);
      if (rel) {
        const display = current.type === 'dir' ? `${rel}/` : rel;
        entries.push({ value: display, type: current.type });
      }
    }
    if (current.children) {
      current.children.forEach(visit);
    }
  };
  visit(node);
  return entries.sort((a, b) => a.value.localeCompare(b.value));
};


function ComposerInput({
  value,
  cursor,
  onChange,
  onCursorChange,
  onSubmit,
  focus,
  disabled,
  submitDisabled,
  placeholder,
  width,
  highlightMentions = false
}: ComposerInputProps) {
  const isActive = focus && !disabled;

  const safeValue = useMemo(() => sanitizeComposerText(value), [value]);
  const safeCursorProp = Math.min(Math.max(cursor, 0), safeValue.length);

  const valueRef = useRef(safeValue);
  const cursorRef = useRef(safeCursorProp);
  const effectiveCursorProp = isActive ? cursorRef.current ?? safeCursorProp : safeCursorProp;
  const renderCursor = useMemo(
    () => Math.min(Math.max(effectiveCursorProp ?? 0, 0), safeValue.length),
    [effectiveCursorProp, safeValue.length]
  );

  useEffect(() => {
    if (safeValue !== value) {
      onChange(safeValue);
    }
  }, [safeValue, value, onChange]);

  useEffect(() => {
    valueRef.current = safeValue;
  }, [safeValue]);
  useEffect(() => {
    if (!isActive) {
      cursorRef.current = safeCursorProp;
    }
  }, [isActive, safeCursorProp]);

  const getLiveValue = useCallback(() => valueRef.current, []);
  const getLiveCursor = useCallback(() => {
    const liveValue = valueRef.current;
    const liveCursor = cursorRef.current ?? cursor;
    return Math.min(Math.max(liveCursor, 0), liveValue.length);
  }, [cursor]);

  const stickyColumnRef = useRef<number | null>(null);
  useEffect(() => {
    stickyColumnRef.current = null;
  }, [width]);

  const composerView = useMemo(
    () => renderComposerView(safeValue, renderCursor, width),
    [safeValue, renderCursor, width]
  );
  const displayLines = composerView.displayLines;
  const displayLinesRef = useRef(displayLines);
  useEffect(() => {
    displayLinesRef.current = displayLines;
  }, [displayLines]);

  const mentionRanges = useMemo(
    () => (highlightMentions ? getMentionRanges(safeValue) : []),
    [highlightMentions, safeValue]
  );

  const insertText = useCallback(
    (text: string) => {
      if (!text) return;
      const normalizedChunk = sanitizeComposerText(text);
      if (!normalizedChunk) return;
      const clampedCursor = getLiveCursor();
      const liveValue = getLiveValue();
      const before = liveValue.slice(0, clampedCursor);
      const after = liveValue.slice(clampedCursor);
      const nextCursor = clampedCursor + normalizedChunk.length;
      stickyColumnRef.current = null;
      const nextValue = before + normalizedChunk + after;
      const normalizedNext = sanitizeComposerText(nextValue);
      const adjustedCursor = Math.min(nextCursor, normalizedNext.length);
      valueRef.current = normalizedNext;
      cursorRef.current = adjustedCursor;
      onCursorChange(adjustedCursor);
      onChange(normalizedNext);
    },
    [getLiveCursor, getLiveValue, onChange, onCursorChange]
  );

  const moveHorizontal = useCallback(
    (delta: number) => {
      stickyColumnRef.current = null;
      const clampedCursor = getLiveCursor();
      const liveValue = getLiveValue();
      const nextCursor = Math.min(Math.max(clampedCursor + delta, 0), liveValue.length);
      cursorRef.current = nextCursor;
      onCursorChange(nextCursor);
    },
    [getLiveCursor, getLiveValue, onCursorChange]
  );

  const removeChar = useCallback(
    (offset: -1 | 0) => {
      const clampedCursor = getLiveCursor();
      if (offset === -1 && clampedCursor === 0) return;
      const liveValue = getLiveValue();
      if (offset === 0 && clampedCursor >= liveValue.length) return;
      const removeIndex = offset === -1 ? clampedCursor - 1 : clampedCursor;
      const before = liveValue.slice(0, removeIndex);
      const after = liveValue.slice(removeIndex + 1);
      stickyColumnRef.current = null;
      const nextValue = before + after;
      const normalizedNext = sanitizeComposerText(nextValue);
      const nextCursor = Math.max(Math.min(removeIndex, normalizedNext.length), 0);
      cursorRef.current = nextCursor;
      onCursorChange(nextCursor);
      valueRef.current = normalizedNext;
      onChange(normalizedNext);
    },
    [getLiveCursor, getLiveValue, onChange, onCursorChange]
  );

  const getCursorSnapshot = useCallback(() => {
    const lines = displayLinesRef.current.length > 0 ? displayLinesRef.current : [{ start: 0, end: 0, columns: [0] }];
    const clampedCursor = getLiveCursor();
    let row = lines.length - 1;
    for (let idx = 0; idx < lines.length; idx++) {
      const line = lines[idx];
      if (clampedCursor < line.end) {
        row = idx;
        break;
      }
      if (clampedCursor === line.end) {
        if (idx + 1 < lines.length && lines[idx + 1].start === line.end) {
          row = idx + 1;
        } else {
          row = idx;
        }
        break;
      }
    }
    const line = lines[row];
    const relativeIndex = Math.max(0, Math.min(line.columns.length - 1, clampedCursor - line.start));
    const column = line.columns[relativeIndex] ?? 0;
    return { row, column, lines };
  }, [displayLinesRef, getLiveCursor]);

  const indexForColumn = useCallback((line: DisplayLine, targetColumn: number) => {
    if (line.columns.length === 0 || targetColumn <= 0) {
      return line.start;
    }
    let closestIndex = 0;
    for (let i = 0; i < line.columns.length; i++) {
      const widthAtIndex = line.columns[i];
      if (widthAtIndex <= targetColumn) {
        closestIndex = i;
      } else {
        break;
      }
    }
    return Math.min(line.start + closestIndex, line.end);
  }, []);

  const moveVertical = useCallback(
    (direction: -1 | 1) => {
      const snapshot = getCursorSnapshot();
      const desiredColumn = stickyColumnRef.current ?? snapshot.column;
      if (direction === -1 && snapshot.row === 0) {
        stickyColumnRef.current = desiredColumn;
        onCursorChange(0);
        return;
      }
      if (direction === 1 && snapshot.row >= snapshot.lines.length - 1) {
        stickyColumnRef.current = desiredColumn;
        onCursorChange(safeValue.length);
        return;
      }
      const targetRow = Math.min(
        Math.max(snapshot.row + direction, 0),
        snapshot.lines.length - 1
      );
      const targetLine = snapshot.lines[targetRow];
      const targetIndex = indexForColumn(targetLine, desiredColumn);
      stickyColumnRef.current = desiredColumn;
      onCursorChange(targetIndex);
      cursorRef.current = targetIndex;
    },
    [getCursorSnapshot, indexForColumn, onCursorChange]
  );

  useInput(
    (inputKey, key) => {
      if (!isActive) {
        return;
      }
      if (key.tab || (key.ctrl && inputKey === 'c')) {
        return;
      }
      const normalizedInput = typeof inputKey === 'string' ? inputKey : '';
      const wantsCtrlNewline =
        !key.meta &&
        !key.shift &&
        ((key.ctrl && (key.return || normalizedInput.toLowerCase() === 'j')) || normalizedInput === '\n');
      if (wantsCtrlNewline) {
        insertText('\n');
        return;
      }
      if (key.return) {
        if (submitDisabled) {
          return;
        }
        onSubmit();
        return;
      }
      if (key.leftArrow) {
        moveHorizontal(-1);
        return;
      }
      if (key.rightArrow) {
        moveHorizontal(1);
        return;
      }
      if (submitDisabled && (key.upArrow || key.downArrow)) {
        return;
      }
      if (key.upArrow) {
        moveVertical(-1);
        return;
      }
      if (key.downArrow) {
        moveVertical(1);
        return;
      }
      if (key.backspace || key.delete || inputKey === '\u0008' || inputKey === '\u007f') {
        removeChar(-1);
        return;
      }
      const isPrintable =
        typeof inputKey === 'string' &&
        inputKey.length > 0 &&
        !/^[\u0000-\u001F\u007F]$/.test(inputKey);
      if (!key.ctrl && !key.meta && isPrintable) {
        insertText(inputKey);
      }
    },
    { isActive }
  );

  const renderPortion = useCallback(
    (start: number, end: number) => {
      if (start >= end) return null;
      if (!highlightMentions || mentionRanges.length === 0) {
        return safeValue.slice(start, end);
      }
      const nodes: React.ReactNode[] = [];
      let pointer = start;
      let segmentId = 0;
      mentionRanges.forEach((range) => {
        if (range.end <= start || range.start >= end) {
          return;
        }
        if (range.start > pointer) {
          nodes.push(
            <Text key={`plain-${segmentId++}`}>{safeValue.slice(pointer, Math.min(range.start, end))}</Text>
          );
        }
        const overlapStart = Math.max(range.start, start);
        const overlapEnd = Math.min(range.end, end);
        nodes.push(
          <Text key={`mention-${segmentId++}`} color="cyan">
            {safeValue.slice(overlapStart, overlapEnd)}
          </Text>
        );
        pointer = overlapEnd;
      });
      if (pointer < end) {
        nodes.push(<Text key={`plain-${segmentId++}`}>{safeValue.slice(pointer, end)}</Text>);
      }
      return nodes;
    },
    [highlightMentions, mentionRanges, safeValue]
  );

  const clampedCursor = renderCursor;

  const linesToRender = composerView.visibleLines.length
    ? composerView.visibleLines
    : [{ start: 0, end: 0, columns: [0] }];
  const clippedTop = composerView.clippedTop;
  const clippedBottom = composerView.clippedBottom;

  const padLine = (line: DisplayLine) => {
    const textSlice = safeValue.slice(line.start, line.end);
    const paddingWidth = Math.max(0, width - stringWidth(textSlice));
    return ' '.repeat(paddingWidth);
  };

  const renderLineWithCursor = (line: DisplayLine) => {
    const afterFull = safeValue.slice(clampedCursor);
    const isNewlineCursor = afterFull.startsWith('\n');
    const cursorChar = isNewlineCursor ? ' ' : afterFull.length > 0 ? afterFull[0] : ' ';
    const consumed = afterFull.length > 0 ? 1 : 0;
    const beforeNodes = renderPortion(line.start, clampedCursor);
    const afterNodes = renderPortion(clampedCursor + consumed, line.end);
    return (
      <Text wrap="truncate-end">
        {beforeNodes}
        <Text inverse>{cursorChar}</Text>
        {afterNodes ?? ''}
        {padLine(line)}
      </Text>
    );
  };

  const renderLine = (line: DisplayLine) => {
    const cursorWithin = isActive && clampedCursor >= line.start && clampedCursor <= line.end;
    if (cursorWithin) {
      return renderLineWithCursor(line);
    }
    const portion = renderPortion(line.start, line.end) ?? ' ';
    return (
      <Text wrap="truncate-end">
        {portion}
        {padLine(line)}
      </Text>
    );
  };

  if (!safeValue.length && !isActive) {
    return placeholder ? <Text dimColor>{placeholder}</Text> : <Text> </Text>;
  }

  if (!safeValue.length && isActive) {
    return (
      <Text>
        <Text inverse> </Text>
        {placeholder ? <Text dimColor>{placeholder}</Text> : null}
      </Text>
    );
  }

  return (
    <Box flexDirection="column" width={Math.max(4, width)}>
      {clippedTop && (
        <Text dimColor>
          ⋮
        </Text>
      )}
      {linesToRender.map((line, idx) => (
        <Box key={`${line.start}-${idx}`}>
          {renderLine(line)}
        </Box>
      ))}
      {clippedBottom && (
        <Text dimColor>
          ⋮
        </Text>
      )}
    </Box>
  );
}

const openDirectory = (dir: string) => {
  const platform = process.platform;
  const target = dir || process.cwd();
  let child;
  if (platform === 'darwin') {
    child = spawn('open', [target], { stdio: 'ignore', detached: true });
  } else if (platform === 'win32') {
    child = spawn('cmd', ['/c', 'start', '', target], { stdio: 'ignore', detached: true });
  } else {
    child = spawn('xdg-open', [target], { stdio: 'ignore', detached: true });
  }
  child.unref();
};

export { Transcript, MessageCard };
// Expose ComposerInput for testing
export const __private__ = { ComposerInput };
