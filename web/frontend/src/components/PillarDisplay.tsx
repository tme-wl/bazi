import { useTranslation } from 'react-i18next';
import type { PillarData } from '../types';

interface PillarDisplayProps {
  pillars: {
    year: PillarData;
    month: PillarData;
    day: PillarData;
    hour: PillarData;
  };
  dayMaster: string;
}

const STEM_COLORS: Record<string, string> = {
  '甲': 'text-emerald-400', '乙': 'text-green-300',
  '丙': 'text-red-400', '丁': 'text-rose-300',
  '戊': 'text-amber-400', '己': 'text-yellow-300',
  '庚': 'text-gray-300', '辛': 'text-slate-200',
  '壬': 'text-blue-400', '癸': 'text-cyan-300',
};
const BRANCH_COLORS: Record<string, string> = {
  '子': 'text-blue-400', '丑': 'text-amber-400',
  '寅': 'text-emerald-400', '卯': 'text-green-300',
  '辰': 'text-amber-300', '巳': 'text-red-400',
  '午': 'text-red-500', '未': 'text-yellow-300',
  '申': 'text-gray-300', '酉': 'text-slate-200',
  '戌': 'text-amber-400', '亥': 'text-cyan-300',
};

const STEM_ENGLISH: Record<string, string> = {
  '甲': 'Jia', '乙': 'Yi', '丙': 'Bing', '丁': 'Ding',
  '戊': 'Wu', '己': 'Ji', '庚': 'Geng', '辛': 'Xin',
  '壬': 'Ren', '癸': 'Gui',
};
const BRANCH_ENGLISH: Record<string, string> = {
  '子': 'Zi', '丑': 'Chou', '寅': 'Yin', '卯': 'Mao',
  '辰': 'Chen', '巳': 'Si', '午': 'Wu', '未': 'Wei',
  '申': 'Shen', '酉': 'You', '戌': 'Xu', '亥': 'Hai',
};

export default function PillarDisplay({ pillars, dayMaster }: PillarDisplayProps) {
  const { i18n } = useTranslation();
  const isZh = i18n.language === 'zh';

  const labels = ['Year', 'Month', 'Day', 'Hour'];
  const pillarKeys = ['year', 'month', 'day', 'hour'] as const;

  const getStemDisplay = (stem: string) => isZh ? stem : (STEM_ENGLISH[stem] || stem);
  const getBranchDisplay = (branch: string) => isZh ? branch : (BRANCH_ENGLISH[branch] || branch);

  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-6">
      <div className="flex items-center justify-center gap-1 mb-6">
        <span className="text-sm text-gray-500">{isZh ? '日主' : 'Day Master'}:</span>
        <span className={`text-xl font-bold ${STEM_COLORS[dayMaster] || 'text-amber-400'}`}>
          {getStemDisplay(dayMaster)}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {pillarKeys.map((key, i) => {
          const pillar = pillars[key];
          return (
            <div key={key} className="text-center">
              <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">{labels[i]}</div>
              <div className={`text-3xl font-bold mb-1 ${STEM_COLORS[pillar.heavenlyStem] || 'text-amber-400'}`}>
                {getStemDisplay(pillar.heavenlyStem)}
              </div>
              <div className={`text-3xl font-bold ${BRANCH_COLORS[pillar.earthlyBranch] || 'text-emerald-400'}`}>
                {getBranchDisplay(pillar.earthlyBranch)}
              </div>
              <div className="mt-2 flex flex-wrap justify-center gap-1">
                {pillar.hiddenStems?.slice(0, 3).map((hs: string) => (
                  <span key={hs} className={`text-xs ${STEM_COLORS[hs] || 'text-gray-500'}`}>
                    {getStemDisplay(hs)}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
