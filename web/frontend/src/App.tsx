import { useState } from 'react';
import type { AnalyzeRequest, ApiResponse, ViewState } from './types';
import { analyzeBazi } from './api/client';
import Home from './pages/Home';
import Reading from './pages/Reading';
import LoadingScreen from './components/LoadingScreen';

export default function App() {
  const [viewState, setViewState] = useState<ViewState>('home');
  const [reading, setReading] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (data: AnalyzeRequest) => {
    setLoading(true);
    setError(null);
    setViewState('loading');

    try {
      const result = await analyzeBazi(data);
      setReading(result);
      setViewState('reading');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setViewState('home');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setViewState('home');
    setReading(null);
    setError(null);
  };

  return (
    <>
      {viewState === 'home' && (
        <Home onAnalyze={handleAnalyze} loading={loading} />
      )}
      {viewState === 'loading' && (
        <LoadingScreen />
      )}
      {viewState === 'reading' && reading && (
        <Reading data={reading} onBack={handleBack} />
      )}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-900/90 border border-red-700 text-red-200 px-4 py-3 rounded-lg text-sm max-w-sm shadow-xl">
          {error}
        </div>
      )}
    </>
  );
}
