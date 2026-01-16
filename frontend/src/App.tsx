import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Transcripts from './pages/Transcripts';
import TranscriptDetail from './pages/TranscriptDetail';
import Players from './pages/Players';
import PlayerDetail from './pages/PlayerDetail';
import Upload from './pages/Upload';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/transcripts" element={<Transcripts />} />
        <Route path="/transcripts/:id" element={<TranscriptDetail />} />
        <Route path="/players" element={<Players />} />
        <Route path="/players/:id" element={<PlayerDetail />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Layout>
  );
}

export default App;
