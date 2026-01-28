import type { MessageAction } from '../state/session.js';
export const formatActionSummary = (action: MessageAction) => {
  const symbol = action.status === 'running' ? '…' : action.status === 'success' ? '✓' : '!';
  const detail = action.detail?.trim();
  const label = detail && detail.length ? detail : action.name.replace(/_/g, ' ');
  return `${symbol} ${label}`;
};

export const formatActionDigest = (actions: MessageAction[]) => {
  if (!actions.length) return '';
  const summaries = actions
    .filter((action) => action.status === 'success')
    .map((action) => {
      const detail = action.detail?.trim();
      const label = detail && detail.length ? detail : action.name.replace(/_/g, ' ');
      return `- ${label}`;
    });
  if (!summaries.length) {
    return '';
  }
  return `Completed actions (latest first):\n${summaries.slice(-5).join('\n')}`;
};
