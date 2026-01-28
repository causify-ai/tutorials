export type PromptIntent = 'conversation' | 'filesystem' | 'notebook' | 'mixed';

export interface RouteDecision {
  intent: PromptIntent;
  confidence: number;
  reason: string;
  instructions: string;
}

const AFFIRMATIVE_REGEX =
  /^(yes|y|yep|yup|sure|please|please do|go ahead|do it|sounds good|okay|ok|alright|confirm)\b/i;
const GREETING_PATTERNS = [
  /^(hi|hello|hey|yo)\b/i,
  /good (morning|afternoon|evening)/i,
  /^thanks\b/i,
  /^thank you\b/i,
  /^howdy\b/i
];

const FILE_KEYWORDS = [
  'list',
  'ls',
  'show',
  'list out',
  'listings',
  'read',
  'write',
  'append',
  'insert',
  'open',
  'view',
  'cat',
  'tail',
  'head',
  'copy',
  'move',
  'rename',
  'delete',
  'remove',
  'rm',
  'mkdir',
  'files',
  'file',
  'folder',
  'folders',
  'directory',
  'directories',
  'workspace',
  'repo',
  'repository',
  'project root',
  'create file',
  'glob',
  'search',
  'diff',
  'compare',
  'top level',
  'level 0',
  'file tree',
  'analyze image'
];

const NOTEBOOK_KEYWORDS = [
  'notebook',
  'jupyter',
  'cell',
  'ipynb',
  'kernel',
  'nb',
  'run cell',
  'create notebook'
];

const EXTENSION_HINTS = [
  'md',
  'ts',
  'tsx',
  'js',
  'json',
  'py',
  'ipynb',
  'jpg',
  'jpeg',
  'png'
];

const formatInstructions = (intent: PromptIntent) => {
  switch (intent) {
    case 'conversation':
      return 'Respond conversationally and avoid filesystem or notebook tools unless the user explicitly asks for work.';
    case 'filesystem':
      return 'Plan filesystem actions, keep your to-do list updated, and describe every tool result in plain language.';
    case 'notebook':
      return 'Use notebook/ipynb helpers (create/run/analyze/patch/artifacts) with filesystem tools, updating the plan and reporting artifact locations clearly.';
    case 'mixed':
    default:
      return 'Blend conversational guidance with the necessary filesystem/notebook tools, explaining why each action is needed.';
  }
};

export const routePrompt = (
  prompt: string,
  options: { hasMention?: boolean; lastIntent?: PromptIntent | null } = {}
): RouteDecision => {
  const trimmed = prompt.trim();
  const normalized = trimmed.toLowerCase();
  let conversationScore = 0;
  let filesystemScore = 0;
  let notebookScore = 0;

  if (AFFIRMATIVE_REGEX.test(trimmed) && options.lastIntent && options.lastIntent !== 'conversation') {
    return {
      intent: options.lastIntent,
      confidence: 1,
      reason: 'Affirmative reply referencing prior tool intent.',
      instructions: formatInstructions(options.lastIntent)
    };
  }

  if (!trimmed) {
    conversationScore += 2;
  }

  if (options.hasMention) {
    filesystemScore += 2;
  }

  for (const pattern of GREETING_PATTERNS) {
    if (pattern.test(trimmed)) {
      conversationScore += 3;
      break;
    }
  }

  if (/\?|explain|what|why|how/.test(normalized)) {
    conversationScore += 1;
  }

  FILE_KEYWORDS.forEach((keyword) => {
    if (normalized.includes(keyword)) {
      filesystemScore += 0.75;
    }
  });

  NOTEBOOK_KEYWORDS.forEach((keyword) => {
    if (normalized.includes(keyword)) {
      notebookScore += 2;
    }
  });

  const wildcardExtensionMatch = /\*\.[a-z0-9]+/i.test(trimmed);
  if (wildcardExtensionMatch) {
    filesystemScore += 1.5;
  }

  const extensionMatches = trimmed.match(/\.(\w{1,5})/gi) ?? [];
  extensionMatches.forEach((ext) => {
    const clean = ext.replace('.', '').toLowerCase();
    if (EXTENSION_HINTS.includes(clean)) {
      filesystemScore += 1.5;
    }
  });

  const totalSignal = conversationScore + filesystemScore + notebookScore;
  let intent: PromptIntent = 'mixed';
  let dominantScore = 0;

  if (totalSignal === 0) {
    intent = 'conversation';
    dominantScore = 1;
  } else {
    dominantScore = Math.max(conversationScore, filesystemScore, notebookScore);
    if (dominantScore === conversationScore && dominantScore >= filesystemScore + 1 && dominantScore >= notebookScore + 1) {
      intent = 'conversation';
    } else if (dominantScore === notebookScore && notebookScore >= filesystemScore + 0.5) {
      intent = 'notebook';
    } else if (dominantScore === filesystemScore && filesystemScore >= notebookScore) {
      intent = 'filesystem';
    } else if (!dominantScore) {
      intent = 'conversation';
    } else {
      intent = 'mixed';
    }
  }

  const confidence =
    totalSignal === 0 ? 1 : Math.min(1, dominantScore / Math.max(1, totalSignal));

  const reason =
    intent === 'conversation'
      ? 'No strong filesystem or notebook cues detected.'
      : intent === 'filesystem'
        ? 'Detected filesystem verbs, mentions, or explicit file references.'
        : intent === 'notebook'
          ? 'Notebook-specific language detected.'
          : 'Prompt mixes conversational context with tool-oriented cues.';

  return {
    intent,
    confidence,
    reason,
    instructions: formatInstructions(intent)
  };
};
