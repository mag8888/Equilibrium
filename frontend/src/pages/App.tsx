import { useEffect } from 'react';
import { StructureView } from '../components/StructureView';
import { QueuePanel } from '../components/QueuePanel';
import './app.css';

export const App = () => {
  useEffect(() => {
    document.title = 'Equilibrium Admin';
  }, []);

  return (
    <div className="layout">
      <header className="app-header">
        <div>
          <h1>Equilibrium · Панель управления</h1>
          <p>Управляйте структурой партнёров и очередью регистраций.</p>
        </div>
      </header>
      <main className="app-main">
        <StructureView />
        <QueuePanel />
      </main>
    </div>
  );
};
