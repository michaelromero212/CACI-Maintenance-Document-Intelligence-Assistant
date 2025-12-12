import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import DocumentDetail from './pages/DocumentDetail'
import StatusBoard from './pages/StatusBoard'
import SummaryReport from './pages/SummaryReport'
import CorrectiveActionPlan from './pages/CorrectiveActionPlan'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Dashboard />} />
                    <Route path="upload" element={<Upload />} />
                    <Route path="documents/:id" element={<DocumentDetail />} />
                    <Route path="status-board" element={<StatusBoard />} />
                    <Route path="reports/summary/:id" element={<SummaryReport />} />
                    <Route path="reports/cap/:id" element={<CorrectiveActionPlan />} />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
