import AlertList from '../../components/AlertList';
import MapPanel from '../../components/MapPanel';

export default function DashboardPage() {
  return (
    <main style={{ padding: 16, display: 'grid', gap: 16 }}>
      <h1>Community Responder View</h1>
      <MapPanel />
      <AlertList />
    </main>
  );
}
