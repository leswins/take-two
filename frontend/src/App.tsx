import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Transcripts from './pages/Transcripts';
import TranscriptDetail from './pages/TranscriptDetail';
import Players from './pages/Players';
import PlayerDetail from './pages/PlayerDetail';
import Upload from './pages/Upload';
import Compare from './pages/Compare';
import Commentators from './pages/Commentators';

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
        <Route path="/compare" element={<Compare />} />
        <Route path="/commentators" element={<Commentators />} />
      </Routes>
    </Layout>
  );
}

export default App;
