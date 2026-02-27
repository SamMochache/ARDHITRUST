import React from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { Home } from './pages/Home';
export function App() {
  return (
    <ThemeProvider>
      <Home />
    </ThemeProvider>);

}