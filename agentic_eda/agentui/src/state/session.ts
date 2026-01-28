import { useReducer } from 'react';
import {
  accumulateUsage,
  calculateContextPercent,
  subtractUsage,
  type TokenUsage
} from './usage.js';

export type Speaker = 'user' | 'agent' | 'system';

export type SystemSeverity = 'success' | 'info' | 'warning' | 'error';

export type MessageActionStatus = 'running' | 'success' | 'error';

export interface MessageAction {
  id: string;
  name: string;
  status: MessageActionStatus;
  detail?: string;
  meta?: Record<string, unknown>;
}

export interface Message {
  id: string;
  speaker: Speaker;
  content: string;
  status?: 'pending' | 'complete' | 'error';
  timestamp?: string;
  severity?: SystemSeverity;
  hidden?: boolean;
  reasoning?: string;
  answer?: string;
  actions?: MessageAction[];
  showReasoning?: boolean;
  images?: import('../utils/images.js').ImageAttachment[];
}

export interface SessionState {
  messages: Message[];
  status: 'idle' | 'thinking' | 'error';
  error?: string;
  tokenUsage?: TokenUsage;
  contextPercent: number | null;
  usageHistory: TokenUsage[];
}

export type SessionAction =
  | { type: 'ADD_MESSAGE'; message: Message }
  | { type: 'UPDATE_MESSAGE'; id: string; patch: Partial<Message> }
  | { type: 'SET_STATUS'; status: SessionState['status']; error?: string }
  | { type: 'RESET_ERROR' }
  | { type: 'RESET_SESSION' }
  | { type: 'RESET_USAGE' }
  | { type: 'UNDO_LAST_TURN'; contextWindow?: number }
  | { type: 'UPDATE_USAGE'; delta: TokenUsage; contextWindow?: number };

export const initialSessionState: SessionState = {
  messages: [],
  status: 'idle',
  contextPercent: null,
  usageHistory: []
};

export const sessionReducer = (
  state: SessionState,
  action: SessionAction
): SessionState => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.message] };
    case 'UPDATE_MESSAGE':
      return {
        ...state,
        messages: state.messages.map((msg) =>
          msg.id === action.id ? { ...msg, ...action.patch } : msg
        )
      };
    case 'SET_STATUS':
      return { ...state, status: action.status, error: action.error };
    case 'RESET_ERROR':
      return { ...state, error: undefined, status: 'idle' };
    case 'UPDATE_USAGE': {
      const tokenUsage = accumulateUsage(state.tokenUsage, action.delta);
      const contextPercent = calculateContextPercent(tokenUsage, action.contextWindow);
      const usageHistory = [...state.usageHistory, action.delta];
      return { ...state, tokenUsage, contextPercent, usageHistory };
    }
    case 'RESET_SESSION':
      return { ...initialSessionState };
    case 'RESET_USAGE':
      return { ...state, tokenUsage: undefined, contextPercent: null, usageHistory: [] };
    case 'UNDO_LAST_TURN': {
      if (state.messages.length === 0) {
        return state;
      }
      const messages = [...state.messages];
      let removedUser = false;
      let removedAgent = false;
      while (messages.length && (!removedUser || !removedAgent)) {
        const msg = messages.pop();
        if (!msg) break;
        if (msg.speaker === 'agent' && !removedAgent) {
          removedAgent = true;
        } else if (msg.speaker === 'user' && !removedUser) {
          removedUser = true;
        }
      }
      const usageHistory = state.usageHistory.slice(0, -1);
      const lastDelta = state.usageHistory[state.usageHistory.length - 1];
      const tokenUsage = subtractUsage(state.tokenUsage, lastDelta);
      const contextPercent = calculateContextPercent(tokenUsage, action.contextWindow);
      return {
        ...state,
        messages,
        usageHistory,
        tokenUsage,
        contextPercent,
        status: 'idle',
        error: undefined
      };
    }
    default:
      return state;
  }
};

export const useSessionState = () => {
  return useReducer(sessionReducer, initialSessionState);
};
