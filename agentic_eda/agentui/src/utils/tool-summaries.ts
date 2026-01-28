import { formatToolDetail, summarizeText } from './text.js';

type ToolStatus = 'running' | 'success' | 'error';

type SummaryParams = {
  rawName?: string;
  normalized: string;
  status: ToolStatus;
  input?: unknown;
  output?: unknown;
};

const TOOL_ALIASES: Record<string, string> = {
  ls: 'list_path',
  dir: 'list_path',
  cat: 'read_file',
  read: 'read_file',
  write: 'write_file',
  append: 'append_file',
  rm: 'delete_path',
  del: 'delete_path',
  cp: 'copy_path',
  mv: 'move_path',
  mkdir: 'make_directory',
  glob: 'glob_path',
  grep: 'search_text',
  diff: 'diff_paths'
};

const PRETTY_NAMES: Record<string, string> = {
  list_path: 'list path',
  read_file: 'read file',
  write_file: 'write file',
  append_file: 'append file',
  copy_path: 'copy path',
  move_path: 'move path',
  delete_path: 'delete path',
  make_directory: 'make directory',
  search_text: 'search text',
  glob_path: 'glob path',
  diff_paths: 'diff files',
  write_todos: 'update todo list',
  ipynb_create: 'create notebook',
  ipynb_run: 'run notebook',
  ipynb_analyze: 'summarize notebook'
};

const normalizeName = (raw?: string): string => {
  if (!raw) return 'tool';
  const lower = raw.toLowerCase();
  return TOOL_ALIASES[lower] ?? lower;
};

const normalizeToolInput = <T extends Record<string, unknown>>(input: unknown): T | undefined => {
  if (!input) return undefined;
  let current: unknown = input;
  const unwrap = (value: unknown): unknown => {
    if (typeof value === 'object' && value !== null && 'input' in (value as Record<string, unknown>)) {
      return (value as Record<string, unknown>).input;
    }
    return value;
  };
  current = unwrap(current);
  while (
    typeof current === 'object' &&
    current !== null &&
    'input' in (current as Record<string, unknown>)
  ) {
    current = unwrap(current);
  }
  if (typeof current === 'string') {
    try {
      return JSON.parse(current) as T;
    } catch {
      return undefined;
    }
  }
  if (typeof current === 'object' && current !== null) {
    const value = current as Record<string, unknown>;
    if ('kwargs' in value && value.kwargs && typeof value.kwargs === 'object') {
      return value.kwargs as T;
    }
    return value as T;
  }
  return undefined;
};

const getFieldFromRaw = (input: unknown, key: string): string | undefined => {
  if (!input) return undefined;
  try {
    const raw =
      typeof input === 'string'
        ? input
        : JSON.stringify(
            typeof input === 'object' && input !== null ? input : { value: String(input) }
          );
    const regex = new RegExp(`"${key}"\\s*:\\s*"([^"]*)"`, 'i');
    return regex.exec(raw)?.[1];
  } catch {
    return undefined;
  }
};

const prettyName = (normalized: string, raw?: string) => {
  if (PRETTY_NAMES[normalized]) {
    return PRETTY_NAMES[normalized];
  }
  return raw ? raw.replace(/_/g, ' ') : normalized.replace(/_/g, ' ');
};

const formatPath = (value?: unknown, fallback = '/') => {
  if (typeof value === 'string' && value.trim().length) {
    return value;
  }
  return fallback;
};

const summarizeListing = (output: unknown) => {
  if (typeof output !== 'string') return '';
  const lines = output.split('\n');
  if (!lines.length) return '';
  const entries = lines
    .map((line) => line.trim())
    .filter((line) => {
      if (!line.length) return false;
      if (/^listing for /i.test(line)) return false;
      if (/^directory is empty/i.test(line)) return true;
      return true;
    });
  // Prefer explicit count if present.
  const countMatch = /\b(\d+)\s+entr(?:y|ies)\b/i.exec(output);
  if (countMatch) {
    const n = Number(countMatch[1]);
    return `${n} entr${n === 1 ? 'y' : 'ies'}`;
  }
  let entryCount = entries.filter((line) => !/^directory is empty/i.test(line)).length;
  if (entryCount === 0 && !/directory is empty/i.test(output)) {
    const markerMatches = output.match(/(?:^|\s)(dir|file|other)\s+[^\s]+/gi);
    if (markerMatches?.length) {
      entryCount = markerMatches.length;
    }
  }
  return `${entryCount} entr${entryCount === 1 ? 'y' : 'ies'}`;
};

const summarizeRead = (output: unknown) => {
  if (typeof output !== 'string') return '';
  const truncatedMatch = /truncated \((\d+) more bytes\)/i.exec(output);
  if (truncatedMatch) {
    return `first chunk, ${truncatedMatch[1]} more byte(s) available`;
  }
  return `${output.length} character(s)`;
};

const summarizeMatches = (output: unknown) => {
  if (typeof output !== 'string') return 0;
  const trimmed = output.trim();
  if (!trimmed) return 0;
  const needsMatches = [
    /no files matched pattern/i,
    /no matches/i,
    /directory is empty/i
  ];
  if (needsMatches.some((regex) => regex.test(trimmed))) {
    return 0;
  }
  const lines = trimmed.split('\n').filter((line) => line.trim().length);
  return lines.length;
};

const extractListingPath = (output: unknown): string | undefined => {
  if (typeof output !== 'string') return undefined;
  const match = /Listing for (.+?):/i.exec(output);
  return match?.[1];
};

const extractCopyPaths = (
  output: unknown
):
  | {
      source: string;
      destination: string;
    }
  | undefined => {
  if (typeof output !== 'string') return undefined;
  const match = /Copied (.+?) to (.+?)\./i.exec(output);
  if (match) {
    return { source: match[1], destination: match[2] };
  }
  return undefined;
};

const extractGlobNoMatch = (
  output: unknown
):
  | {
      pattern: string;
      base: string;
    }
  | undefined => {
  if (typeof output !== 'string') return undefined;
  const match = /No files matched pattern "([^"]*)" under (.+?)\./i.exec(output);
  if (match) {
    return { pattern: match[1], base: match[2] };
  }
  return undefined;
};

const summarizers: Record<
  string,
  (params: SummaryParams) => string
> = {
  list_path: ({ input, output, status }) => {
    const payload = normalizeToolInput<{ targetPath?: string; path?: string; dir_path?: string }>(input);
    const targetPath =
      payload?.targetPath ??
      payload?.dir_path ??
      payload?.path ??
      getFieldFromRaw(input, 'dir_path') ??
      getFieldFromRaw(input, 'targetPath') ??
      getFieldFromRaw(input, 'path') ??
      extractListingPath(output);
    const target = formatPath(targetPath);
    if (status !== 'success') {
      return `Listed ${target}`;
    }
    const summary = summarizeListing(output);
    return summary ? `Listed ${target} (${summary})` : `Listed ${target}`;
  },
  read_file: ({ input, output }) => {
    const payload = normalizeToolInput<{ targetPath?: string; file_path?: string }>(input);
    const target =
      payload?.targetPath ??
      payload?.file_path ??
      getFieldFromRaw(input, 'file_path') ??
      getFieldFromRaw(input, 'targetPath');
    const sizeSummary = summarizeRead(output);
    return sizeSummary ? `Read ${formatPath(target)} (${sizeSummary})` : `Read ${formatPath(target)}`;
  },
  write_file: ({ input }) => {
    const payload = normalizeToolInput<{ targetPath?: string; file_path?: string; content?: string; text?: string }>(input);
    const target =
      payload?.targetPath ??
      payload?.file_path ??
      getFieldFromRaw(input, 'file_path') ??
      getFieldFromRaw(input, 'targetPath');
    const body = payload?.content ?? payload?.text ?? getFieldFromRaw(input, 'content') ?? getFieldFromRaw(input, 'text');
    const chars = body?.length ?? 0;
    return `Wrote ${target} (${chars} char${chars === 1 ? '' : 's'})`;
  },
  append_file: ({ input }) => {
    const payload = normalizeToolInput<{ targetPath?: string; file_path?: string; content?: string; text?: string }>(input);
    const target =
      payload?.targetPath ??
      payload?.file_path ??
      getFieldFromRaw(input, 'file_path') ??
      getFieldFromRaw(input, 'targetPath');
    const body = payload?.content ?? payload?.text ?? getFieldFromRaw(input, 'content') ?? getFieldFromRaw(input, 'text');
    const chars = body?.length ?? 0;
    return `Appended ${chars} char${chars === 1 ? '' : 's'} to ${target}`;
  },
  copy_path: ({ input, output }) => {
    const payload = normalizeToolInput<{
      sourcePath?: string;
      destinationPath?: string;
      source_path?: string;
      destination_path?: string;
      overwrite?: boolean;
    }>(input) ?? {};
    let source =
      payload?.sourcePath ??
      payload?.source_path ??
      getFieldFromRaw(input, 'source_path') ??
      getFieldFromRaw(input, 'sourcePath');
    let destination =
      payload?.destinationPath ??
      payload?.destination_path ??
      getFieldFromRaw(input, 'destination_path') ??
      getFieldFromRaw(input, 'destinationPath');
    if (!source || !destination) {
      const parsed = extractCopyPaths(output);
      source = parsed?.source ?? source;
      destination = parsed?.destination ?? destination;
    }
    const formattedSource = formatPath(source);
    const formattedDestination = formatPath(destination);
    return payload?.overwrite
      ? `Copied ${formattedSource} → ${formattedDestination} (overwrite)`
      : `Copied ${formattedSource} → ${formattedDestination}`;
  },
  move_path: ({ input, output }) => {
    const payload = normalizeToolInput<{
      sourcePath?: string;
      destinationPath?: string;
      source_path?: string;
      destination_path?: string;
    }>(input) ?? {};
    let source =
      payload?.sourcePath ??
      payload?.source_path ??
      getFieldFromRaw(input, 'source_path') ??
      getFieldFromRaw(input, 'sourcePath');
    let destination =
      payload?.destinationPath ??
      payload?.destination_path ??
      getFieldFromRaw(input, 'destination_path') ??
      getFieldFromRaw(input, 'destinationPath');
    if ((!source || !destination) && typeof output === 'string') {
      const parsed = extractCopyPaths(output);
      source = parsed?.source ?? source;
      destination = parsed?.destination ?? destination;
    }
    return `Moved ${formatPath(source)} → ${formatPath(destination)}`;
  },
  delete_path: ({ input, output }) => {
    const payload = normalizeToolInput<{ targetPath?: string; file_path?: string }>(input);
    if (typeof output === 'string' && output.startsWith('Deleted ')) {
      return output;
    }
    const target =
      payload?.targetPath ??
      payload?.file_path ??
      getFieldFromRaw(input, 'file_path') ??
      getFieldFromRaw(input, 'targetPath');
    return `Deleted ${target}`;
  },
  make_directory: ({ input, output }) => {
    const payload = normalizeToolInput<{ targetPath?: string; dir_path?: string }>(input);
    let target =
      payload?.targetPath ??
      payload?.dir_path ??
      getFieldFromRaw(input, 'dir_path') ??
      getFieldFromRaw(input, 'targetPath');
    if ((!target || !target.length) && typeof output === 'string') {
      const match = /Created directory (.+)/i.exec(output);
      if (match) target = match[1];
    }
    return `Created directory ${formatPath(target)}`;
  },
  search_text: ({ input, output }) => {
    const payload = normalizeToolInput<{ pattern?: string; targetPath?: string; path?: string; dir_path?: string }>(input);
    const matches = summarizeMatches(output);
    const pattern =
      payload?.pattern ?? getFieldFromRaw(input, 'pattern') ?? getFieldFromRaw(input, 'query') ?? '';
    const target =
      payload?.targetPath ??
      payload?.dir_path ??
      payload?.path ??
      getFieldFromRaw(input, 'dir_path') ??
      getFieldFromRaw(input, 'targetPath') ??
      getFieldFromRaw(input, 'path');
    return `Searched "${pattern}" under ${formatPath(target)} (${matches} match${
      matches === 1 ? '' : 'es'
    })`;
  },
  glob_path: ({ input, output }) => {
    const payload = normalizeToolInput<{ pattern?: string; targetPath?: string; path?: string; dir_path?: string; maxDepth?: number }>(input) ?? {};
    let pattern = payload?.pattern ?? getFieldFromRaw(input, 'pattern');
    let base =
      payload?.targetPath ??
      payload?.dir_path ??
      payload?.path ??
      getFieldFromRaw(input, 'dir_path') ??
      getFieldFromRaw(input, 'targetPath') ??
      getFieldFromRaw(input, 'path');
    if (!pattern) {
      const parsed = extractGlobNoMatch(output);
      pattern = parsed?.pattern ?? pattern;
      base = parsed?.base ?? base;
    }
    const matches = summarizeMatches(output);
    const depth = payload?.maxDepth ?? 0;
    let sample = '';
    if (typeof output === 'string') {
      const lines = output
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line.length && !/^Listing for /i.test(line) && !/match/i.test(line));
      if (lines.length) {
        const shown = lines.slice(0, 3).join(', ');
        const more = lines.length > 3 ? `, … ${lines.length - 3} more` : '';
        sample = ` → ${shown}${more}`;
      }
    }
    return `Glob "${pattern ?? ''}" under ${formatPath(base)} (depth ${depth}, ${matches} match${
      matches === 1 ? '' : 'es'
    })${sample}`;
  },
  diff_paths: ({ input, output }) => {
    const payload = normalizeToolInput<{ leftPath?: string; rightPath?: string; left_path?: string; right_path?: string }>(input);
    const left =
      payload?.leftPath ??
      payload?.left_path ??
      getFieldFromRaw(input, 'left_path') ??
      getFieldFromRaw(input, 'leftPath');
    const right =
      payload?.rightPath ??
      payload?.right_path ??
      getFieldFromRaw(input, 'right_path') ??
      getFieldFromRaw(input, 'rightPath');
    if (typeof output === 'string' && output.includes('identical')) {
      return `Diffed ${formatPath(left)} vs ${formatPath(right)} (identical)`;
    }
    return `Diffed ${formatPath(left)} vs ${formatPath(right)}`;
  },
  write_todos: ({ output, status }) => {
    if (status === 'running') {
      return 'Updating to-do list';
    }
    return summarizeText(typeof output === 'string' ? output : JSON.stringify(output ?? ''), 120);
  },
  ipynb_create: ({ input, output, status }) => {
    const payload = normalizeToolInput<{ outputPath?: string }>(input);
    const target = formatPath(payload?.outputPath);
    if (status !== 'success') {
      return `Creating notebook ${target}`;
    }
    return `Created notebook ${target}`;
  },
  ipynb_run: ({ input, output, status }) => {
    const payload = normalizeToolInput<{ inputPath?: string; outputPath?: string }>(input) ?? {};
    if (status !== 'success') {
      return `Running notebook ${formatPath(payload?.inputPath)}`;
    }
    const text = formatToolDetail(output, 200);
    if (text) {
      const beforeRaw = text.split('Raw response:')[0].trim();
      return beforeRaw || summarizeText(text, 140);
    }
    return `Ran notebook ${formatPath(payload?.inputPath)} → ${formatPath(payload?.outputPath)}`;
  },
  ipynb_analyze: ({ input }) => {
    const payload = normalizeToolInput<{ inputPath?: string }>(input);
    return `Summarized notebook ${formatPath(payload?.inputPath)}`;
  }
};

const defaultSummarizer = ({ normalized, rawName, status, output }: SummaryParams) => {
  const label = prettyName(normalized, rawName);
  if (status === 'running') {
    return `Running ${label}`;
  }
  const summary = summarizeText(formatToolDetail(output), 80);
  return summary ? `${label}: ${summary}` : label;
};

export const describeToolAction = (
  rawName: string | undefined,
  input: unknown,
  output: unknown,
  status: ToolStatus
): string => {
  const normalized = normalizeName(rawName);
  const handler = summarizers[normalized] ?? defaultSummarizer;
  return handler({ rawName, normalized, status, input, output });
};
