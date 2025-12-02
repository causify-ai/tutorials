export const BASELINE_TOKENS = 12_000;

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
}

export interface UsageMetadata {
  input_tokens?: number | null;
  output_tokens?: number | null;
  total_tokens?: number | null;
}

export const usageFromMetadata = (metadata?: UsageMetadata | null): TokenUsage | null => {
  if (!metadata) return null;
  const inputTokens = metadata.input_tokens ?? 0;
  const outputTokens = metadata.output_tokens ?? 0;
  const totalTokens = metadata.total_tokens ?? inputTokens + outputTokens;
  if (inputTokens === 0 && outputTokens === 0 && totalTokens === 0) {
    return null;
  }
  return { inputTokens, outputTokens, totalTokens };
};

export const accumulateUsage = (
  current: TokenUsage | undefined,
  delta: TokenUsage
): TokenUsage => ({
  inputTokens: (current?.inputTokens ?? 0) + delta.inputTokens,
  outputTokens: (current?.outputTokens ?? 0) + delta.outputTokens,
  totalTokens: (current?.totalTokens ?? 0) + delta.totalTokens
});

export const subtractUsage = (
  current: TokenUsage | undefined,
  delta: TokenUsage | undefined
): TokenUsage | undefined => {
  if (!current || !delta) return current;
  return {
    inputTokens: Math.max(0, current.inputTokens - delta.inputTokens),
    outputTokens: Math.max(0, current.outputTokens - delta.outputTokens),
    totalTokens: Math.max(0, current.totalTokens - delta.totalTokens)
  };
};

export const calculateContextPercent = (
  usage: TokenUsage | undefined,
  contextWindow?: number
): number | null => {
  if (!usage || !contextWindow) {
    return null;
  }
  if (contextWindow <= BASELINE_TOKENS) {
    return 0;
  }
  const effectiveWindow = contextWindow - BASELINE_TOKENS;
  const used = Math.max(0, usage.totalTokens - BASELINE_TOKENS);
  const remaining = Math.max(0, effectiveWindow - used);
  const percent = Math.round((remaining / effectiveWindow) * 100);
  return Math.max(0, Math.min(100, percent));
};
