import { describe, expect, it } from 'vitest';
import { DEFAULT_SYSTEM_PROMPT, ConfigError, loadConfig } from './index.js';

describe('loadConfig', () => {
  it('loads defaults when overrides provided', () => {
    const config = loadConfig({ OPENAI_API_KEY: 'sk-test' });
    expect(config).toEqual({
      openAIApiKey: 'sk-test',
      openAIModel: 'gpt-5-mini',
      systemPrompt: DEFAULT_SYSTEM_PROMPT
    });
  });

  it('allows overriding optional values', () => {
    const config = loadConfig({
      OPENAI_API_KEY: 'sk-test',
      OPENAI_MODEL: 'gpt-nova',
      SYSTEM_PROMPT: 'custom prompt'
    });
    expect(config.systemPrompt).toBe('custom prompt');
    expect(config.openAIModel).toBe('gpt-nova');
  });

  it('throws ConfigError when key missing', () => {
    const original = process.env.OPENAI_API_KEY;
    delete process.env.OPENAI_API_KEY;
    expect(() => loadConfig({})).toThrow(ConfigError);
    if (original) {
      process.env.OPENAI_API_KEY = original;
    } else {
      delete process.env.OPENAI_API_KEY;
    }
  });
});
