import { useTranslation } from 'react-i18next';
import BirthForm from '../components/BirthForm';
import LanguageToggle from '../components/LanguageToggle';
import type { AnalyzeRequest, ViewState } from '../types';

interface HomeProps {
  onAnalyze: (data: AnalyzeRequest) => void;
  loading: boolean;
}

export default function Home({ onAnalyze, loading }: HomeProps) {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-950/80 backdrop-blur-md border-b border-gray-800/50">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="text-lg font-semibold tracking-tight">
            <span className="text-amber-400">Bazi</span>
            <span className="text-gray-400">Reading</span>
          </span>
          <LanguageToggle />
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-24 pb-12 px-4 overflow-hidden">
        {/* Subtle background pattern */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-500/5 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-3xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-gray-100 mb-4">
            {t('home.heroTitle')}
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
            {t('home.heroSubtitle')}
          </p>
        </div>
      </section>

      {/* Form Section */}
      <section className="px-4 pb-20">
        <div className="max-w-md mx-auto">
          <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 backdrop-blur-sm">
            <h2 className="text-base font-semibold text-gray-200 mb-5">{t('home.formTitle')}</h2>
            <BirthForm onSubmit={onAnalyze} loading={loading} />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 py-6 px-4">
        <p className="text-center text-xs text-gray-600">{t('footer.disclaimer')}</p>
      </footer>
    </div>
  );
}
