import { describe, it, expect } from 'vitest';
import { describeToolAction } from './tool-summaries.js';

describe('describeToolAction', () => {
  it('parses list_path inputs and renders paths', () => {
    const detail = describeToolAction(
      'list_path',
      { input: JSON.stringify({ targetPath: '/Users/test/project/tmp', path: '/Users/test/project/tmp' }) },
      '',
      'success'
    );
    expect(detail).toContain('/Users/test/project/tmp');
  });

  it('parses flattened glob inputs with path metadata', () => {
    const detail = describeToolAction(
      'glob_path',
      {
        input: {
          input: JSON.stringify({
            pattern: '**/sprint5*',
            targetPath: '/Users/test/project',
            maxDepth: 5
          })
        }
      },
      'No files matched pattern "**/sprint5*" under /Users/test/project.',
      'success'
    );
    expect(detail).toContain('**/sprint5*');
    expect(detail).toContain('/Users/test/project');
  });

  it('counts listed entries from tool output', () => {
    const output = `Listing for /tmp:\ndir  /tmp/folder\nfile /tmp/file.txt (12B)\n`;
    const detail = describeToolAction(
      'list_path',
      { input: JSON.stringify({ targetPath: '/tmp' }) },
      output,
      'success'
    );
    expect(detail).toContain('(2 entries)');
  });

  it('counts listed entries from single-line outputs', () => {
    const output = 'Listing for /tmp: dir /tmp/folder file /tmp/file.txt (12B)';
    const detail = describeToolAction(
      'list_path',
      { input: JSON.stringify({ targetPath: '/tmp' }) },
      output,
      'success'
    );
    expect(detail).toContain('(2 entries)');
  });
});
