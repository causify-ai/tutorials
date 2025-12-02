import path from 'path';
import { requireWorkspacePath } from '../path/resolver.js';

export type MentionContext = {
  start: number;
  query: string;
};

export type MentionRange = { start: number; end: number };

const MENTION_REGEX = /@(?:"[^"\n]+"|[A-Za-z0-9@._/-]+)/g;

export const detectMentionContext = (text: string, cursor: number): MentionContext | null => {
  let start = -1;
  for (let i = cursor - 1; i >= 0; i--) {
    const char = text[i];
    if (char === '@') {
      const prev = i > 0 ? text[i - 1] : '';
      if (i === 0 || /\s|\(|\[|\{|"|'|`/.test(prev)) {
        start = i;
        break;
      }
      continue;
    }
    if (!/[A-Za-z0-9@._/-]/.test(char)) {
      break;
    }
  }
  if (start === -1) return null;
  const before = text.slice(0, cursor);
  const charBefore = start > 0 ? before[start - 1] : '';
  if (start > 0 && charBefore && !/\s|\(|\[|\{|"|'|`/.test(charBefore)) {
    return null;
  }
  const query = before.slice(start + 1);
  if (query && !/^[a-zA-Z0-9@._/-]+$/.test(query)) {
    return null;
  }
  return { start, query };
};

const stripMentionToken = (token: string) => {
  return token.startsWith('"') && token.endsWith('"') ? token.slice(1, -1) : token;
};

export const formatMentionValue = (value: string) => {
  return /\s/.test(value) ? `"${value}"` : value;
};

const ensureAbsolutePath = (root: string, normalized: string, preserveTrailing: boolean) => {
  const result = requireWorkspacePath(root, normalized);
  let absolute = result.absolute;
  if (preserveTrailing && !absolute.endsWith(path.sep)) {
    absolute += path.sep;
  }
  return absolute;
};

export const replaceMentionsWithPaths = (text: string, root: string) => {
  return text.replace(MENTION_REGEX, (match) => {
    const token = match.slice(1);
    const normalized = stripMentionToken(token.replace(/\/$/, ''));
    const preservedSlash = match.endsWith('/');
    return ensureAbsolutePath(root, normalized, preservedSlash);
  });
};

export const getMentionRanges = (text: string): MentionRange[] => {
  const ranges: MentionRange[] = [];
  let match: RegExpExecArray | null;
  while ((match = MENTION_REGEX.exec(text)) !== null) {
    ranges.push({ start: match.index, end: match.index + match[0].length });
  }
  return ranges;
};

export const extractMentionMetadata = (text: string, root: string) => {
  const matches = Array.from(text.matchAll(MENTION_REGEX));
  if (matches.length === 0) return null;
  const files: string[] = [];
  matches.forEach((match) => {
    const token = match[0].slice(1);
    const normalized = stripMentionToken(token.replace(/\/$/, ''));
    const absolute = ensureAbsolutePath(root, normalized, false);
    files.push(absolute);
  });
  return files.length ? { mentioned_files: files } : null;
};

export const appendMentionMetadata = (content: string, metadata: { mentioned_files: string[] }) => {
  return `${content}\n\n[Mentioned files]\n${metadata.mentioned_files.map((file) => `- ${file}`).join('\n')}`;
};
