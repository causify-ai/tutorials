import fs from 'fs/promises';
import path from 'path';
import { requireWorkspacePath } from '../path/resolver.js';

export type ImageAttachment = {
  path: string;
  mime: string;
  dataUrl: string;
};

const IMAGE_EXTS = new Set(['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']);

const extToMime = (ext: string): string => {
  switch (ext) {
    case '.png':
      return 'image/png';
    case '.jpg':
    case '.jpeg':
      return 'image/jpeg';
    case '.webp':
      return 'image/webp';
    case '.gif':
      return 'image/gif';
    case '.bmp':
      return 'image/bmp';
    default:
      return 'application/octet-stream';
  }
};

export const isImagePath = (filePath: string) => IMAGE_EXTS.has(path.extname(filePath).toLowerCase());

export const loadImageAttachments = async (
  workspaceRoot: string,
  filePaths: string[]
): Promise<ImageAttachment[]> => {
  const attachments: ImageAttachment[] = [];
  for (const filePath of filePaths) {
    try {
      const resolved = requireWorkspacePath(workspaceRoot, filePath);
      const absolute = resolved.absolute;
      if (!isImagePath(absolute)) continue;
      const stat = await fs.stat(absolute);
      if (!stat.isFile()) continue;
      const data = await fs.readFile(absolute);
      const ext = path.extname(absolute).toLowerCase();
      const mime = extToMime(ext);
      attachments.push({
        path: absolute,
        mime,
        dataUrl: `data:${mime};base64,${data.toString('base64')}`
      });
    } catch {
      // Ignore failures; missing/non-readable files simply won't be attached.
    }
  }
  return attachments;
};
