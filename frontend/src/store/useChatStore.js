import { create } from 'zustand';

export const useChatStore = create((set) => ({
  messages: [
    {
      id: 'msg_1',
      sender: 'assistant',
      text: 'Hello! I am FinAgent AI, your personal financial intelligence assistant. How can I analyze your cashflow or transactions today?',
      sources: [],
      timestamp: new Date().toISOString(),
    },
  ],
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, { ...message, id: `msg_${Date.now()}` }],
    })),
  clearMessages: () =>
    set({
      messages: [
        {
          id: 'msg_init',
          sender: 'assistant',
          text: 'Conversation reset. Ask me anything about your income, expenses, subscriptions, or top merchants!',
          sources: [],
          timestamp: new Date().toISOString(),
        },
      ],
    }),
}));
