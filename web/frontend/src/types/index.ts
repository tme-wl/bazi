// API response types
export interface ApiPillar {
  stem: string;
  branch: string;
  stem_en: string;
  branch_en: string;
}

export interface ApiLuckCycle {
  ganzhi: string;
  ganzhi_en: string;
  age_start: number;
  age_end: number;
  element: string;
  element_en: string;
  tone: string;
  current: boolean;
  description: string;
  description_en: string;
}

export interface ApiSections {
  summary: string;
  summary_en: string;
  personality: string;
  personality_en: string;
  career: string;
  career_en: string;
  wealth: string;
  wealth_en: string;
  relationships: string;
  relationships_en: string;
  health: string;
  health_en: string;
  advice: string;
  advice_en: string;
}

export interface ApiResponse {
  bazi: string;
  bazi_en: string;
  pillars: Record<string, ApiPillar>;
  day_master: string;
  day_element: string;
  day_element_en: string;
  pattern: string;
  pattern_en: string;
  element_scores: Record<string, number>;
  element_scores_en: Record<string, number>;
  useful: string[];
  useful_en: string[];
  avoid: string[];
  avoid_en: string[];
  sections: ApiSections;
  luck_cycles: ApiLuckCycle[];
  llm_enhanced: boolean;
}

export interface AnalyzeRequest {
  year: number;
  month: number;
  day: number;
  hour?: number;
  minute?: number;
  gender: 'male' | 'female';
  language: 'en' | 'zh';
}

export type ViewState = 'home' | 'loading' | 'reading';

// Component prop types
export interface PillarData {
  heavenlyStem: string;
  earthlyBranch: string;
  hiddenStems?: string[];
}

export interface ElementScores {
  wood: number;
  fire: number;
  earth: number;
  metal: number;
  water: number;
}

export interface LifeSection {
  title: string;
  summary: string;
  details: string;
  rating: 'good' | 'neutral' | 'challenging';
}
