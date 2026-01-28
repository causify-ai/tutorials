import { describe, expect, it } from 'vitest';
import { prepareAgentInput } from './prompt.js';
import path from 'path';

const root = path.resolve(process.cwd());

describe('prepareAgentInput', () => {
  it('injects notebook guardrails once for notebook intent', () => {
    const result = prepareAgentInput('please create a notebook for plotting', root);
    expect(result.includedNotebookTips).toBe(true);
    expect(result.content).toContain('[Notebook guardrails]');
  });

  it('skips guardrails when already shown', () => {
    const result = prepareAgentInput('please create another notebook', root, {
      notebookTipsShown: true
    });
    expect(result.includedNotebookTips).toBe(false);
    expect(result.content).not.toContain('[Notebook guardrails]');
  });
});
