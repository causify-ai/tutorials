import { describe, expect, it, vi } from 'vitest';
import {
  buildNotebookTools,
  createNotebook,
  patchNotebook,
  listNotebookArtifacts,
  summarizeNotebook
} from './notebook.js';
import path from 'path';
import { promises as fs } from 'fs';

vi.mock('child_process', () => ({
  spawn: vi.fn(() => ({
    stdout: { on: (_evt: string, handler: (chunk: string) => void) => handler('{"status":"ok"}') },
    stderr: { on: () => {} },
    on: (event: string, handler: (code: number) => void) => {
      if (event === 'close') handler(0);
    }
  }))
}));

const root = process.cwd();

describe('notebook tools', () => {
  it('builds notebook tools array', () => {
    const tools = buildNotebookTools(root);
    expect(tools.length).toBe(5);
  });

  it('creates a notebook from sections JSON', async () => {
    const output = path.join('tmp', 'test-notebook.ipynb');
    const sections = [{ title: 'Test', code: "print('ok')" }];
    const result = await createNotebook(root, sections, output);
    expect(result.message).toContain('Notebook created');
    await fs.rm(path.resolve(root, output), { force: true });
  });

  it('patches a notebook by replacing a cell', async () => {
    const tempDir = path.join(root, 'tmp', 'patch-tests');
    await fs.mkdir(tempDir, { recursive: true });
    const notebookPath = path.join(tempDir, 'inline.ipynb');
    const sample = {
      cells: [{ cell_type: 'markdown', source: 'Hello world' }],
      metadata: {},
      nbformat: 4,
      nbformat_minor: 5
    };
    await fs.writeFile(notebookPath, JSON.stringify(sample, null, 2));
    await patchNotebook(root, notebookPath, [
      { action: 'replace', cellIndex: 0, newSource: 'Updated content' }
    ]);
    const patched = JSON.parse(await fs.readFile(notebookPath, 'utf8'));
    expect(patched.cells[0].source).toBe('Updated content');
  });

  it('describes notebook artifacts even when missing', async () => {
    const tempDir = path.join(root, 'tmp', 'artifacts-tests');
    await fs.mkdir(tempDir, { recursive: true });
    const executedPath = path.join(tempDir, 'demo.ipynb');
    await fs.writeFile(executedPath, JSON.stringify({ cells: [], metadata: {}, nbformat: 4, nbformat_minor: 5 }));
    const result = await listNotebookArtifacts(root, executedPath);
    expect(result.message).toContain('No artifacts directory');
  });

  it('summarizes notebook without throwing', async () => {
    const tempDir = path.join(root, 'tmp', 'summary-tests');
    await fs.mkdir(tempDir, { recursive: true });
    const notebookPath = path.join(tempDir, 'summary.ipynb');
    const nb = { cells: [], metadata: {}, nbformat: 4, nbformat_minor: 5 };
    await fs.writeFile(notebookPath, JSON.stringify(nb));
    const result = await summarizeNotebook(root, notebookPath, { includeMarkdown: false });
    expect(result.message).toContain('Notebook summary');
  });
});
