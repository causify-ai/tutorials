export type SlashCommand =
  | { type: 'model'; value?: string }
  | { type: 'new' }
  | { type: 'undo' }
  | { type: 'files' }
  | { type: 'quit' }
  | { type: 'exit' };

export const parseSlashCommand = (input: string): SlashCommand | null => {
  const trimmed = input.trim();
  if (!trimmed.startsWith('/')) return null;
  const [cmd, ...rest] = trimmed.slice(1).split(/\s+/);
  const value = rest.join(' ').trim() || undefined;
  switch (cmd.toLowerCase()) {
    case 'model':
      return { type: 'model', value };
    case 'new':
      return { type: 'new' };
    case 'undo':
      return { type: 'undo' };
    case 'files':
      return { type: 'files' };
    case 'quit':
      return { type: 'quit' };
    case 'exit':
      return { type: 'exit' };
    default:
      return null;
  }
};
