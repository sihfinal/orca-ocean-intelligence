import React from 'react';
import { 
  ArrowRight, 
  Sparkles, 
  Compass,
  Lock
} from 'lucide-react';
import { motion } from 'framer-motion';
import KineticGrid from './ui/kinetic-grid';
import { t } from '../utils/translations';

interface BlueOrbitLandingHeroProps {
  onExplorePlatform: (tab: 'home' | 'chat' | 'map' | 'agent-lab' | 'safety' | 'bulletin') => void;
  currentLang?: string; // 👈 1. Added currentLang here
}

export const BlueOrbitLandingHero: React.FC<BlueOrbitLandingHeroProps> = ({
  onExplorePlatform,
  currentLang = 'en' // 👈 2. Received currentLang here
}) => {
  return (
    <KineticGrid globalColor="light" className="min-h-screen h-screen flex flex-col justify-between select-none">
      
      {/* Subtle Ambient Depth Glow */}
      <div 
        className="absolute top-1/3 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[750px] h-[520px] pointer-events-none z-0"
        style={{
          background: 'radial-gradient(circle, rgba(56, 189, 248, 0.22) 0%, rgba(14, 165, 233, 0.12) 40%, transparent 70%)',
          filter: 'blur(110px)'
        }}
      />

      {/* Main Left-Aligned Calibrated Hero Section */}
      <main className="relative z-10 flex-1 flex flex-col items-start justify-center text-left px-6 sm:px-12 lg:px-20 pt-28 sm:pt-40 pb-12 max-w-7xl mx-auto w-full pointer-events-auto">
        
        {/* Calibrated Display Headline & Subtitle */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="space-y-4 max-w-3xl"
        >
          {/* 👇 Heading 1 & Heading 2 translated */}
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-[-0.035em] leading-[1.12] select-none text-slate-900 drop-shadow-xs">
            {t('hero_title_1', currentLang)}<br />
            <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 bg-clip-text text-transparent">
              {t('hero_title_2', currentLang)}
            </span>
          </h1>

          {/* 👇 Paragraph translated */}
          <p className="text-slate-600 text-sm sm:text-base md:text-lg max-w-2xl font-normal leading-[1.65] pt-1">
            {t('hero_subtitle', currentLang)}
          </p>
        </motion.div>

        {/* Calibrated Action Buttons */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }}
          className="mt-8 flex flex-col sm:flex-row items-stretch sm:items-center gap-3.5 w-full sm:w-auto"
        >
          {/* 👇 Button 1 translated */}
          <button 
            onClick={() => onExplorePlatform('chat')}
            className="w-full sm:w-auto px-7 py-3.5 rounded-full text-sm font-semibold text-white bg-slate-900 hover:bg-slate-800 transition-all shadow-md active:scale-95 cursor-pointer flex items-center justify-center space-x-2 group"
          >
            <Sparkles className="w-4 h-4 text-cyan-300 group-hover:rotate-12 transition-transform" />
            <span>{t('launch_ai_studio', currentLang)}</span>
            <ArrowRight className="w-4 h-4 text-slate-300 group-hover:translate-x-0.5 transition-transform" />
          </button>

          {/* 👇 Button 2 translated */}
          <button 
            onClick={() => onExplorePlatform('map')}
            className="w-full sm:w-auto px-7 py-3.5 rounded-full text-sm font-semibold text-slate-800 bg-white hover:bg-slate-50 border border-slate-200 transition-all flex items-center justify-center space-x-2 active:scale-95 cursor-pointer shadow-xs"
          >
            <Compass className="w-4 h-4 text-blue-600" />
            <span>{t('gis_command_map', currentLang)}</span>
          </button>
        </motion.div>
      </main>

      {/* Bottom Footer Strip */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-6 sm:px-12 lg:px-20 py-4 border-t border-slate-200/80 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2 shrink-0">
        <div>
          Created by <strong className="text-slate-700 font-medium">Sih_Hackers</strong> for ISRO · Smart India Hackathon 2026
        </div>
        <div className="text-xs text-slate-500 font-mono">
          Oceansat-3 · INSAT-3DR · INCOIS
        </div>
      </footer>
    </KineticGrid>
  );
};

export const OrcaLandingHero = BlueOrbitLandingHero;