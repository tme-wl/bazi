import { useTranslation } from 'react-i18next';
import LanguageToggle from '../components/LanguageToggle';
import PillarDisplay from '../components/PillarDisplay';
import ElementChart from '../components/ElementChart';
import SectionCard from '../components/SectionCard';
import LuckTimeline from '../components/LuckTimeline';
import type { ApiResponse } from '../types';

interface ReadingProps {
  data: ApiResponse;
  onBack: () => void;
}

export default function Reading({ data, onBack }: ReadingProps) {
  const { t, i18n } = useTranslation();
  const isZh = i18n.language === 'zh';

  // -- PillarDisplay expects: { year: {heavenlyStem, earthlyBranch, hiddenStems?}, ... }
  const pillars = {
    year: { heavenlyStem: data.pillars['年柱'].stem, earthlyBranch: data.pillars['年柱'].branch },
    month: { heavenlyStem: data.pillars['月柱'].stem, earthlyBranch: data.pillars['月柱'].branch },
    day: { heavenlyStem: data.pillars['日柱'].stem, earthlyBranch: data.pillars['日柱'].branch },
    hour: { heavenlyStem: data.pillars['时柱'].stem, earthlyBranch: data.pillars['时柱'].branch },
  };

  // -- ElementChart expects: { wood, fire, earth, metal, water }
  const es = data.element_scores;
  const maxElem = Math.max(...Object.values(es));
  const minElem = Math.min(...Object.values(es));
  const elemToKey: Record<string, string> = { '木': 'wood', '火': 'fire', '土': 'earth', '金': 'metal', '水': 'water' };
  const scores = {
    wood: es['木'] || 0,
    fire: es['火'] || 0,
    earth: es['土'] || 0,
    metal: es['金'] || 0,
    water: es['水'] || 0,
  };
  const dominantKey = Object.entries(es).find(([, v]) => v === maxElem)?.[0] || '';
  const deficientKey = Object.entries(es).find(([, v]) => v === minElem)?.[0] || '';
  const dominantElement = elemToKey[dominantKey] || dominantKey;
  const deficientElement = elemToKey[deficientKey] || deficientKey;

  // -- Sections
  const getSection = (key: string) => {
    const s = data.sections as unknown as Record<string, string>;
    const text = s[key + (isZh ? '' : '_en')] || s[key] || '';
    return text;
  };

  // -- Life sections for cards
  const sectionKeys = ['career', 'wealth', 'relationships', 'health', 'advice'] as const;
  const sectionIcons: Record<string, JSX.Element> = {
    career: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    wealth: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    relationships: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    ),
    health: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
      </svg>
    ),
    advice: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  };

  // -- Luck cycles
  const luckPillars = data.luck_cycles.map((c) => ({
    ageStart: c.age_start,
    ageEnd: c.age_end,
    heavenlyStem: c.ganzhi[0] || '',
    earthlyBranch: c.ganzhi[1] || '',
    description: isZh ? c.description : c.description_en,
    // Keep ganzhi for display
    ganzhi: isZh ? c.ganzhi : c.ganzhi_en,
  }));

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Nav */}
      <nav className="sticky top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-md border-b border-gray-800/50">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <button onClick={onBack} className="text-gray-400 hover:text-gray-200 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="text-lg font-semibold tracking-tight">
            <span className="text-amber-400">Bazi</span>
            <span className="text-gray-400">Reading</span>
          </span>
          <LanguageToggle />
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Title with Ba Zi */}
        <div className="text-center">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-100">
            {isZh ? data.bazi : data.bazi_en}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {data.pattern_en} · {data.llm_enhanced ? '✨ AI Enhanced' : t('reading.title')}
          </p>
        </div>

        {/* Four Pillars */}
        <section>
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">{t('reading.fourPillars')}</h2>
          <PillarDisplay pillars={pillars} dayMaster={data.day_master} />
        </section>

        {/* Pattern Summary + Element Chart */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-3">{t('reading.patternSummary')}</h3>
            <div className="inline-block px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm font-medium mb-3">
              {isZh ? data.pattern : data.pattern_en}
            </div>
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="text-xs text-gray-500">{isZh ? '喜用' : 'Favorable'}: {isZh ? data.useful.join(', ') : data.useful_en.join(', ')}</span>
              <span className="text-xs text-gray-500">|</span>
              <span className="text-xs text-gray-500">{isZh ? '忌神' : 'Avoid'}: {isZh ? data.avoid.join(', ') : data.avoid_en.join(', ')}</span>
            </div>
            <p className="text-sm text-gray-300 leading-relaxed">{getSection('summary')}</p>
          </div>
          <ElementChart scores={scores} dominantElement={dominantElement} deficientElement={deficientElement} />
        </div>

        {/* Personality */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-3">{isZh ? '性格分析' : 'Personality'}</h3>
          <p className="text-sm text-gray-300 leading-relaxed">{getSection('personality')}</p>
        </div>

        {/* Life Sections */}
        <section>
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">{t('reading.career')}</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {sectionKeys.map((key) => (
              <SectionCard
                key={key}
                icon={sectionIcons[key]}
                section={{
                  title: t(`reading.${key === 'relationships' ? 'relationships' : key}`),
                  summary: '',
                  details: getSection(key),
                  rating: 'neutral',
                }}
                colorClass={
                  key === 'career' ? 'border-blue-500/30' :
                  key === 'wealth' ? 'border-amber-500/30' :
                  key === 'relationships' ? 'border-rose-500/30' :
                  key === 'health' ? 'border-emerald-500/30' :
                  'border-violet-500/30'
                }
              />
            ))}
          </div>
        </section>

        {/* Luck Timeline */}
        <section>
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">{t('reading.luckTimeline')}</h2>
          <LuckTimeline pillars={luckPillars} />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 mt-12 py-6 px-4">
        <p className="text-center text-xs text-gray-600">{t('footer.disclaimer')}</p>
      </footer>
    </div>
  );
}
