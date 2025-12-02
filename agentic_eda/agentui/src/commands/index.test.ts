import { describe, expect, it } from 'vitest';
import { parseSlashCommand } from './index.js';

describe('parseSlashCommand', () => {
  it('parses model command with argument', () => {
    expect(parseSlashCommand('/model gpt-4o')).toEqual({ type: 'model', value: 'gpt-4o' });
  });

  it('parses model command without argument', () => {
    expect(parseSlashCommand('/model')).toEqual({ type: 'model', value: undefined });
  });

  it('parses control commands', () => {
    expect(parseSlashCommand('/new')).toEqual({ type: 'new' });
    expect(parseSlashCommand('/undo')).toEqual({ type: 'undo' });
    expect(parseSlashCommand('/quit')).toEqual({ type: 'quit' });
    expect(parseSlashCommand('/exit')).toEqual({ type: 'exit' });
  });

  it('returns null for unknown input', () => {
    expect(parseSlashCommand('/unknown')).toBeNull();
    expect(parseSlashCommand('hello')).toBeNull();
  });
});
