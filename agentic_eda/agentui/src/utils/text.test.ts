import { describe, expect, it } from 'vitest';
import { formatToolDetail } from './text.js';

describe('formatToolDetail', () => {
  const toolMessage = {
    lc: 1,
    type: 'constructor',
    id: ['langchain_core', 'messages', 'ToolMessage'],
    kwargs: {
      content: 'Run 123: 0 errors, 1 artifact.'
    }
  };

  it('extracts LangChain ToolMessage content', () => {
    expect(formatToolDetail(toolMessage)).toBe('Run 123: 0 errors, 1 artifact.');
  });

  it('extracts content when payload is an array of tool messages', () => {
    expect(formatToolDetail([toolMessage])).toBe('Run 123: 0 errors, 1 artifact.');
  });

});
