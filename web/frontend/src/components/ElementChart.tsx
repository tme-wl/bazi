import { useTranslation } from 'react-i18next';
import type { ElementScores } from '../types';

interface ElementChartProps {
  scores: ElementScores;
  dominantElement: string;
  deficientElement: string;
}

const ELEMENT_CONFIG: Record<string, { color: string; label: string }> = {
  wood: { color: 'bg-emerald-500', label: 'Wood' },
  fire: { color: 'bg-red-500', label: 'Fire' },
  earth: { color: 'bg-amber-500', label: 'Earth' },
  metal: { color: 'bg-gray-300', label: 'Metal' },
  water: { color: 'bg-blue-500', label: 'Water' },
};

export default function ElementChart({ scores, dominantElement, deficientElement }: ElementChartProps) {
  const { t } = useTranslation();

  const elements = ['wood', 'fire', 'earth', 'metal', 'water'] as const;
  const maxScore = Math.max(...elements.map((e) => scores[e]), 1);

  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6">
      <h3 className="text-sm font-medium text-gray-400 mb-4">{t('reading.elementChart')}</h3>
      <div className="space-y-3">
        {elements.map((key) => {
          const config = ELEMENT_CONFIG[key];
          const score = scores[key];
          const pct = (score / maxScore) * 100;
          return (
            <div key={key}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-300">{t(`reading.element.${key}`)}</span>
                <span className="text-gray-500">{score.toFixed(1)}</span>
              </div>
              <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${config.color}`}
                  style={{ width: `${Math.max(pct, 4)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-4 flex gap-4 text-xs">
        {dominantElement && (
          <span className="text-emerald-400">
            ↑ {t('reading.element.wood')}: {t(`reading.element.${dominantElement}`)}
          </span>
        )}
        {deficientElement && (
          <span className="text-red-400">
            ↓ {t('reading.element.wood')}: {t(`reading.element.${deficientElement}`)}
          </span>
        )}
      </div>
    </div>
  );
}
