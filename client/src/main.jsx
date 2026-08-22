/**
 * main.jsx
 * Application entry point. Mounts <App /> wrapped with:
 *   - Redux <Provider>          (store.js - auth/theme/ui slices)
 *   - <BrowserRouter>           (react-router-dom)
 *   - react-hot-toast <Toaster> (global toast notifications)
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import './index.css'
import App from './App.jsx'
import { store } from './store/store.js'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
        <Toaster position="top-right" toastOptions={{ duration: 3500 }} />
      </BrowserRouter>
    </Provider>
  </StrictMode>,
)
