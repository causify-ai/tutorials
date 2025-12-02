import fs from 'node:fs';

const TIP_DOC_URL = new URL('../../docs/NOTEBOOK_BEST_PRACTICES.md', import.meta.url);

export const NOTEBOOK_BEST_PRACTICES = fs.readFileSync(TIP_DOC_URL, 'utf8').trim();
