import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles.css'

createRoot(document.getElementById('root')).render(<App />)

// Register service worker (PWA) — safe fallback if not available
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/src/sw.js').then(reg => {
      console.log('ServiceWorker registered:', reg.scope);
    }).catch(err => console.warn('ServiceWorker registration failed:', err));
  });
}
