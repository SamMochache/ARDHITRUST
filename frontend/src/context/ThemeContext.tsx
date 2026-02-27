import React, { useEffect, useState, createContext, useContext } from 'react';
type Theme = 'light' | 'dark';
interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}
const ThemeContext = createContext<ThemeContextValue>({
  theme: 'light',
  toggleTheme: () => {}
});
export function ThemeProvider({ children }: {children: React.ReactNode;}) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('ardhitrust-theme') as Theme | null;
      if (stored) return stored;
      if (window.matchMedia('(prefers-color-scheme: dark)').matches)
      return 'dark';
    }
    return 'light';
  });
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('ardhitrust-theme', theme);
  }, [theme]);
  const toggleTheme = () => {
    setTheme((prev) => prev === 'light' ? 'dark' : 'light');
  };
  return (
    <ThemeContext.Provider
      value={{
        theme,
        toggleTheme
      }}>

      {children}
    </ThemeContext.Provider>);

}
export function useTheme() {
  return useContext(ThemeContext);
}