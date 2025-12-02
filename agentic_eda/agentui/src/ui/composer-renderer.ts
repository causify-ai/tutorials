import stringWidth from 'string-width';

export const COMPOSER_VIEWPORT_ROWS = 6;
const CONTROL_REGEX = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g;

export type DisplayLine = {
  start: number;
  end: number;
  columns: number[];
};

export type ComposerRenderResult = {
  displayLines: DisplayLine[];
  visibleLines: DisplayLine[];
  clippedTop: boolean;
  clippedBottom: boolean;
  cursorRow: number;
  cursorColumn: number;
  scrollRow: number;
  totalLines: number;
  ascii: string[];
};

const FALLBACK_LINE: DisplayLine = { start: 0, end: 0, columns: [0] };

export const sanitizeComposerText = (input: string): string => {
  if (!input) return '';
  return input
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(/\u2028|\u2029/g, '\n')
    .replace(/\t/g, '  ')
    .replace(CONTROL_REGEX, '');
};

export const renderComposerView = (
  rawValue: string,
  rawCursor: number,
  rawWidth: number
): ComposerRenderResult => {
  const value = sanitizeComposerText(rawValue ?? '');
  const safeWidth =
    Number.isFinite(rawWidth) && rawWidth > 0 ? Math.floor(rawWidth) : 1;
  const displayLines = buildDisplayLines(value, safeWidth);
  const totalLines = displayLines.length || 1;
  const clampedCursor = clamp(rawCursor ?? 0, 0, value.length);
  const cursorRow = findCursorRow(displayLines, clampedCursor);
  const cursorLine = displayLines[cursorRow] ?? FALLBACK_LINE;
  const relativeIndex = clamp(
    clampedCursor - cursorLine.start,
    0,
    cursorLine.columns.length - 1
  );
  const cursorColumn = cursorLine.columns[relativeIndex] ?? 0;
  const scrollRow = computeScrollRow(cursorRow, totalLines);
  const visibleLines = (
    displayLines.slice(scrollRow, scrollRow + COMPOSER_VIEWPORT_ROWS) ||
    []
  ).filter(Boolean);
  if (!visibleLines.length) {
    visibleLines.push(FALLBACK_LINE);
  }
  const clippedTop = scrollRow > 0;
  const clippedBottom =
    totalLines > COMPOSER_VIEWPORT_ROWS &&
    scrollRow + COMPOSER_VIEWPORT_ROWS < totalLines;
  const ascii: string[] = [];
  if (clippedTop) {
    ascii.push('^^^');
  }
  visibleLines.forEach((line) => {
    ascii.push(renderAsciiLine(value, line, clampedCursor, safeWidth));
  });
  if (clippedBottom) {
    ascii.push('vvv');
  }
  if (!ascii.length) {
    ascii.push(renderAsciiLine(value, FALLBACK_LINE, clampedCursor, safeWidth));
  }
  return {
    displayLines,
    visibleLines,
    clippedTop,
    clippedBottom,
    cursorRow,
    cursorColumn,
    scrollRow,
    totalLines,
    ascii
  };
};

const clamp = (value: number, min: number, max: number) => {
  if (Number.isNaN(value)) return min;
  if (value < min) return min;
  if (value > max) return max;
  return value;
};

const computeScrollRow = (cursorRow: number, totalLines: number) => {
  if (totalLines <= COMPOSER_VIEWPORT_ROWS) {
    return 0;
  }
  const maxScroll = totalLines - COMPOSER_VIEWPORT_ROWS;
  const desiredStart = cursorRow - (COMPOSER_VIEWPORT_ROWS - 1);
  return clamp(desiredStart, 0, maxScroll);
};

const findCursorRow = (lines: DisplayLine[], cursor: number) => {
  if (!lines.length) return 0;
  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx];
    if (cursor <= line.end) {
      return idx;
    }
  }
  return Math.max(lines.length - 1, 0);
};

const renderAsciiLine = (
  value: string,
  line: DisplayLine,
  cursor: number,
  width: number
) => {
  const lineText = value.slice(line.start, line.end);
  const cursorWithin = cursor >= line.start && cursor <= line.end;
  const padWidth = Math.max(0, width - stringWidth(lineText));
  if (!cursorWithin) {
    return `${lineText}${' '.repeat(padWidth)}`;
  }
  const afterFull = value.slice(cursor);
  const isNewlineCursor = afterFull.startsWith('\n');
  const cursorChar =
    isNewlineCursor || afterFull.length === 0 ? ' ' : afterFull[0] ?? ' ';
  const consumed = afterFull.length > 0 ? 1 : 0;
  const before = value.slice(line.start, cursor);
  const after = value.slice(cursor + consumed, line.end);
  return `${before}<${cursorChar}>${after}${' '.repeat(padWidth)}`;
};

const buildDisplayLines = (text: string, width: number): DisplayLine[] => {
  const wrapLimit = width > 0 ? width : Number.POSITIVE_INFINITY;
  const lines: DisplayLine[] = [];
  let currentStart = 0;
  let currentWidth = 0;
  let idx = 0;
  let columns: number[] = [0];

  const pushLine = (endIndex: number) => {
    lines.push({ start: currentStart, end: endIndex, columns });
    currentStart = endIndex;
    currentWidth = 0;
    columns = [0];
  };

  while (idx < text.length) {
    const codePoint = text.codePointAt(idx);
    if (codePoint === undefined) {
      break;
    }
    const char = String.fromCodePoint(codePoint);
    const charLen = char.length;

    if (char === '\n') {
      pushLine(idx);
      idx += charLen;
      currentStart = idx;
      continue;
    }

    const charWidth = Math.max(1, stringWidth(char));

    if (
      Number.isFinite(wrapLimit) &&
      currentWidth + charWidth > wrapLimit &&
      columns.length > 1
    ) {
      pushLine(idx);
      continue;
    }

    currentWidth += charWidth;
    columns.push(currentWidth);
    idx += charLen;
  }

  pushLine(text.length);

  if (lines.length === 0) {
    lines.push(FALLBACK_LINE);
  }

  return lines;
};
