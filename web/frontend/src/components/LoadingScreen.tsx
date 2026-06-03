import { useTranslation } from 'react-i18next';
import { useEffect, useState } from 'react';

export default function LoadingScreen() {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    t('loading.step1'),
    t('loading.step2'),
    t('loading.step3'),
    t('loading.step4'),
    t('loading.step5'),
  ];

  useEffect(() => {
    if (currentStep >= steps.length - 1) return;
    const timer = setTimeout(() => setCurrentStep((s) => s + 1), 1200);
    return () => clearTimeout(timer);
  }, [currentStep, steps.length]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-950 px-4">
      {/* Animated ring */}
      <div className="relative mb-12">
        <div className="w-24 h-24 rounded-full border-2 border-gray-800 animate-pulse" />
        <div className="absolute inset-0 w-24 h-24 rounded-full border-2 border-t-amber-500 border-r-emerald-500 border-transparent animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <svg className="w-8 h-8 text-amber-400/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </div>
      </div>

      <h2 className="text-xl font-semibold text-gray-200 mb-8">{t('loading.title')}</h2>

      <div className="space-y-3">
        {steps.map((step, i) => (
          <div
            key={i}
            className={`flex items-center gap-3 transition-all duration-500 ${
              i <= currentStep ? 'opacity-100' : 'opacity-20'
            }`}
          >
            {i < currentStep ? (
              <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : i === currentStep ? (
              <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border border-gray-700 flex-shrink-0" />
            )}
            <span className={`text-sm ${i <= currentStep ? 'text-gray-300' : 'text-gray-600'}`}>
              {step}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
