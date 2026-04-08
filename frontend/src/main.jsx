import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'  // Real-time API integration with toggle mode
import ErrorBoundary from './components/ErrorBoundary'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
