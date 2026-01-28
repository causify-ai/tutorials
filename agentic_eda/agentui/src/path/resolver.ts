import path from 'path';
import os from 'os';

export type ResolveOptions = {
  allowOutsideWorkspace?: boolean;
};

export type ResolveResult =
  | {
      ok: true;
      absolute: string;
      relative: string;
      virtual: string;
      input: string;
      isDirectoryHint: boolean;
    }
  | {
      ok: false;
      error: string;
      input: string;
    };

const sanitize = (value: string) => value.trim().replace(/^['"`]|['"`]$/g, '');

const stripMention = (value: string) => (value.startsWith('@') ? value.slice(1) : value);

const normalizeRoot = (root: string) => {
  if (!root) throw new Error('Workspace root is required');
  return path.resolve(root);
};

const toVirtualPath = (relative: string) => {
  if (!relative || relative === '.' || relative === '') return '/';
  const parts = relative.split(path.sep).filter(Boolean);
  return `/${parts.join('/')}`;
};

const looksLikeWindowsPath = (value: string) => /^[a-zA-Z]:\\/.test(value) || /^[a-zA-Z]:\//.test(value);

const expandHome = (value: string) => {
  if (value === '~') return os.homedir();
  if (value.startsWith('~/')) {
    return path.join(os.homedir(), value.slice(2));
  }
  return value;
};

export const resolveWorkspacePath = (root: string, rawInput: string | null | undefined, options?: ResolveOptions): ResolveResult => {
  const normalizedRoot = normalizeRoot(root);
  if (!rawInput || !rawInput.trim()) {
    return { ok: false, error: 'Path is empty', input: rawInput ?? '' };
  }
  const sanitized = sanitize(stripMention(rawInput));
  if (!sanitized) {
    return { ok: false, error: 'Path is empty', input: rawInput };
  }
  const dirHint = sanitized.endsWith('/') && sanitized !== '/';
  let candidate = sanitized.replace(/\/+$/, dirHint ? '/' : '');
  candidate = expandHome(candidate);
  const isWindows = looksLikeWindowsPath(candidate);
  const normalizedCandidate = candidate.startsWith('file://') ? candidate.replace(/^file:\/+/, '/') : candidate;
  let absolute: string;
  if (normalizedCandidate.startsWith('/') && !normalizedCandidate.startsWith(normalizedRoot)) {
    absolute = path.join(normalizedRoot, normalizedCandidate.replace(/^\/+/, ''));
  } else if (path.isAbsolute(normalizedCandidate) || isWindows) {
    absolute = path.resolve(normalizedCandidate);
  } else {
    absolute = path.resolve(normalizedRoot, normalizedCandidate);
  }
  const relative = path.relative(normalizedRoot, absolute);
  const outsideWorkspace = relative.startsWith('..') || path.isAbsolute(relative);
  if (outsideWorkspace && !options?.allowOutsideWorkspace) {
    return {
      ok: false,
      error: `Path ${absolute} is outside the workspace root ${normalizedRoot}`,
      input: rawInput
    };
  }
  return {
    ok: true,
    absolute,
    relative,
    virtual: toVirtualPath(relative),
    input: rawInput,
    isDirectoryHint: dirHint
  };
};

export const requireWorkspacePath = (root: string, raw: string, options?: ResolveOptions) => {
  const result = resolveWorkspacePath(root, raw, options);
  if (!result.ok) {
    throw new Error(result.error);
  }
  return result;
};

export const absoluteToVirtual = (root: string, absolute: string) => {
  const normalizedRoot = normalizeRoot(root);
  const resolvedAbsolute = path.resolve(absolute);
  const relative = path.relative(normalizedRoot, resolvedAbsolute);
  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error(`Path ${resolvedAbsolute} is outside workspace ${normalizedRoot}`);
  }
  return {
    relative,
    virtual: toVirtualPath(relative)
  };
};
