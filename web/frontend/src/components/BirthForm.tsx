import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { AnalyzeRequest } from '../types';

interface BirthFormProps {
  onSubmit: (data: AnalyzeRequest) => void;
  loading: boolean;
}

export default function BirthForm({ onSubmit, loading }: BirthFormProps) {
  const { t, i18n } = useTranslation();

  const [year, setYear] = useState(new Date().getFullYear() - 30);
  const [month, setMonth] = useState(1);
  const [day, setDay] = useState(15);
  const [hour, setHour] = useState(12);
  const [minute, setMinute] = useState(0);
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [timeUnknown, setTimeUnknown] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const common = {
      year,
      month,
      day,
      gender,
      language: i18n.language as 'en' | 'zh',
    } as AnalyzeRequest;
    if (!timeUnknown) {
      common.hour = hour;
      common.minute = minute;
    }
    onSubmit(common);
  };

  const currentYear = new Date().getFullYear();

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Birth Date */}
      <div>
        <label className="block text-sm font-medium text-gray-400 mb-2">{t('home.birthDate')}</label>
        <div className="grid grid-cols-3 gap-3">
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500/60"
          >
            {Array.from({ length: 120 }, (_, i) => currentYear - i).map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <select
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500/60"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{String(m).padStart(2, '0')}</option>
            ))}
          </select>
          <select
            value={day}
            onChange={(e) => setDay(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500/60"
          >
            {Array.from({ length: 31 }, (_, i) => i + 1).map((d) => (
              <option key={d} value={d}>{String(d).padStart(2, '0')}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Birth Time */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-400">{t('home.birthTime')}</label>
          <label className="flex items-center gap-2 text-xs text-gray-500">
            <input
              type="checkbox"
              checked={timeUnknown}
              onChange={(e) => setTimeUnknown(e.target.checked)}
              className="rounded border-gray-600 bg-gray-800 text-amber-500 focus:ring-amber-500/40"
            />
            {t('home.unknownTime')}
          </label>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <select
            value={hour}
            onChange={(e) => setHour(Number(e.target.value))}
            disabled={timeUnknown}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500/60 disabled:opacity-40"
          >
            {Array.from({ length: 24 }, (_, i) => i).map((h) => (
              <option key={h} value={h}>{String(h).padStart(2, '0')}</option>
            ))}
          </select>
          <select
            value={minute}
            onChange={(e) => setMinute(Number(e.target.value))}
            disabled={timeUnknown}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500/40 focus:border-amber-500/60 disabled:opacity-40"
          >
            {Array.from({ length: 60 }, (_, i) => i).map((m) => (
              <option key={m} value={m}>{String(m).padStart(2, '0')}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Gender */}
      <div>
        <label className="block text-sm font-medium text-gray-400 mb-2">{t('home.gender')}</label>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setGender('male')}
            className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              gender === 'male'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50'
                : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-gray-600'
            }`}
          >
            {t('home.genderMale')}
          </button>
          <button
            type="button"
            onClick={() => setGender('female')}
            className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              gender === 'female'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50'
                : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-gray-600'
            }`}
          >
            {t('home.genderFemale')}
          </button>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 px-6 rounded-lg font-semibold text-base transition-all duration-200 bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-gray-950 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-amber-500/20"
      >
        {loading ? t('home.analyzing') : t('home.analyzeButton')}
      </button>
    </form>
  );
}
