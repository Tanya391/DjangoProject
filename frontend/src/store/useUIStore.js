import { create } from 'zustand';

const initialTheme = localStorage.getItem('finagent_theme') || 'light';

export const useUIStore = create((set) => ({
  isSidebarOpen: true,
  theme: initialTheme,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
  toggleTheme: () =>
    set((state) => {
      const nextTheme = state.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('finagent_theme', nextTheme);
      return { theme: nextTheme };
    }),
  setTheme: (theme) => {
    localStorage.setItem('finagent_theme', theme);
    set({ theme });
  },
}));
