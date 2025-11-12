import { useEffect, useState } from 'react';
import { getStructure } from '../state/api';
import { Node } from '../state/types';

export const StructureView = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await getStructure();
        setNodes(data);
      } catch (err) {
        console.error(err);
        setError('Не удалось загрузить структуру');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return <section className="card">Загружаем структуру…</section>;
  }
  if (error) {
    return <section className="card error">{error}</section>;
  }

  return (
    <section className="card">
      <header className="card-header">
        <h2>Структура партнёров</h2>
        <span>{nodes.length} узлов</span>
      </header>
      <div className="structure-placeholder">
        <p>На данном этапе отрисовка дерева будет реализована в последующих задачах.</p>
        <pre>{JSON.stringify(nodes.slice(0, 5), null, 2)}</pre>
      </div>
    </section>
  );
};
