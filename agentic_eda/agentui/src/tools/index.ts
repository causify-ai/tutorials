import { buildFilesystemTools } from './filesystem.js';
import { buildNotebookTools } from './notebook.js';
import { buildImageTools } from './vision.js';

export const buildTools = (workspaceRoot: string) => {
  return [...buildFilesystemTools(workspaceRoot), ...buildNotebookTools(workspaceRoot), ...buildImageTools(workspaceRoot)];
};
