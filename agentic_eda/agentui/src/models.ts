export type ModelInfo = {
  contextWindow: number;
};

const MODEL_INFO: Record<string, ModelInfo> = {
  'gpt-4o-mini': { contextWindow: 128_000 },
  'gpt-4o-mini-2024-07-18': { contextWindow: 128_000 },
  'gpt-4o': { contextWindow: 128_000 },
  'gpt-4.1-mini': { contextWindow: 128_000 },
  'gpt-4.1': { contextWindow: 128_000 },
  'gpt-5-nano': { contextWindow: 64_000 },
  'gpt-5-mini': { contextWindow: 128_000 },
  'gpt-5': { contextWindow: 200_000 },
  'gpt-5.1': { contextWindow: 200_000 },
  o1: { contextWindow: 200_000 },
  'o1-preview': { contextWindow: 200_000 },
  'o1-mini': { contextWindow: 200_000 }
};

const FALLBACK_CONTEXT_WINDOW = 100_000;

export const getModelContextWindow = (model: string): number => {
  return MODEL_INFO[model]?.contextWindow ?? FALLBACK_CONTEXT_WINDOW;
};

export const getKnownModels = (): string[] => Object.keys(MODEL_INFO);
