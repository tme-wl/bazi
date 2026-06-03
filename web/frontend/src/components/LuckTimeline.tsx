interface LuckPillar {
  ageStart: number;
  ageEnd: number;
  heavenlyStem: string;
  earthlyBranch: string;
  description: string;
  ganzhi?: string;
}

export default function LuckTimeline({ pillars }: { pillars: LuckPillar[] }) {
  if (!pillars || pillars.length === 0) return null;

  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6">
      <h3 className="text-sm font-medium text-gray-400 mb-6">Luck Cycle Timeline</h3>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-800 -translate-y-1/2" />

        <div className="flex gap-0 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-gray-700">
          {pillars.map((pillar, i) => (
            <div key={i} className="flex flex-col items-center min-w-[100px] flex-shrink-0 relative">
              {/* Connector dot */}
              <div className="w-3 h-3 rounded-full bg-amber-500/60 border-2 border-gray-900 relative z-10 mb-3" />

              {/* Age range */}
              <span className="text-xs text-gray-500 mb-1 whitespace-nowrap">
                {pillar.ageStart}–{pillar.ageEnd}
              </span>

              {/* Pillar characters */}
              <div className="flex gap-1 mb-1">
                <span className="text-lg font-bold text-amber-400">{pillar.heavenlyStem}</span>
                <span className="text-lg font-bold text-emerald-400">{pillar.earthlyBranch}</span>
              </div>

              {/* Description */}
              <p className="text-xs text-gray-400 text-center leading-tight max-w-[90px]">
                {pillar.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
