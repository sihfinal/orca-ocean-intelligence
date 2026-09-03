import React from 'react'
import ReactDOM from 'react-dom/client'
import 'leaflet/dist/leaflet.css'
import './index.css'
import { App } from './App'

// Ensure browser tab title is updated immediately
document.title = "Blue Orbit — ISRO Marine Ecosystem Reasoning with Collaborative Agents";

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
