export const summarizeText = (value: string, max = 160): string => {
  if (!value) return '';
  const clean = value.replace(/\s+/g, ' ').trim();
  if (!clean) return '';
  return clean.length > max ? `${clean.slice(0, max)}…` : clean;
};

const extractText = (value: unknown): string | null => {
  if (value == null) return null;
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    for (const item of value) {
      const result = extractText(item);
      if (result) return result;
    }
    return null;
  }
  if (typeof value === 'object') {
    if ('text' in (value as Record<string, unknown>) && typeof (value as { text?: unknown }).text === 'string') {
      return (value as { text: string }).text;
    }
    if ('content' in (value as Record<string, unknown>)) {
      const nested = extractText((value as { content?: unknown }).content);
      if (nested) return nested;
    }
  }
  return null;
};

const extractLangChainContent = (payload: unknown): string | null => {
  const candidates = Array.isArray(payload) ? payload : [payload];
  for (const candidate of candidates) {
    if (!candidate || typeof candidate !== 'object') {
      continue;
    }
    const record = candidate as Record<string, unknown>;
    if (typeof record.content === 'string') {
      return record.content;
    }
    if (record.kwargs && typeof record.kwargs === 'object') {
      const nested = extractText((record.kwargs as { content?: unknown }).content);
      if (nested) {
        return nested;
      }
    }
  }
  return null;
};

const stringifyPayload = (payload: unknown): string => {
  if (payload == null) return '';
  if (typeof payload === 'string') {
    return payload;
  }
  const langchainContent = extractLangChainContent(payload);
  if (langchainContent) {
    return langchainContent;
  }
  if (typeof payload === 'object') {
    try {
      return JSON.stringify(payload);
    } catch {
      return '[unserializable payload]';
    }
  }
  return String(payload);
};

export const formatToolDetail = (payload: unknown, max = 160): string => {
  const raw = stringifyPayload(payload);
  return summarizeText(raw, max);
};
