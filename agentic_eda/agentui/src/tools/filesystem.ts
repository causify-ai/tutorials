import { promises as fs, Dirent } from 'fs';
import path from 'path';
import { tool } from 'langchain';
import { z } from 'zod';
import { requireWorkspacePath } from '../path/resolver.js';

const formatEntry = async (absolute: string) => {
  const stats = await fs.stat(absolute);
  const type = stats.isDirectory() ? 'dir ' : stats.isFile() ? 'file' : 'other';
  const size = stats.isDirectory() ? '' : `${stats.size}B`;
  return `${type.padEnd(4)} ${absolute}${size ? ` (${size})` : ''}`;
};

const listDirectory = async (absolute: string) => {
  const entries = await fs.readdir(absolute);
  if (!entries.length) {
    return 'Directory is empty.';
  }
  const lines = await Promise.all(entries.map((name) => formatEntry(path.join(absolute, name))));
  return lines.join('\n');
};

const summarizeAction = (label: string, absolute: string) => `${label}: ${absolute}`;

const wrapError = (err: unknown) => (err instanceof Error ? err.message : String(err));

const resolveForTool = (workspaceRoot: string, raw: string) => {
  const result = requireWorkspacePath(workspaceRoot, raw);
  return result;
};

const createLsTool = (workspaceRoot: string) =>
  tool(
    async ({ dir_path, targetPath }: { dir_path?: string; targetPath?: string }) => {
      const rawPath = dir_path ?? targetPath ?? '.';
      const resolved = resolveForTool(workspaceRoot, rawPath);
      try {
        const stats = await fs.stat(resolved.absolute);
        if (!stats.isDirectory()) {
          return `${resolved.absolute} is not a directory.`;
        }
        const body = await listDirectory(resolved.absolute);
        return `Listing for ${resolved.virtual}:\n${body}`;
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'list_path',
      description: 'List files/directories at a path (ls).',
      schema: z.object({
        dir_path: z.string().optional().describe('Directory to list (default workspace root).'),
        targetPath: z.string().optional().describe('Alias for dir_path (legacy).')
      })
    }
  );

const createReadTool = (workspaceRoot: string) =>
  tool(
    async ({ file_path, targetPath, offset, limit }: { file_path?: string; targetPath?: string; offset?: number; limit?: number }) => {
      try {
        const rawPath = file_path ?? targetPath;
        if (!rawPath) {
          throw new Error('file_path is required');
        }
        const resolved = resolveForTool(workspaceRoot, rawPath);
        const start = offset ?? 0;
        const maxBytes = limit ?? 4000;
        const data = await fs.readFile(resolved.absolute, 'utf8');
        const sliced = data.slice(start, start + maxBytes);
        if (data.length > start + maxBytes) {
          return `${sliced}\n… truncated (${data.length - (start + maxBytes)} more bytes)`;
        }
        return sliced;
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'read_file',
      description: 'Read a file (cat/head).',
      schema: z.object({
        file_path: z.string().optional().describe('File to read.'),
        targetPath: z.string().optional().describe('Alias for file_path (legacy).'),
        offset: z.number().int().nonnegative().optional().describe('Starting byte offset (default 0).'),
        limit: z.number().int().positive().optional().describe('Max bytes to return (default 4000).')
      })
    }
  );

const createWriteTool = (workspaceRoot: string) =>
  tool(
    async ({ file_path, targetPath, content, text }: { file_path?: string; targetPath?: string; content?: string; text?: string }) => {
      try {
        const rawPath = file_path ?? targetPath;
        if (!rawPath) {
          throw new Error('file_path is required');
        }
        const resolved = resolveForTool(workspaceRoot, rawPath);
        const body = content ?? text;
        if (body === undefined) {
          throw new Error('content is required');
        }
        await fs.mkdir(path.dirname(resolved.absolute), { recursive: true });
        await fs.writeFile(resolved.absolute, body, 'utf8');
        return summarizeAction('Wrote file', resolved.absolute);
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'write_file',
      description: 'Create or overwrite a file with given content.',
      schema: z.object({
        file_path: z.string().optional().describe('File to write.'),
        targetPath: z.string().optional().describe('Alias for file_path.'),
        content: z.string().optional().describe('Content to write.'),
        text: z.string().optional().describe('Alias for content.')
      })
    }
  );

const createAppendTool = (workspaceRoot: string) =>
  tool(
    async ({ file_path, targetPath, content, text }: { file_path?: string; targetPath?: string; content?: string; text?: string }) => {
      try {
        const rawPath = file_path ?? targetPath;
        if (!rawPath) {
          throw new Error('file_path is required');
        }
        const resolved = resolveForTool(workspaceRoot, rawPath);
        const body = content ?? text;
        if (body === undefined) {
          throw new Error('content is required');
        }
        await fs.appendFile(resolved.absolute, body, 'utf8');
        return summarizeAction('Appended to file', resolved.absolute);
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'append_file',
      description: 'Append text to an existing file.',
      schema: z.object({
        file_path: z.string().optional().describe('File to append to.'),
        targetPath: z.string().optional().describe('Alias for file_path.'),
        content: z.string().optional().describe('Text to append.'),
        text: z.string().optional().describe('Alias for content.')
      })
    }
  );

const createCopyTool = (workspaceRoot: string) =>
  tool(
    async ({
      sourcePath,
      destinationPath,
      source_path,
      destination_path,
      overwrite = false
    }: {
      sourcePath?: string;
      destinationPath?: string;
      source_path?: string;
      destination_path?: string;
      overwrite?: boolean;
    }) => {
      try {
        const sourceRaw = sourcePath ?? source_path;
        const destinationRaw = destinationPath ?? destination_path;
        if (!sourceRaw || !destinationRaw) {
          throw new Error('Both source_path and destination_path are required');
        }
        const source = resolveForTool(workspaceRoot, sourceRaw);
        const destination = resolveForTool(workspaceRoot, destinationRaw);
        const stats = await fs.stat(source.absolute);
        await fs.mkdir(path.dirname(destination.absolute), { recursive: true });
        if (stats.isDirectory()) {
          await fs.cp(source.absolute, destination.absolute, { recursive: true, force: overwrite });
        } else {
          if (!overwrite) {
            try {
              await fs.access(destination.absolute);
              return `Destination ${destination.absolute} exists. Set overwrite=true to replace.`;
            } catch {
              // ok
            }
          }
          await fs.copyFile(source.absolute, destination.absolute);
        }
        return `Copied ${source.absolute} to ${destination.absolute}.`;
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'copy_path',
      description: 'Copy a file or directory (cp).',
      schema: z.object({
        source_path: z.string().optional().describe('Source path.'),
        destination_path: z.string().optional().describe('Destination path.'),
        sourcePath: z.string().optional().describe('Alias for source_path.'),
        destinationPath: z.string().optional().describe('Alias for destination_path.'),
        overwrite: z.boolean().optional().describe('Whether to overwrite destination if it exists.')
      })
    }
  );

const createMoveTool = (workspaceRoot: string) =>
  tool(
    async ({
      sourcePath,
      destinationPath,
      source_path,
      destination_path,
      overwrite = false
    }: {
      sourcePath?: string;
      destinationPath?: string;
      source_path?: string;
      destination_path?: string;
      overwrite?: boolean;
    }) => {
      try {
        const sourceRaw = sourcePath ?? source_path;
        const destinationRaw = destinationPath ?? destination_path;
        if (!sourceRaw || !destinationRaw) {
          throw new Error('Both source_path and destination_path are required');
        }
        const source = resolveForTool(workspaceRoot, sourceRaw);
        const destination = resolveForTool(workspaceRoot, destinationRaw);
        if (!overwrite) {
          try {
            await fs.access(destination.absolute);
            return `Destination ${destination.absolute} exists. Set overwrite=true to replace.`;
          } catch {
            // available
          }
        }
        await fs.mkdir(path.dirname(destination.absolute), { recursive: true });
        await fs.rename(source.absolute, destination.absolute);
        return `Moved ${source.absolute} to ${destination.absolute}.`;
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'move_path',
      description: 'Move or rename files/directories (mv).',
      schema: z.object({
        source_path: z.string().optional().describe('Source path.'),
        destination_path: z.string().optional().describe('Destination path.'),
        sourcePath: z.string().optional().describe('Alias for source_path.'),
        destinationPath: z.string().optional().describe('Alias for destination_path.'),
        overwrite: z.boolean().optional().describe('Set true to replace destination.')
      })
    }
  );

const createDeleteTool = (workspaceRoot: string) =>
  tool(
    async ({ file_path, targetPath }: { file_path?: string; targetPath?: string }) => {
      try {
        const rawPath = file_path ?? targetPath;
        if (!rawPath) {
          throw new Error('file_path is required');
        }
        const resolved = resolveForTool(workspaceRoot, rawPath);
        await fs.rm(resolved.absolute, { recursive: true, force: true });
        return summarizeAction('Deleted', resolved.absolute);
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'delete_path',
      description: 'Delete files or directories (rm -rf).',
      schema: z.object({
        file_path: z.string().optional().describe('Path to delete.'),
        targetPath: z.string().optional().describe('Alias for file_path.')
      })
    }
  );

const createMkdirTool = (workspaceRoot: string) =>
  tool(
    async ({ dir_path, targetPath, recursive = true }: { dir_path?: string; targetPath?: string; recursive?: boolean }) => {
      try {
        const rawPath = dir_path ?? targetPath;
        if (!rawPath) {
          throw new Error('dir_path is required');
        }
        const resolved = resolveForTool(workspaceRoot, rawPath);
        await fs.mkdir(resolved.absolute, { recursive });
        return summarizeAction('Created directory', resolved.absolute);
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'make_directory',
      description: 'Create directories (mkdir).',
      schema: z.object({
        dir_path: z.string().optional().describe('Directory to create.'),
        targetPath: z.string().optional().describe('Alias for dir_path.'),
        recursive: z.boolean().optional().describe('Whether to create parent folders (default true).')
      })
    }
  );

const createSearchTool = (workspaceRoot: string) =>
  tool(
    async ({ pattern, dir_path, targetPath, maxDepth = 5 }: { pattern: string; dir_path?: string; targetPath?: string; maxDepth?: number }) => {
      try {
        const basePath = dir_path ?? targetPath;
        const base = basePath ? resolveForTool(workspaceRoot, basePath).absolute : workspaceRoot;
        const regex = new RegExp(pattern, 'i');
        const results: string[] = [];
        await walkDirectory(base, async (abs, entry, depth) => {
          if (!entry.isFile()) return;
          const content = await fs.readFile(abs, 'utf8');
          const lines = content.split('\n');
          lines.forEach((line, idx) => {
            if (regex.test(line)) {
              results.push(`${abs}:${idx + 1} ${line.trim()}`);
            }
          });
        }, maxDepth);
        if (!results.length) {
          return `No matches for "${pattern}" under ${base}.`;
        }
        if (results.length > 50) {
          return results.slice(0, 50).join('\n') + `\n… ${results.length - 50} more matches`;
        }
        return results.join('\n');
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'search_text',
      description: 'Search files for a regex or keyword (non-recursive by default).',
      schema: z.object({
        pattern: z.string().describe('Regex or plain-text pattern to search for.'),
        dir_path: z.string().optional().describe('Directory to search (default workspace root).'),
        targetPath: z.string().optional().describe('Alias for dir_path.'),
        maxDepth: z.number().int().min(0).optional().describe('Maximum directory depth to search (default 5).')
      })
    }
  );

const createGlobTool = (workspaceRoot: string) =>
  tool(
    async ({ pattern, dir_path, targetPath, maxDepth = 0 }: { pattern: string; dir_path?: string; targetPath?: string; maxDepth?: number }) => {
      try {
        const basePath = dir_path ?? targetPath;
        const base = basePath ? resolveForTool(workspaceRoot, basePath).absolute : workspaceRoot;
        const regex = globToRegex(pattern);
        const matches: string[] = [];
        await walkDirectory(
          base,
          async (abs, entry) => {
            if (entry.isFile() && regex.test(entry.name)) {
              matches.push(abs);
            }
          },
          maxDepth
        );
        if (!matches.length) {
          return `No files matched pattern "${pattern}" under ${base}.`;
        }
        return matches.join('\n');
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'glob_path',
      description: 'Find files matching a glob pattern at a given depth.',
      schema: z.object({
        pattern: z.string().describe('Glob pattern (e.g., *.md).'),
        dir_path: z.string().optional().describe('Directory to search (default workspace root).'),
        targetPath: z.string().optional().describe('Alias for dir_path.'),
        maxDepth: z.number().int().min(0).optional().describe('Depth to traverse (default 1 for top-level).')
      })
    }
  );

const walkDirectory = async (
  base: string,
  visitor: (absolute: string, entry: Dirent, depth: number) => Promise<void> | void,
  maxDepth = Infinity,
  depth = 0
) => {
  if (depth > maxDepth) return;
  const entries = await fs.readdir(base, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name.startsWith('.')) continue;
    const absolute = path.join(base, entry.name);
    await visitor(absolute, entry, depth);
    if (entry.isDirectory()) {
      await walkDirectory(absolute, visitor, maxDepth, depth + 1);
    }
  }
};

const globToRegex = (pattern: string) => {
  const escaped = pattern.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.');
  return new RegExp(`^${escaped}$`, 'i');
};

const createDiffTool = (workspaceRoot: string) =>
  tool(
    async ({
      leftPath,
      rightPath,
      left_path,
      right_path
    }: {
      leftPath?: string;
      rightPath?: string;
      left_path?: string;
      right_path?: string;
    }) => {
      try {
        const leftRaw = leftPath ?? left_path;
        const rightRaw = rightPath ?? right_path;
        if (!leftRaw || !rightRaw) {
          throw new Error('Both left_path and right_path are required');
        }
        const left = resolveForTool(workspaceRoot, leftRaw);
        const right = resolveForTool(workspaceRoot, rightRaw);
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
        const result: string[] = [];
        for (let i = 0; i < max; i++) {
          const l = leftLines[i];
          const r = rightLines[i];
          if (l === r) continue;
          if (l !== undefined) {
            result.push(`- ${i + 1}: ${l}`);
          }
          if (r !== undefined) {
            result.push(`+ ${i + 1}: ${r}`);
          }
        }
        return [`Diff between ${left.virtual} and ${right.virtual}:`, ...result].join('\n');
      } catch (error) {
        return wrapError(error);
      }
    },
    {
      name: 'diff_paths',
      description: 'Compare two files (rough diff).',
      schema: z.object({
        left_path: z.string().optional().describe('First file.'),
        right_path: z.string().optional().describe('Second file.'),
        leftPath: z.string().optional().describe('Alias for left_path.'),
        rightPath: z.string().optional().describe('Alias for right_path.')
      })
    }
  );

export const buildFilesystemTools = (workspaceRoot: string) => [
  createLsTool(workspaceRoot),
  createReadTool(workspaceRoot),
  createWriteTool(workspaceRoot),
  createAppendTool(workspaceRoot),
  createCopyTool(workspaceRoot),
  createMoveTool(workspaceRoot),
  createDeleteTool(workspaceRoot),
  createMkdirTool(workspaceRoot),
  createSearchTool(workspaceRoot),
  createGlobTool(workspaceRoot),
  createDiffTool(workspaceRoot)
];
