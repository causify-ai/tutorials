import { describe, it, expect } from 'vitest';
import path from 'path';
import { absoluteToVirtual, resolveWorkspacePath, requireWorkspacePath } from './resolver.js';

const root = path.resolve('/Users/example/project');

describe('resolveWorkspacePath', () => {
  it('resolves relative paths', () => {
    const result = resolveWorkspacePath(root, 'src/index.ts');
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.absolute).toBe(path.join(root, 'src/index.ts'));
      expect(result.virtual).toBe('/src/index.ts');
    }
  });

  it('resolves mention paths', () => {
    const result = resolveWorkspacePath(root, '@examples/demo.md');
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.virtual).toBe('/examples/demo.md');
    }
  });

  it('treats /examples as workspace-relative', () => {
    const result = resolveWorkspacePath(root, '/examples/demo.md');
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.absolute).toBe(path.join(root, 'examples/demo.md'));
    }
  });

  it('allows fully qualified absolute paths when inside root', () => {
    const absolutePath = path.join(root, 'README.md');
    const result = resolveWorkspacePath(root, absolutePath);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.absolute).toBe(absolutePath);
    }
  });

  it('blocks directory traversal outside workspace', () => {
    const result = resolveWorkspacePath(root, '../etc/passwd');
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toMatch(/outside the workspace/);
    }
  });
});

describe('requireWorkspacePath', () => {
  it('throws on invalid input', () => {
    expect(() => requireWorkspacePath(root, '../etc/passwd')).toThrow(/outside the workspace/);
  });
});

describe('absoluteToVirtual', () => {
  it('converts absolute to virtual', () => {
    const absolute = path.join(root, 'src/app.ts');
    const { virtual } = absoluteToVirtual(root, absolute);
    expect(virtual).toBe('/src/app.ts');
  });
});
