import type { ReactNode } from 'react';
import type { LifeSection } from '../types';

interface SectionCardProps {
  icon: ReactNode;
  section: LifeSection;
  colorClass?: string;
}

export default function SectionCard({ icon, section, colorClass = 'border-amber-500/30' }: SectionCardProps) {
  const ratingColors: Record<string, string> = {
    good: 'text-emerald-400',
    neutral: 'text-amber-400',
    challenging: 'text-red-400',
  };

  return (
    <div className={`bg-gray-900/80 border ${colorClass} rounded-2xl p-5 transition-all duration-200 hover:border-opacity-60`}>
      <div className="flex items-start gap-3 mb-3">
        <div className="mt-0.5 text-amber-400/80">{icon}</div>
        <div className="flex-1">
          <h3 className="text-base font-semibold text-gray-100">{section.title}</h3>
          <p className="text-sm text-gray-400 mt-1">{section.summary}</p>
        </div>
        <span className={`text-xs font-medium ${ratingColors[section.rating] || 'text-gray-500'}`}>
          {section.rating.charAt(0).toUpperCase() + section.rating.slice(1)}
        </span>
      </div>
      <p className="text-sm text-gray-300 leading-relaxed">{section.details}</p>
    </div>
  );
}
