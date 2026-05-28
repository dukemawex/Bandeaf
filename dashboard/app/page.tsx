import Link from 'next/link';

export default function HomePage() {
  return (
    <main style={{ padding: 24 }}>
      <h1>SAFE-NET Dashboard</h1>
      <ul>
        <li><Link href="/dashboard">Responder Dashboard</Link></li>
        <li><Link href="/alerts">Alerts</Link></li>
        <li><Link href="/zones">Zones</Link></li>
        <li><Link href="/users">Users</Link></li>
        <li><Link href="/responders">Responders</Link></li>
      </ul>
    </main>
  );
}
