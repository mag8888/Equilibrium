import { useEffect, useState } from 'react';
import { getStructure } from '../state/api';
import { Node } from '../state/types';

interface LevelGroup {
  level: number;
  nodes: Node[];
}

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
    return (
      <section className="card">
        <header className="card-header">
          <h2>Структура партнёров</h2>
        </header>
        <div className="loading">Загружаем структуру…</div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="card">
        <header className="card-header">
          <h2>Структура партнёров</h2>
        </header>
        <div className="error-banner">{error}</div>
      </section>
    );
  }

  // Группируем узлы по уровням
  const rootNode = nodes.find(n => !n.parent);
  const levelGroups: LevelGroup[] = [];
  
  if (rootNode) {
    const buildLevels = (parentId: number | null, level: number): void => {
      const children = nodes.filter(n => n.parent === parentId);
      if (children.length > 0 || level === 0) {
        if (!levelGroups[level]) {
          levelGroups[level] = { level, nodes: [] };
        }
        if (level === 0 && parentId === null) {
          levelGroups[level].nodes.push(rootNode);
        }
        children.forEach(child => {
          levelGroups[level].nodes.push(child);
          buildLevels(child.user, level + 1);
        });
      }
    };
    
    buildLevels(null, 0);
  }

  return (
    <section className="card">
      <header className="card-header">
        <h2>Структура партнёров</h2>
        <span>{nodes.length} узлов</span>
      </header>
      <div className="structure-container">
        {levelGroups.length === 0 ? (
          <div className="structure-placeholder">
            <p>Структура пуста. Добавьте первого партнёра.</p>
          </div>
        ) : (
          <div className="structure-tree">
            {levelGroups.map((group, idx) => (
              <div key={group.level} className="structure-level">
                {group.nodes.map((node) => (
                  <div
                    key={node.id}
                    className={`structure-node ${node.level === 0 ? 'root' : ''}`}
                    title={`Уровень: ${node.level}, Партнёров: ${node.direct || 0}`}
                  >
                    <div className="node-name">
                      {node.level === 0 ? '🌐' : '👤'} {node.user_display || `ID ${node.user}`}
                    </div>
                    <div className="node-level">Уровень {node.level}</div>
                    <div className="node-stats">
                      <div>
                        <div style={{ fontWeight: 600 }}>{node.direct || 0}</div>
                        <div style={{ fontSize: 11, opacity: 0.7 }}>прямых</div>
                      </div>
                      <div>
                        <div style={{ fontWeight: 600 }}>{node.total || 0}</div>
                        <div style={{ fontSize: 11, opacity: 0.7 }}>всего</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};
