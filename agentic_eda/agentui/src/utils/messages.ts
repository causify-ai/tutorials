const VISIBILITY_REGEX = /^\s*ReasoningVisible:\s*(yes|no)\s*/i;
const ACTIONS_REGEX = /Actions:\s*/i;
const ANSWER_REGEX = /Answer:\s*/i;

export const stripReasoningVisibilityLine = (
  text: string
): { text: string; visible?: boolean } => {
  if (!text) {
    return { text: '', visible: undefined };
  }
  const match = VISIBILITY_REGEX.exec(text);
  if (!match) {
    return { text, visible: undefined };
  }
  const visible = match[1].toLowerCase() === 'yes';
  const remainder = text.slice(match[0].length).replace(/^\s*/, '');
  return { text: remainder, visible };
};

const dedupeLines = (text: string) => {
  const lines = text.split('\n');
  const result: string[] = [];
  lines.forEach((line) => {
    const last = result[result.length - 1];
    if (last === line) {
      return;
    }
    if (!line.trim() && !last?.trim()) {
      return;
    }
    result.push(line);
  });
  return result.join('\n').replace(/\n{3,}/g, '\n\n').trim();
};

export const splitReasoningAndAnswer = (raw: string) => {
  if (!raw) {
    return { reasoning: '', answer: '' };
  }
  const { text, visible } = stripReasoningVisibilityLine(raw);
  const answerMatch = ANSWER_REGEX.exec(text);
  if (!answerMatch) {
    return { reasoning: '', answer: text.trim(), visible };
  }
  const answer = text.slice(answerMatch.index + answerMatch[0].length).trim();
  const beforeAnswer = text.slice(0, answerMatch.index).trim();
  const actionsIndex = beforeAnswer.search(ACTIONS_REGEX);
  const reasoning =
    actionsIndex === -1
      ? beforeAnswer
      : beforeAnswer.slice(0, actionsIndex).trim();
  return { reasoning: dedupeLines(reasoning), answer, visible };
};
