import path from 'path';
import { describe, expect, it } from 'vitest';
import {
  appendMentionMetadata,
  detectMentionContext,
  extractMentionMetadata,
  formatMentionValue,
  getMentionRanges,
  replaceMentionsWithPaths
} from './mentions.js';

describe('mentions helpers', () => {
  it('detects mention context after @', () => {
    const text = 'Summarize @src/ui/App.tsx please';
    const cursor = text.indexOf(' please');
    const ctx = detectMentionContext(text, cursor);
    expect(ctx).toEqual({ start: 10, query: 'src/ui/App.tsx' });
  });

  it('handles scoped packages with @ in the path', () => {
    const text = 'Inspect @node_modules/@scope/pkg/src/index.ts';
    const cursor = text.length;
    const ctx = detectMentionContext(text, cursor);
    expect(ctx).toEqual({ start: 8, query: 'node_modules/@scope/pkg/src/index.ts' });
  });

  it('ignores invalid mention sequences', () => {
    const text = 'Email me @not-a/path?';
    const cursor = text.length;
    expect(detectMentionContext(text, cursor)).toBeNull();
  });

  it('formats mention insertion with quotes when needed', () => {
    expect(formatMentionValue('summary.md')).toBe('summary.md');
    expect(formatMentionValue('docs/notes final.md')).toBe('"docs/notes final.md"');
  });

  it('extracts absolute paths for metadata', () => {
    const root = '/repo';
    const meta = extractMentionMetadata('Check @src/index.ts and @"notes/todo.md"', root);
    expect(meta).toEqual({
      mentioned_files: [
        path.resolve(root, 'src/index.ts'),
        path.resolve(root, 'notes/todo.md')
      ]
    });
  });

  it('adds metadata block to message', () => {
    const meta = {
      mentioned_files: [path.resolve('/repo', 'summary.md')]
    };
    const appended = appendMentionMetadata('Please summarize', meta);
    expect(appended).toContain('[Mentioned files]');
    expect(appended).toContain('- /repo/summary.md');
  });

  it('computes mention ranges for highlighting', () => {
    const ranges = getMentionRanges('Use @a and @"b c"');
    expect(ranges).toEqual([
      { start: 4, end: 6 },
      { start: 11, end: 17 }
    ]);
  });

  it('replaces mentions with absolute paths', () => {
    const replaced = replaceMentionsWithPaths('Open @README.md and visit @src/', '/repo');
    expect(replaced).toBe('Open /repo/README.md and visit /repo/src/');
  });
});
