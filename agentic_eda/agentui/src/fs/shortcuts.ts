import path from 'path';
import { promises as fs } from 'fs';
import { FilesystemBackend } from 'deepagents';
import { extractMentionMetadata } from '../ui/mentions.js';
import { createNotebook, runNotebook, summarizeNotebook } from '../tools/notebook.js';
import { buildImageTools } from '../tools/vision.js';
import { resolveWorkspacePath } from '../path/resolver.js';

const extractMentionedAbsolute = (prompt: string, root: string): string | null => {
  const metadata = extractMentionMetadata(prompt, root);
  if (!metadata?.mentioned_files?.length) return null;
  const first = metadata.mentioned_files[0];
  if (!first) return null;
  return first;
};

const resolveVirtualPath = (rawArg: string | undefined, prompt: string, root: string) => {
  if (rawArg) {
    const resolution = resolveWorkspacePath(root, rawArg);
    if (resolution.ok) {
      return resolution.absolute;
    }
  }
  const mentioned = extractMentionedAbsolute(prompt, root);
  if (mentioned) return mentioned;
  return root;
};

const resolveAbsolute = (root: string, raw: string) => {
  const resolution = resolveWorkspacePath(root, raw);
  if (!resolution.ok) {
    throw new Error(resolution.error);
  }
  return resolution;
};

const copyShortcut = async (root: string, sourceRaw: string, destRaw: string, overwrite: boolean) => {
  const source = resolveAbsolute(root, sourceRaw);
  const destination = resolveAbsolute(root, destRaw);
  const stats = await fs.stat(source.absolute);
  await fs.mkdir(path.dirname(destination.absolute), { recursive: true });
  if (stats.isDirectory()) {
    await fs.cp(source.absolute, destination.absolute, { recursive: true, force: overwrite });
  } else {
    if (!overwrite) {
      try {
        await fs.access(destination.absolute);
        throw new Error(`Destination ${destination.absolute} exists. Specify overwrite to replace.`);
      } catch {
        // available
      }
    }
    await fs.copyFile(source.absolute, destination.absolute);
  }
  return `Copied ${source.absolute} -> ${destination.absolute}`;
};

const moveShortcut = async (root: string, sourceRaw: string, destRaw: string, overwrite: boolean) => {
  const source = resolveAbsolute(root, sourceRaw);
  const destination = resolveAbsolute(root, destRaw);
  if (!overwrite) {
    try {
      await fs.access(destination.absolute);
      throw new Error(`Destination ${destination.absolute} exists. Specify overwrite to replace.`);
    } catch {
      // ok
    }
  }
  await fs.mkdir(path.dirname(destination.absolute), { recursive: true });
  await fs.rename(source.absolute, destination.absolute);
  return `Moved ${source.absolute} -> ${destination.absolute}`;
};

const deleteShortcut = async (root: string, targetRaw: string) => {
  const target = resolveAbsolute(root, targetRaw);
  await fs.rm(target.absolute, { recursive: true, force: true });
  return `Deleted ${target.absolute}`;
};

const mkdirShortcut = async (root: string, targetRaw: string) => {
  const target = resolveAbsolute(root, targetRaw);
  await fs.mkdir(target.absolute, { recursive: true });
  return `Created directory ${target.absolute}`;
};

const diffShortcut = async (root: string, leftRaw: string, rightRaw: string) => {
  const left = resolveAbsolute(root, leftRaw);
  const right = resolveAbsolute(root, rightRaw);
  const [leftContent, rightContent] = await Promise.all([
    fs.readFile(left.absolute, 'utf8'),
    fs.readFile(right.absolute, 'utf8')
  ]);
  if (leftContent === rightContent) {
    return 'Files are identical.';
  }
  const leftLines = leftContent.split('\n');
  const rightLines = rightContent.split('\n');
  const max = Math.max(leftLines.length, rightLines.length);
  const lines: string[] = [`Diff between ${left.absolute} and ${right.absolute}:`];
  for (let i = 0; i < max; i++) {
    const l = leftLines[i];
    const r = rightLines[i];
    if (l === r) continue;
    if (l !== undefined) lines.push(`- ${i + 1}: ${l}`);
    if (r !== undefined) lines.push(`+ ${i + 1}: ${r}`);
  }
  return lines.join('\n');
};

const formatEntries = (entries: Array<{ path: string; is_dir?: boolean }>) => {
  if (!entries.length) return 'No entries found.';
  const dirs = entries.filter((entry) => entry.is_dir);
  const files = entries.filter((entry) => !entry.is_dir);
  const renderList = (items: typeof entries) =>
    items
      .map((entry) => `- ${entry.path}`)
      .join('\n');
  const sections = [];
  if (dirs.length) sections.push('Directories:\n' + renderList(dirs));
  if (files.length) sections.push('Files:\n' + renderList(files));
  return sections.join('\n\n');
};

const runLs = async (backend: FilesystemBackend, target: string) => {
  const entries = await backend.lsInfo(target);
  return entries.length
    ? formatEntries(entries)
    : `No entries found in ${target}.`;
};

const runRead = async (
  backend: FilesystemBackend,
  target: string,
  lines: number | null
) => {
  const content = await backend.read(target, 0, 2000);
  if (!content) {
    return `No content returned for ${target}.`;
  }
  if (!lines) {
    return content;
  }
  const splitted = content.split('\n').slice(0, lines);
  return splitted.join('\n');
};

const runGrep = async (
  backend: FilesystemBackend,
  pattern: string,
  basePath: string
) => {
  const result = await backend.grepRaw(pattern, basePath);
  if (!Array.isArray(result) || result.length === 0) {
    return `No matches for '${pattern}' under ${basePath}.`;
  }
  const formatted = result
    .slice(0, 20)
    .map((match) => `${match.path}:${match.line} ${match.text}`)
    .join('\n');
  return formatted + (result.length > 20 ? `\n… ${result.length - 20} more` : '');
};

const runGlob = async (
  backend: FilesystemBackend,
  pattern: string,
  basePath?: string
) => {
  const results = await backend.globInfo(pattern, basePath);
  if (!results.length) {
    return `No files matched ${pattern}${basePath ? ` under ${basePath}` : ''}.`;
  }
  return results.map((entry) => `- ${entry.path}`).join('\n');
};

export const maybeExecuteFsCommand = async (
  prompt: string,
  root: string
): Promise<string | null> => {
  const trimmed = prompt.trim();
  if (!trimmed) return null;
  const lower = trimmed.toLowerCase();
  if (trimmed.endsWith('?') || lower.startsWith('what ') || lower.startsWith('which ') || lower.startsWith('who ')) {
    return null;
  }
  const backend = new FilesystemBackend({ rootDir: root, virtualMode: false });
  const imageMentionMatch = trimmed.match(/analyze\s+image\s+(.+)/i);
  if (imageMentionMatch) {
    const analyzer = buildImageTools(root)[0];
    const pathArg = imageMentionMatch[1].split(/\s+/)[0];
    const resolved = resolveVirtualPath(pathArg, trimmed, root);
    const result = await analyzer.invoke({ imagePath: resolved });
    return result;
  }

  const copyMatch =
    trimmed.match(/^(?:cp|copy|duplicate)\s+(\S+)\s+(?:to|into|as)\s+(\S+)\s*$/i) ||
    trimmed.match(/^(?:cp|copy)\s+(\S+)\s+(\S+)\s*$/i);
  if (copyMatch) {
    try {
      const response = await copyShortcut(root, copyMatch[1], copyMatch[2], /--force|--overwrite/i.test(trimmed));
      return response;
    } catch (error) {
      return error instanceof Error ? error.message : String(error);
    }
  }

  const moveMatch =
    trimmed.match(/^(?:mv|move|rename)\s+(\S+)\s+(?:to|into|as)\s+(\S+)\s*$/i) ||
    trimmed.match(/^(?:mv|move)\s+(\S+)\s+(\S+)\s*$/i);
  if (moveMatch) {
    try {
      const response = await moveShortcut(root, moveMatch[1], moveMatch[2], /--force|--overwrite/i.test(trimmed));
      return response;
    } catch (error) {
      return error instanceof Error ? error.message : String(error);
    }
  }

  const deleteMatch = trimmed.match(/^(?:rm|remove|delete)\s+(\S+)\s*$/i);
  if (deleteMatch) {
    try {
      const response = await deleteShortcut(root, deleteMatch[1]);
      return response;
    } catch (error) {
      return error instanceof Error ? error.message : String(error);
    }
  }

  const mkdirMatch = trimmed.match(/^(?:mkdir|create\s+(?:a\s+)?(?:dir(?:ectory)?|folder))\s+(\S+)\s*$/i);
  if (mkdirMatch) {
    try {
      const response = await mkdirShortcut(root, mkdirMatch[1]);
      return response;
    } catch (error) {
      return error instanceof Error ? error.message : String(error);
    }
  }

  const diffMatch =
    trimmed.match(/^(?:diff|compare)\s+(\S+)\s+(?:and|with)\s+(\S+)\s*$/i) ||
    trimmed.match(/^(?:diff)\s+(\S+)\s+(\S+)\s*$/i);
  if (diffMatch) {
    try {
      const response = await diffShortcut(root, diffMatch[1], diffMatch[2]);
      return response;
    } catch (error) {
      return error instanceof Error ? error.message : String(error);
    }
  }

  const createMatch = trimmed.match(/create\s+notebook\s+([^\s]+)\s+from\s+plan\s+([^\s]+)/i);
  if (createMatch) {
    const output = resolveVirtualPath(createMatch[1], trimmed, root);
    const planPath = path.resolve(root, createMatch[2].replace(/^@/, ''));
    const sections = JSON.parse(await fs.readFile(planPath, 'utf8'));
    const result = await createNotebook(root, sections, output);
    return `${result.message} (shortcut)`;
  }

  const runMatch = trimmed.match(/run\s+notebook\s+([^\s]+)(?:\s+into\s+([^\s]+))?/i);
  if (runMatch) {
    const input = resolveVirtualPath(runMatch[1], trimmed, root);
    const output = runMatch[2] ? resolveVirtualPath(runMatch[2], trimmed, root) : `${input.replace(/\.ipynb$/, '')}-executed.ipynb`;
    const result = await runNotebook(root, input, output);
    return `${result.message} (shortcut)`;
  }

  const summarizeMatch = trimmed.match(/(?:summarize|analyze)\s+notebook\s+([^\s]+)/i);
  if (summarizeMatch) {
    const input = resolveVirtualPath(summarizeMatch[1], trimmed, root);
    const result = await summarizeNotebook(root, input);
    return `${result.message}: ${result.raw}`;
  }

  const lsMatch =
    trimmed.match(/^ls\s+(.+)/i) ||
    trimmed.match(/(?:what\s+are|list)\s+(?:all\s+)?(?:the\s+)?(?:files|folders|directories)\s+(?:in|inside)\s+(.+)/i);
  if (lsMatch) {
    const target = resolveVirtualPath(lsMatch[1], trimmed, root);
    return runLs(backend, target);
  }

  const readDirectMatch = trimmed.match(/^read\s+(\S+)(?:\s+--lines\s+(\d+))?/i);
  if (readDirectMatch) {
    const target = resolveVirtualPath(readDirectMatch[1], trimmed, root);
    const lines = readDirectMatch[2] ? Number(readDirectMatch[2]) : null;
    return runRead(backend, target, lines);
  }
  const readFriendlyMatch = trimmed.match(
    /(?:show|display|read)\s+(?:the\s+)?(?:first\s+(\d+)\s+(?:lines|characters)\s+of\s+)?(.+)/i
  );
  if (readFriendlyMatch) {
    const target = resolveVirtualPath(readFriendlyMatch[2], trimmed, root);
    const lines = readFriendlyMatch[1] ? Number(readFriendlyMatch[1]) : null;
    return runRead(backend, target, lines);
  }

  const grepMatch = trimmed.match(/grep\s+"([^"]+)"\s+(.+)/i) || trimmed.match(/search\s+for\s+"([^"]+)"\s+(?:across|in)\s+(.+)/i);
  if (grepMatch) {
    const pattern = grepMatch[1];
    const basePath = resolveVirtualPath(grepMatch[2], trimmed, root);
    return runGrep(backend, pattern, basePath);
  }

  const globMatch = trimmed.match(/glob\s+"([^"]+)"\s+(.+)/i) || trimmed.match(/list\s+files\s+matching\s+"([^"]+)"\s+(?:in|under)\s+(.+)/i);
  if (globMatch) {
    const pattern = globMatch[1];
    const base = resolveVirtualPath(globMatch[2], trimmed, root);
    return runGlob(backend, pattern, base);
  }

  return null;
};
