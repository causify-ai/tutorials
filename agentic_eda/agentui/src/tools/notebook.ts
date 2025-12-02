import path from 'path';
import os from 'os';
import crypto from 'node:crypto';
import { promises as fs } from 'fs';
import { existsSync } from 'fs';
import { spawn } from 'child_process';
import { tool } from 'langchain';
import { z } from 'zod';
import { requireWorkspacePath } from '../path/resolver.js';
import { analyzeImagePath } from './vision.js';
import { fileURLToPath } from 'url';

const PYTHON_BIN = process.env.AGEN_TUI_PYTHON ?? 'python3';
const AUTO_ANALYZE_IMAGES = process.env.AGEN_TUI_AUTO_ANALYZE_IMAGES === '1';
const parseAnalyzerCaption = (raw: string) => {
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed.caption === 'string') {
      return parsed.caption;
    }
  } catch {
    // ignore
  }
  return raw;
};

type NotebookArtifact = { cell: number; path: string; mimetype?: string; analysis?: string };
type RunnerMetadata = {
  run_id?: string;
  attempts?: number;
  max_retries?: number;
  allow_errors?: boolean;
  started_at?: string;
  finished_at?: string;
  python_version?: string;
  matplotlib_backend?: string | null;
  artifact_dir?: string;
  last_exception?: string | null;
  artifact_captions?: Array<{ path: string; caption: string }>;
};

type RunnerResult = {
  status: 'ok' | 'error';
  action?: string;
  path?: string;
  output?: string;
  artifacts?: NotebookArtifact[];
  errors?: Array<{ cell: number; ename?: string; evalue?: string; traceback?: string[] }>;
  summary?: Array<{ cell: number; type: string; preview: string }>;
  metadata?: RunnerMetadata;
  message?: string;
};

const packageRoot = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..', '..');

const resolveRunnerScript = (workspaceRoot: string) => {
  const workspaceRunner = path.join(workspaceRoot, 'scripts/ipynb/runner.py');
  if (existsSync(workspaceRunner)) {
    return workspaceRunner;
  }
  const packagedRunner = path.join(packageRoot, 'scripts/ipynb/runner.py');
  if (existsSync(packagedRunner)) {
    return packagedRunner;
  }
  throw new Error(
    'Notebook runner script is missing. Ensure scripts/ipynb/runner.py exists in the workspace or package.'
  );
};

const runRunner = async (workspaceRoot: string, args: string[]): Promise<RunnerResult> => {
  const scriptPath = resolveRunnerScript(workspaceRoot);
  return new Promise<RunnerResult>((resolve, reject) => {
    const child = spawn(PYTHON_BIN, [scriptPath, ...args], { cwd: workspaceRoot });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `Runner exited with code ${code}`));
        return;
      }
      try {
        resolve(JSON.parse(stdout.trim() || '{}'));
      } catch (error) {
        reject(new Error(`Failed to parse runner output: ${stdout}`));
      }
    });
  });
};

const normalizeSections = (sections: unknown) => {
  if (typeof sections === 'string') {
    try {
      return JSON.parse(sections);
    } catch {
      const lines = sections.split('\n').filter(Boolean);
      return lines.map((line: string, idx: number) => ({ title: line.trim() || `Section ${idx + 1}` }));
    }
  }
  return sections;
};

export const createNotebook = async (workspaceRoot: string, sections: unknown, outputPath: string) => {
  const normalizedSections = normalizeSections(sections);
  const planSchema = z.array(z.object({ title: z.string(), code: z.string().optional() }));
  const parsedPlan = planSchema.parse(normalizedSections);
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'agentui-plan-'));
  const planPath = path.join(tmpDir, 'plan.json');
  await fs.writeFile(planPath, JSON.stringify(parsedPlan, null, 2));
  const resolvedOutput = requireWorkspacePath(workspaceRoot, outputPath).absolute;
  await fs.mkdir(path.dirname(resolvedOutput), { recursive: true });
  const result = await runRunner(workspaceRoot, ['create', '--plan', planPath, '--output', resolvedOutput]);
  if (result.status !== 'ok') {
    throw new Error(result.message ?? 'Notebook creation failed');
  }
  return { message: `Notebook created at ${resolvedOutput}.`, raw: JSON.stringify(result) };
};

const createNotebookTool = (workspaceRoot: string) =>
  tool(
    async ({ sections, outputPath }: { sections: unknown; outputPath: string }) => {
      const result = await createNotebook(workspaceRoot, sections, outputPath);
      return `${result.message} Details: ${result.raw}`;
    },
    {
      name: 'ipynb_create',
      description: 'Create a Jupyter notebook from a structured plan (title + optional code per section).',
      schema: z.object({
        sections: z.union([z.string(), z.array(z.object({ title: z.string(), code: z.string().optional() }))]).describe(
          'Plan describing sections/cells. Either JSON array or newline-separated outline.'
        ),
        outputPath: z.string().describe('Target notebook path (relative to workspace).')
      })
    }
  );

const MAX_NOTEBOOK_RETRIES = Number(process.env.AGEN_TUI_NOTEBOOK_MAX_RETRIES ?? '2');
const analyzeArtifacts = async (workspaceRoot: string, artifacts: NotebookArtifact[] | undefined) => {
  if (!AUTO_ANALYZE_IMAGES || !artifacts?.length) {
    return { artifacts: artifacts ?? [], captions: [] as Array<{ path: string; caption: string }> };
  }
  const augmented: NotebookArtifact[] = [];
  const captions: Array<{ path: string; caption: string }> = [];
  for (const artifact of artifacts) {
    const entry: NotebookArtifact = { ...artifact };
    try {
      const raw = await analyzeImagePath(workspaceRoot, artifact.path);
      const caption = parseAnalyzerCaption(raw);
      entry.analysis = caption;
      captions.push({ path: artifact.path, caption });
    } catch (error) {
      entry.analysis = error instanceof Error ? error.message : String(error);
    }
    augmented.push(entry);
  }
  return { artifacts: augmented, captions };
};

export type NotebookRunResult = {
  message: string;
  raw: string;
  metadata?: RunnerMetadata;
  artifacts: NotebookArtifact[];
  errors: RunnerResult['errors'] | undefined;
};

export const runNotebook = async (
  workspaceRoot: string,
  inputPath: string,
  outputPath: string,
  options: { allowErrors?: boolean; runId?: string } = {}
): Promise<NotebookRunResult> => {
  const resolvedInput = requireWorkspacePath(workspaceRoot, inputPath).absolute;
  const resolvedOutput = requireWorkspacePath(workspaceRoot, outputPath).absolute;
  await fs.mkdir(path.dirname(resolvedOutput), { recursive: true });
  const runId = options.runId ?? crypto.randomUUID();
  const runnerArgs = [
    'run',
    '--input',
    resolvedInput,
    '--output',
    resolvedOutput,
    '--workspace-root',
    workspaceRoot,
    '--max-retries',
    String(Math.max(1, MAX_NOTEBOOK_RETRIES)),
    '--run-id',
    runId
  ];
  if (options.allowErrors) {
    runnerArgs.push('--allow-errors');
  }
  const result = await runRunner(workspaceRoot, runnerArgs);
  if (result.status !== 'ok') {
    throw new Error(result.message ?? 'Notebook execution failed');
  }
  const errorCount = result.errors?.length ?? 0;
  const { artifacts: analyzedArtifacts, captions } = await analyzeArtifacts(workspaceRoot, result.artifacts);
  const artifactCount = analyzedArtifacts.length;
  const runLabel = result.metadata?.run_id ? `Run ${result.metadata.run_id}` : 'Notebook run';
  const summaryParts = [
    `${errorCount} error${errorCount === 1 ? '' : 's'}`,
    `${artifactCount} artifact${artifactCount === 1 ? '' : 's'}`
  ];
  const artifactList = analyzedArtifacts.length
    ? `Artifacts: ${analyzedArtifacts.map((artifact) => path.basename(artifact.path)).join(', ')}. `
    : '';
  const captionSnippets = captions
    .filter(({ caption }) => caption && caption.trim().length)
    .slice(0, 2)
    .map(({ path: artifactPath, caption }) => `${path.basename(artifactPath)} – ${caption}`);
  const extraCaptionText =
    captionSnippets.length > 0
      ? `Artifact captions: ${captionSnippets.join('; ')}${captions.length > captionSnippets.length ? '; …' : ''}. `
      : '';
  const message = `${runLabel}: ${summaryParts.join(', ')}. ${artifactList}${extraCaptionText}Results saved to ${resolvedOutput}.`;
  return {
    message,
    raw: JSON.stringify({ ...result, artifacts: analyzedArtifacts }),
    metadata: { ...result.metadata, artifact_captions: captions },
    artifacts: analyzedArtifacts,
    errors: result.errors
  };
};

const runNotebookTool = (workspaceRoot: string) =>
  tool(
    async ({ inputPath, outputPath, allowErrors }: { inputPath: string; outputPath: string; allowErrors?: boolean }) => {
      const result = await runNotebook(workspaceRoot, inputPath, outputPath, { allowErrors });
      return `${result.message} Raw response: ${result.raw}`;
    },
    {
      name: 'ipynb_run',
      description: 'Execute a notebook and capture outputs/artifacts.',
      schema: z.object({
        inputPath: z.string().describe('Path to the source notebook.'),
        outputPath: z.string().describe('Path to write the executed notebook (nbclient output).'),
        allowErrors: z
          .boolean()
          .optional()
          .describe('Set true to keep executing even if cells raise errors (gathers all tracebacks).')
      })
    }
  );

export const summarizeNotebook = async (
  workspaceRoot: string,
  inputPath: string,
  options: { includeMarkdown?: boolean; includeCode?: boolean; maxCells?: number } = {}
) => {
  const resolvedInput = requireWorkspacePath(workspaceRoot, inputPath).absolute;
  const result = await runRunner(workspaceRoot, ['summarize', '--input', resolvedInput]);
  if (result.status !== 'ok') {
    throw new Error(result.message ?? 'Notebook summarize failed');
  }
  const includeMarkdown = options.includeMarkdown !== false;
  const includeCode = options.includeCode !== false;
  const summaries = (result.summary ?? []).filter((cell) => {
    if (cell.type === 'markdown' && !includeMarkdown) return false;
    if (cell.type === 'code' && !includeCode) return false;
    return true;
  });
  const limited = typeof options.maxCells === 'number' ? summaries.slice(0, options.maxCells) : summaries;
  return { message: `Notebook summary for ${resolvedInput}`, raw: JSON.stringify(limited) };
};

const analyzeNotebookTool = (workspaceRoot: string) =>
  tool(
    async ({
      inputPath,
      includeMarkdown,
      includeCode,
      maxCells
    }: {
      inputPath: string;
      includeMarkdown?: boolean;
      includeCode?: boolean;
      maxCells?: number;
    }) => {
      const result = await summarizeNotebook(workspaceRoot, inputPath, {
        includeMarkdown,
        includeCode,
        maxCells
      });
      return `${result.message}: ${result.raw}`;
    },
    {
      name: 'ipynb_analyze',
      description: 'Summarize notebook cells (type + preview).',
      schema: z.object({
        inputPath: z.string().describe('Notebook to summarize.'),
        includeMarkdown: z.boolean().optional().describe('Include markdown cells (default true).'),
        includeCode: z.boolean().optional().describe('Include code cells (default true).'),
        maxCells: z.number().int().positive().optional().describe('Limit number of cells in the summary.')
      })
    }
  );

type NotebookCell = {
  cell_type: 'markdown' | 'code';
  source: string | string[];
  metadata?: Record<string, unknown>;
  outputs?: unknown[];
  execution_count?: number | null;
};

type NotebookFile = {
  cells: NotebookCell[];
  metadata?: Record<string, unknown>;
  nbformat: number;
  nbformat_minor: number;
};

const normalizeSource = (source: string | string[] | undefined): string => {
  if (!source) return '';
  if (typeof source === 'string') return source;
  return source.join('');
};

const resetCodeCellState = (cell: NotebookCell) => {
  if (cell.cell_type === 'code') {
    cell.outputs = [];
    cell.execution_count = null;
  }
};

const instructionSchema = z
  .object({
    action: z.enum(['replace', 'insert_after', 'delete']),
    cellIndex: z.number().int().nonnegative().optional(),
    match: z.string().optional(),
    newSource: z.string().optional(),
    newCell: z
      .object({
        cell_type: z.enum(['markdown', 'code']),
        source: z.string()
      })
      .optional()
  })
  .refine((value) => typeof value.cellIndex === 'number' || typeof value.match === 'string', {
    message: 'Provide either cellIndex or match to identify the target cell.'
  });

export type NotebookEditInstruction = z.infer<typeof instructionSchema>;

const findCellIndex = (cells: NotebookCell[], instruction: NotebookEditInstruction) => {
  if (typeof instruction.cellIndex === 'number') {
    const idx = instruction.cellIndex;
    if (idx < 0 || idx >= cells.length) {
      throw new Error(`Cell index ${idx} is out of range`);
    }
    return idx;
  }
  if (instruction.match) {
    const idx = cells.findIndex((cell) => normalizeSource(cell.source).includes(instruction.match ?? ''));
    if (idx >= 0) {
      return idx;
    }
  }
  throw new Error('Unable to locate target cell for instruction');
};

const buildCell = (config: NonNullable<NotebookEditInstruction['newCell']>): NotebookCell => {
  if (config.cell_type === 'code') {
    return {
      cell_type: 'code',
      source: config.source,
      metadata: {},
      outputs: [],
      execution_count: null
    };
  }
  return {
    cell_type: 'markdown',
    source: config.source,
    metadata: {}
  };
};

export const patchNotebook = async (
  workspaceRoot: string,
  inputPath: string,
  instructions: NotebookEditInstruction[],
  outputPath?: string
) => {
  const resolvedInput = requireWorkspacePath(workspaceRoot, inputPath).absolute;
  const resolvedOutput = outputPath
    ? requireWorkspacePath(workspaceRoot, outputPath).absolute
    : resolvedInput;
  const raw = await fs.readFile(resolvedInput, 'utf8');
  const notebook = JSON.parse(raw) as NotebookFile;
  if (!Array.isArray(notebook.cells)) {
    throw new Error('Notebook is missing cells array');
  }
  const applied: string[] = [];
  instructions.forEach((instruction, index) => {
    const parsed = instructionSchema.parse(instruction);
    switch (parsed.action) {
      case 'replace': {
        const targetIdx = findCellIndex(notebook.cells, parsed);
        const target = notebook.cells[targetIdx];
        if (!parsed.newSource) {
          throw new Error(`Instruction ${index} missing newSource for replace action`);
        }
        notebook.cells[targetIdx] = {
          ...target,
          source: parsed.newSource
        };
        resetCodeCellState(notebook.cells[targetIdx]);
        applied.push(`Replaced cell ${targetIdx}`);
        break;
      }
      case 'insert_after': {
        if (!parsed.newCell) {
          throw new Error(`Instruction ${index} missing newCell for insert`);
        }
        const targetIdx = findCellIndex(notebook.cells, parsed);
        const newCell = buildCell(parsed.newCell);
        notebook.cells.splice(targetIdx + 1, 0, newCell);
        applied.push(`Inserted cell after ${targetIdx}`);
        break;
      }
      case 'delete': {
        const targetIdx = findCellIndex(notebook.cells, parsed);
        notebook.cells.splice(targetIdx, 1);
        applied.push(`Deleted cell ${targetIdx}`);
        break;
      }
      default:
        throw new Error(`Unsupported action ${parsed.action}`);
    }
  });
  await fs.writeFile(resolvedOutput, JSON.stringify(notebook, null, 1));
  return { message: `Patched notebook ${resolvedOutput}`, applied };
};

const patchNotebookTool = (workspaceRoot: string) =>
  tool(
    async ({
      inputPath,
      outputPath,
      instructions
    }: {
      inputPath: string;
      outputPath?: string;
      instructions: NotebookEditInstruction[];
    }) => {
      const result = await patchNotebook(workspaceRoot, inputPath, instructions, outputPath);
      return `${result.message}. Applied edits: ${result.applied.join(', ')}`;
    },
    {
      name: 'ipynb_patch',
      description: 'Modify notebook cells by replacing, inserting, or deleting code/markdown.',
      schema: z.object({
        inputPath: z.string().describe('Existing notebook to patch.'),
        outputPath: z.string().optional().describe('Where to write the patched notebook. Defaults to the input file.'),
        instructions: z.array(instructionSchema).describe('List of edits to apply sequentially.')
      })
    }
  );

const describeArtifacts = async (baseDir: string) => {
  try {
    const entries = await fs.readdir(baseDir, { withFileTypes: true });
    return entries;
  } catch {
    return null;
  }
};

const formatArtifactList = async (artifactRoot: string, limit = 5) => {
  const runs = await describeArtifacts(artifactRoot);
  if (!runs || !runs.length) {
    return 'No artifacts recorded.';
  }
  const runSummaries: string[] = [];
  for (const dirent of runs) {
    if (!dirent.isDirectory()) continue;
    const runDir = path.join(artifactRoot, dirent.name);
    const files = await fs.readdir(runDir);
    const images = files.filter((file) => /\.(png|jpg|jpeg)$/i.test(file));
    runSummaries.push(`${dirent.name}: ${images.length ? images.join(', ') : 'no images'}`);
    if (runSummaries.length >= limit) break;
  }
  return runSummaries.length ? runSummaries.join('\n') : 'No artifacts recorded.';
};

export const listNotebookArtifacts = async (workspaceRoot: string, executedPath: string, options: { limit?: number } = {}) => {
  const resolved = requireWorkspacePath(workspaceRoot, executedPath).absolute;
  const baseDir = resolved.replace(/\.ipynb$/, '');
  const artifactRoot = path.join(baseDir, 'artifacts');
  const exists = await describeArtifacts(artifactRoot);
  if (!exists) {
    return {
      message: `No artifacts directory found for ${baseDir}. Run the notebook to generate artifacts.`,
      listings: []
    };
  }
  const summary = await formatArtifactList(artifactRoot, options.limit ?? 5);
  return {
    message: `Artifacts for ${baseDir}:\n${summary}`,
    listings: summary.split('\n')
  };
};

const artifactNotebookTool = (workspaceRoot: string) =>
  tool(
    async ({ executedPath, limit }: { executedPath: string; limit?: number }) => {
      const result = await listNotebookArtifacts(workspaceRoot, executedPath, { limit });
      return result.message;
    },
    {
      name: 'ipynb_artifacts',
      description: 'List saved artifact files for an executed notebook.',
      schema: z.object({
        executedPath: z.string().describe('Path to the executed notebook (.ipynb).'),
        limit: z.number().int().positive().optional().describe('How many run directories to summarize (default 5).')
      })
    }
  );

export const buildNotebookTools = (workspaceRoot: string) => [
  createNotebookTool(workspaceRoot),
  runNotebookTool(workspaceRoot),
  analyzeNotebookTool(workspaceRoot),
  patchNotebookTool(workspaceRoot),
  artifactNotebookTool(workspaceRoot)
];
