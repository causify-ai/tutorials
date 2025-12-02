import { describe, expect, it } from 'vitest';
import { renderComposerView } from './composer-renderer.js';

describe('renderComposerView', () => {
  it('renders deterministic viewport for wall-of-text paste', () => {
    const text =
      'Paste-heavy output should wrap predictably even when the entire payload is dropped into the composer in one go.';
    const view = renderComposerView(text, text.length, 24);
    expect(view.ascii.join('\n')).toMatchInlineSnapshot(`
"Paste-heavy output shoul
d wrap predictably even 
when the entire payload 
is dropped into the comp
oser in one go.< >         "
`);
  });

  it('keeps stray pipes aligned while scrolling', () => {
    const text = ['cat input.log |', '  grep ERROR |', '  sort |', '  uniq -c'].join('\n');
    const view = renderComposerView(text, text.length, 20);
    expect(view.ascii.join('\n')).toMatchInlineSnapshot(`
"cat input.log |     
  grep ERROR |      
  sort |            
  uniq -c< >           "
`);
  });

  it('produces stable snapshots for repeated arrow navigation', () => {
    const lines = Array.from({ length: 12 }, (_, idx) => `line ${String(idx + 1).padStart(2, '0')} for QA`);
    const block = lines.join('\n');
    const cursorPositions: number[] = [];
    let offset = 0;
    lines.forEach((line) => {
      offset += line.length;
      cursorPositions.push(offset);
      offset += 1;
    });
    const snapshots = cursorPositions
      .slice(-8)
      .reverse()
      .map((cursor) => renderComposerView(block, cursor, 26).ascii.join('\n'));
    expect(snapshots.join('\n---\n')).toMatchInlineSnapshot(`
"^^^
line 07 for QA            
line 08 for QA            
line 09 for QA            
line 10 for QA            
line 11 for QA            
line 12 for QA< >            
---
^^^
line 06 for QA            
line 07 for QA            
line 08 for QA            
line 09 for QA            
line 10 for QA            
line 11 for QA< >            
vvv
---
^^^
line 05 for QA            
line 06 for QA            
line 07 for QA            
line 08 for QA            
line 09 for QA            
line 10 for QA< >            
vvv
---
^^^
line 04 for QA            
line 05 for QA            
line 06 for QA            
line 07 for QA            
line 08 for QA            
line 09 for QA< >            
vvv
---
^^^
line 03 for QA            
line 04 for QA            
line 05 for QA            
line 06 for QA            
line 07 for QA            
line 08 for QA< >            
vvv
---
^^^
line 02 for QA            
line 03 for QA            
line 04 for QA            
line 05 for QA            
line 06 for QA            
line 07 for QA< >            
vvv
---
line 01 for QA            
line 02 for QA            
line 03 for QA            
line 04 for QA            
line 05 for QA            
line 06 for QA< >            
vvv
---
line 01 for QA            
line 02 for QA            
line 03 for QA            
line 04 for QA            
line 05 for QA< >            
line 06 for QA            
vvv"
`);
  });

  it('normalizes carriage returns and tabs before computing layout', () => {
    const text = 'foo\rbar\tbaz\r\nfinal';
    const view = renderComposerView(text, text.length, 12);
    expect(view.ascii.join('\n')).toMatchInlineSnapshot(`
"foo         
bar  baz    
final< >       "
`);
  });

  it('handles sprint summary paste with stray carriage returns without breaking viewport', () => {
    const snippet = [
      '"  - Removed the unused countLines helper so npm run typecheck stays clean',
      '    (src/utils/tool-summaries.ts:104-149 now flows directly from formatPath',
      '    into the summarizers).',
      '  - Documented the new behavior/QA steps in both README.md (highlights +',
      '    QA checklist; README.md:12, README.md:50, README.md:134-140) and docs/',
      '    STATE.md (docs/STATE.md:7-22). Updated the Sprint 7 plan to show what’s',
      '    done and left (sprint_markdowns/sprint7_plan.md:1-16)."'
    ].join('\r');
    const view = renderComposerView(snippet, snippet.length, 52);
    expect(view.ascii.join('\n')).toMatchInlineSnapshot(`
"^^^
    QA checklist; README.md:12, README.md:50, README
.md:134-140) and docs/                              
    STATE.md (docs/STATE.md:7-22). Updated the Sprin
t 7 plan to show what’s                             
    done and left (sprint_markdowns/sprint7_plan.md:
1-16).\"< >                                             "
`);
  });
});
