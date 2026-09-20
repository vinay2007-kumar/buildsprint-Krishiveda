import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import { ToastProvider } from './components/ui.jsx'
import { Dashboard, ChatAssistant, DiseaseDetection, SoilAnalysis, WeatherPage, SchemesPage } from './pages/Pages.jsx'

export default function App() {
  return (
    <ToastProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<ChatAssistant />} />
          <Route path="/disease" element={<DiseaseDetection />} />
          <Route path="/soil" element={<SoilAnalysis />} />
          <Route path="/weather" element={<WeatherPage />} />
          <Route path="/schemes" element={<SchemesPage />} />
        </Routes>
      </Layout>
    </ToastProvider>
  )
}