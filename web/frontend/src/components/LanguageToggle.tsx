import { useTranslation } from 'react-i18next';

export default function LanguageToggle() {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const next = i18n.language === 'zh' ? 'en' : 'zh';
    i18n.changeLanguage(next);
  };

  return (
    <button
      onClick={toggleLanguage}
      className="px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-700 text-gray-300 hover:text-amber-400 hover:border-amber-500/50 transition-colors duration-200 bg-gray-800/50"
    >
      {i18n.language === 'zh' ? 'EN' : '中文'}
    </button>
  );
}
