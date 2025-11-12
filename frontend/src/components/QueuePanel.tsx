import { useEffect, useState } from 'react';
import { getQueue, completeRegistration } from '../state/api';
import { QueueEntry } from '../state/types';

export const QueuePanel = () => {
  const [queue, setQueue] = useState<QueueEntry[]>([]);
  const [processing, setProcessing] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    try {
      const data = await getQueue();
      setQueue(data);
    } catch (err) {
      console.error(err);
      setError('Не удалось загрузить очередь');
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleComplete = async (entry: QueueEntry) => {
    setProcessing(entry.user);
    try {
      await completeRegistration(entry.user);
      await refresh();
    } catch (err) {
      console.error(err);
      setError('Ошибка завершения регистрации');
    } finally {
      setProcessing(null);
    }
  };

  return (
    <section className="card queue">
      <header className="card-header">
        <h2>Очередь регистрации</h2>
        <button onClick={refresh}>Обновить</button>
      </header>
      {error && <div className="error-banner">{error}</div>}
      <div className="queue-list">
        {queue.length === 0 && <p>Очередь пуста.</p>}
        {queue.map((entry) => (
          <div key={entry.id} className="queue-item">
            <div>
              <strong>{entry.user_display}</strong>
              <p>Пригласил: {entry.inviter ?? '—'}</p>
              <p>Тариф: {entry.tariff.name}</p>
            </div>
            <button
              disabled={processing === entry.user}
              onClick={() => handleComplete(entry)}
            >
              {processing === entry.user ? '...' : '$'}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
};
