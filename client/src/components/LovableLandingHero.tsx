import React from 'react';
import { ChevronDown, ArrowRight, Sparkles, Play, Shield, Zap, Layers, Globe } from 'lucide-react';
import { motion } from 'framer-motion';

interface LovableLandingHeroProps {
  onExplorePlatform?: () => void;
  onGetDemo?: () => void;
}

export const LovableLandingHero: React.FC<LovableLandingHeroProps> = ({
  onExplorePlatform,
  onGetDemo
}) => {
  return (
    <div className="relative min-h-screen w-full bg-[#08090d] text-white flex flex-col justify-between overflow-hidden font-['Outfit',sans-serif] selection:bg-pink-500 selection:text-white">
      {/* 1. Atmospheric Gradient Lighting Layers */}
      {/* Bottom-Left Directional Spotlight (Magenta / Violet Beam projecting diagonally) */}
      <div 
        className="absolute -bottom-24 -left-24 w-[750px] h-[600px] pointer-events-none z-0"
        style={{
          background: 'radial-gradient(ellipse at bottom left, rgba(236, 72, 153, 0.42) 0%, rgba(168, 85, 247, 0.28) 35%, rgba(88, 28, 135, 0.1) 60%, transparent 75%)',
          filter: 'blur(70px)',
          transform: 'rotate(-15deg)'
        }}
      />

      {/* Bottom-Right Ambient Royal Blue / Cyan Glow */}
      <div 
        className="absolute -bottom-20 -right-20 w-[800px] h-[650px] pointer-events-none z-0"
        style={{
          background: 'radial-gradient(ellipse at bottom right, rgba(59, 130, 246, 0.45) 0%, rgba(99, 102, 241, 0.3) 40%, rgba(14, 165, 233, 0.1) 65%, transparent 80%)',
          filter: 'blur(80px)'
        }}
      />

      {/* Central Soft Ambient Glow directly behind headline */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] pointer-events-none z-0"
        style={{
          background: 'radial-gradient(circle, rgba(236, 72, 153, 0.12) 0%, rgba(59, 130, 246, 0.08) 50%, transparent 70%)',
          filter: 'blur(90px)'
        }}
      />

      {/* 2. Top Navigation Bar */}
      <nav className="relative z-50 w-full max-w-7xl mx-auto h-20 px-6 sm:px-10 flex items-center justify-between">
        {/* Brand Logo */}
        <div className="flex items-center space-x-3 cursor-pointer group">
          {/* Folded Heart / Multi-Color Gradient Icon */}
          <div className="relative w-7 h-7 flex items-center justify-center">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full drop-shadow-[0_0_12px_rgba(244,63,94,0.6)]">
              <path 
                d="M16 28C16 28 3 20.5 3 11.5C3 6.8 6.8 3 11.5 3C14.2 3 15.6 4.3 16 5.2C16.4 4.3 17.8 3 20.5 3C25.2 3 29 6.8 29 11.5C29 20.5 16 28 16 28Z" 
                fill="url(#lovable-grad)"
              />
              <defs>
                <linearGradient id="lovable-grad" x1="3" y1="3" x2="29" y2="28" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FB923C" />
                  <stop offset="35%" stopColor="#F43F5E" />
                  <stop offset="70%" stopColor="#A855F7" />
                  <stop offset="100%" stopColor="#38BDF8" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span className="text-xl font-bold tracking-tight text-white group-hover:text-zinc-200 transition-colors">
            Lovable
          </span>
        </div>

        {/* Center Menu Links */}
        <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-zinc-300">
          <div className="flex items-center space-x-1 hover:text-white cursor-pointer transition-colors">
            <span>Solutions</span>
            <ChevronDown className="w-3.5 h-3.5 opacity-70" />
          </div>
          <div className="flex items-center space-x-1 hover:text-white cursor-pointer transition-colors">
            <span>Resources</span>
            <ChevronDown className="w-3.5 h-3.5 opacity-70" />
          </div>
          <span className="hover:text-white cursor-pointer transition-colors">Community</span>
          <span className="hover:text-white cursor-pointer transition-colors">Enterprise</span>
          <span className="hover:text-white cursor-pointer transition-colors">Pricing</span>
          <span className="hover:text-white cursor-pointer transition-colors">Security</span>
        </div>

        {/* Right Action Buttons */}
        <div className="flex items-center space-x-3">
          <button 
            onClick={onGetDemo}
            className="px-4 py-2 rounded-full text-sm font-medium text-zinc-200 bg-zinc-800/70 hover:bg-zinc-700/80 border border-zinc-700/60 hover:border-zinc-600 transition-all cursor-pointer"
          >
            Log in
          </button>
          <button 
            onClick={onExplorePlatform}
            className="px-4 py-2 rounded-full text-sm font-semibold text-zinc-950 bg-white hover:bg-zinc-100 transition-all shadow-md active:scale-95 cursor-pointer"
          >
            Get started
          </button>
        </div>
      </nav>

      {/* 3. Hero Centerpiece Content */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-4 pt-12 pb-24 max-w-5xl mx-auto">
        {/* Eyebrow Badge */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <span className="text-zinc-400 font-medium text-sm sm:text-base tracking-wide">
            Lovable for enterprises
          </span>
        </motion.div>

        {/* Massive Display Headline ("Ship [3D Prism Icon] faster") */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="flex items-center justify-center flex-wrap gap-x-3 sm:gap-x-5 leading-none tracking-tight select-none"
        >
          {/* Word "Ship" */}
          <span className="text-7xl sm:text-8xl md:text-9xl font-extrabold text-white tracking-tight drop-shadow-2xl">
            Ship
          </span>

          {/* Centerpiece 3D Translucent Neon Prism Pointer */}
          <div className="relative inline-flex items-center justify-center mx-1 sm:mx-2 group">
            {/* Ambient drop glow */}
            <div className="absolute inset-0 bg-gradient-to-r from-pink-500 via-rose-500 to-cyan-400 rounded-3xl filter blur-xl opacity-70 group-hover:opacity-100 transition-opacity" />
            
            <svg 
              viewBox="0 0 120 120" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
              className="relative w-20 h-20 sm:w-28 sm:h-28 md:w-36 md:h-36 drop-shadow-[0_15px_30px_rgba(255,59,129,0.5)] transform hover:scale-105 transition-transform duration-300"
            >
              <defs>
                {/* 3D Prism Gradient */}
                <linearGradient id="prism-front" x1="20" y1="20" x2="100" y2="100" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FF3B81" />
                  <stop offset="50%" stopColor="#E056FD" />
                  <stop offset="100%" stopColor="#38E8FF" />
                </linearGradient>
                <linearGradient id="prism-top" x1="30" y1="10" x2="100" y2="60" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#FF65A3" />
                  <stop offset="100%" stopColor="#C066FF" />
                </linearGradient>
                <linearGradient id="prism-glass" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="rgba(255,255,255,0.6)" />
                  <stop offset="100%" stopColor="rgba(255,255,255,0.05)" />
                </linearGradient>
              </defs>

              {/* Main Arrow / Prism Body */}
              <path 
                d="M22 28C22 23.5787 26.5816 20.8037 30.4199 23.0118L102.42 64.4118C106.258 66.6199 106.258 72.1558 102.42 74.3639L30.4199 115.764C26.5816 117.972 22 115.197 22 110.776V28Z" 
                fill="url(#prism-front)"
              />

              {/* Top Facet for 3D Volume */}
              <path 
                d="M22 28C22 23.5787 26.5816 20.8037 30.4199 23.0118L102.42 64.4118C95 62 65 52 22 55V28Z" 
                fill="url(#prism-top)"
                opacity="0.85"
              />

              {/* Glossy Glass Highlight Overlay */}
              <path 
                d="M24 30L95 68L30 80L24 30Z" 
                fill="url(#prism-glass)"
                opacity="0.6"
              />
            </svg>
          </div>

          {/* Word "faster" */}
          <span className="text-7xl sm:text-8xl md:text-9xl font-extrabold text-white tracking-tight drop-shadow-2xl">
            faster
          </span>
        </motion.div>

        {/* Subtitle */}
        <motion.p 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="text-zinc-300/90 text-base sm:text-lg md:text-xl max-w-xl mx-auto mt-8 font-normal leading-relaxed text-center"
        >
          Prototype faster, validate early, and ship internal tools and production apps without waiting on engineering.
        </motion.p>

        {/* Call to Action Buttons */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.35 }}
          className="mt-8 flex flex-col sm:flex-row items-center gap-4"
        >
          <button 
            onClick={onGetDemo}
            className="px-6 py-2.5 rounded-full text-sm font-semibold text-zinc-900 bg-zinc-100 hover:bg-white transition-all shadow-lg hover:shadow-white/20 active:scale-95 cursor-pointer"
          >
            Get a demo
          </button>

          {/* Secondary Quick Jump into Blue Orbit Platform */}
          <button 
            onClick={onExplorePlatform}
            className="px-6 py-2.5 rounded-full text-sm font-semibold text-zinc-200 bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-700/80 hover:border-cyan-400 transition-all flex items-center space-x-2 active:scale-95 cursor-pointer"
          >
            <span>Launch Blue Orbit Studio</span>
            <ArrowRight className="w-4 h-4 text-cyan-400" />
          </button>
        </motion.div>
      </main>

      {/* 4. Bottom Footer Strip */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 border-t border-zinc-800/40 flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-500 gap-3">
        <div>
          © 2026 Lovable · Enterprise AI Platform
        </div>
        <div className="flex items-center space-x-6 text-zinc-400">
          <span className="hover:text-white cursor-pointer transition-colors">Privacy Policy</span>
          <span className="hover:text-white cursor-pointer transition-colors">Terms of Service</span>
          <span className="hover:text-white cursor-pointer transition-colors">Security</span>
          <span className="hover:text-white cursor-pointer transition-colors">SOC2 Type II Certified</span>
        </div>
      </footer>
    </div>
  );
};
