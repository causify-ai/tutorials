import { describe, expect, it } from 'vitest';
import {
  accumulateUsage,
  calculateContextPercent,
  usageFromMetadata,
  BASELINE_TOKENS,
  type TokenUsage
} from './usage.js';

describe('usage helpers', () => {
  it('creates usage from metadata', () => {
    expect(
      usageFromMetadata({ input_tokens: 10, output_tokens: 5, total_tokens: 20 })
    ).toEqual({ inputTokens: 10, outputTokens: 5, totalTokens: 20 });
  });

  it('returns null when metadata empty', () => {
    expect(usageFromMetadata({ input_tokens: 0, output_tokens: 0, total_tokens: 0 })).toBeNull();
  });

  it('accumulates usage', () => {
    const initial: TokenUsage = { inputTokens: 10, outputTokens: 5, totalTokens: 20 };
    const delta: TokenUsage = { inputTokens: 2, outputTokens: 3, totalTokens: 6 };
    expect(accumulateUsage(initial, delta)).toEqual({
      inputTokens: 12,
      outputTokens: 8,
      totalTokens: 26
    });
  });

  it('calculates percent remaining with baseline adjustment', () => {
    const usage: TokenUsage = {
      inputTokens: BASELINE_TOKENS,
      outputTokens: 0,
      totalTokens: BASELINE_TOKENS
    };
    expect(calculateContextPercent(usage, BASELINE_TOKENS + 100)).toBe(100);
    const heavyUsage: TokenUsage = {
      inputTokens: BASELINE_TOKENS + 75,
      outputTokens: 25,
      totalTokens: BASELINE_TOKENS + 100
    };
    expect(calculateContextPercent(heavyUsage, BASELINE_TOKENS + 100)).toBe(0);
  });
});
