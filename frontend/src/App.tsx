
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import DashboardPage from './pages/DashboardPage';
import AnalyticsPage from './pages/AnalyticsPage';
import QuestionBank from './pages/QuestionBank';
import QuestionEditor from './pages/QuestionEditor';
import MvpMockupPage from './pages/MvpMockupPage';
import MisconceptionClinic from './pages/MisconceptionClinic';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="questions" element={<QuestionBank />} />
          <Route path="questions/new" element={<QuestionEditor />} />
          <Route path="questions/:id" element={<QuestionEditor />} />
          <Route path="misconception/:questionId" element={<MisconceptionClinic />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="mockup" element={<MvpMockupPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
