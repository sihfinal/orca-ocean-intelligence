import React, { useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

export interface HolographicBeamsProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * Theme mode: 'dark' or 'light'
   * Default: 'light'
   */
  theme?: 'dark' | 'light';
  /**
   * Density of the light pillars.
   * Default: 20
   */
  density?: number;
  /**
   * Speed of the animation.
   * Default: 1.4
   */
  speed?: number;
  /**
   * Intensity of the chromatic aberration (RGB shift).
   * Default: 3.5
   */
  aberration?: number;
  /**
   * Base color weight (mostly influences the center white-hot area).
   * Default: 95 (opacity percentage)
   */
  opacity?: number;
}

export const HolographicBeams: React.FC<HolographicBeamsProps> = ({
  className,
  theme = 'light',
  density = 20,
  speed = 1.4,
  aberration = 3.5,
  opacity = 95,
  style,
  ...props
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = container.offsetWidth;
    let height = container.offsetHeight;
    let time = 0;
    let animationFrameId: number;

    const isLight = theme === 'light';

    // --- NOISE GENERATOR (Sine Superposition) ---
    const noise = (x: number, t: number) => {
      return (
        Math.sin(x * 0.01 + t) +
        Math.sin(x * 0.03 + t * 2) * 0.5 +
        Math.sin(x * 0.1 + t * 4) * 0.25
      ) / 1.75; // Normalize roughly to -1..1
    };

    const resize = () => {
      width = container.offsetWidth;
      height = container.offsetHeight;
      canvas.width = width;
      canvas.height = height;
    };

    const drawBeam = (x: number, t: number, color: string, widthMod: number) => {
      const n = noise(x, t * 0.5);
      const beamHeight = height * (0.82 + n * 0.25); 
      const beamWidth = (width / density) * widthMod;

      const gradient = ctx.createLinearGradient(x, height, x, height - beamHeight);
      gradient.addColorStop(0, color); // Base
      gradient.addColorStop(1, "transparent"); // Tip

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.moveTo(x - beamWidth / 2, height);
      ctx.lineTo(x + beamWidth / 2, height);
      ctx.lineTo(x + beamWidth, height - beamHeight);
      ctx.lineTo(x - beamWidth, height - beamHeight);
      ctx.fill();
    };

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      
      // On light theme, use source-over for rich vivid jewel tones; on dark, use screen for glowing additive blending
      ctx.globalCompositeOperation = isLight ? "source-over" : "screen";

      time += 0.01 * speed;
      const beamWidth = width / density;

      for (let i = 0; i <= density; i++) {
        const x = i * beamWidth;
        const pos = i / density; // 0 (left) to 1 (right)
        
        if (isLight) {
          // 1. ROYAL COBALT BLUE / INDIGO CHANNEL (Left to Center)
          const bAlpha = (opacity / 100) * (0.7 + 0.3 * Math.sin(i * 0.5 + time * 1.1));
          const blueWeight = Math.max(0.35, 1.3 - pos * 1.1);
          drawBeam(
              x - aberration * 1.5, 
              time + i * 0.1, 
              `rgba(29, 78, 216, ${bAlpha * 0.85 * blueWeight})`, 
              1.8
          );

          // 2. CRIMSON / SCARLET RED CHANNEL (Right to Center)
          const rAlpha = (opacity / 100) * (0.7 + 0.3 * Math.cos(i * 0.45 + time));
          const redWeight = Math.max(0.35, pos * 1.1 + 0.2);
          drawBeam(
              x + aberration * 1.5, 
              time + i * 0.12 + 10, 
              `rgba(225, 29, 72, ${rAlpha * 0.88 * redWeight})`, 
              1.8
          );

          // 3. VIOLET / MAGENTA / PURPLE CORE CHANNEL (Mid transitions)
          const coreAlpha = (opacity / 100) * (0.65 + 0.35 * Math.sin(i * 0.35 - time));
          drawBeam(
              x, 
              time + i * 0.1 + 5, 
              `rgba(147, 51, 234, ${coreAlpha * 0.75})`, 
              1.2
          );
        } else {
          // Dark Hologram Mode (Pure RGB)
          const rAlpha = (opacity / 100) * (0.5 + 0.5 * Math.cos(i * 0.5 + time));
          drawBeam(
              x - aberration, 
              time + i * 0.1, 
              `rgba(255, 0, 0, ${rAlpha * 0.5})`, 
              1.5
          );

          const bAlpha = (opacity / 100) * (0.5 + 0.5 * Math.sin(i * 0.6 + time * 1.1));
          drawBeam(
              x + aberration, 
              time + i * 0.12 + 10, 
              `rgba(0, 50, 255, ${bAlpha * 0.5})`, 
              1.5
          );

          const coreAlpha = (opacity / 100) * (0.6 + 0.4 * Math.sin(i * 0.3 - time));
          drawBeam(
              x, 
              time + i * 0.1 + 5, 
              `rgba(200, 255, 255, ${coreAlpha * 0.3})`, 
              0.8
          );
        }
      }

      animationFrameId = requestAnimationFrame(draw);
    };

    window.addEventListener("resize", resize);
    resize();
    draw();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [theme, density, speed, aberration, opacity]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "absolute inset-0 z-0 overflow-hidden pointer-events-none transform-gpu will-change-transform",
        theme === 'light' ? "bg-[#fcfbf8]" : "bg-black",
        className
      )}
      style={style}
      {...props}
    >
      <canvas 
        ref={canvasRef} 
        className="block w-full h-full filter blur-[3px] pointer-events-none transform-gpu will-change-transform" // Sharp, distinct shader pillar cones
      />

      {/* Ambient Blue & Red Dual Atmosphere Glow at the bottom on light theme */}
      {theme === 'light' && (
        <div className="absolute inset-x-0 bottom-0 h-[75%] pointer-events-none z-10 overflow-hidden transform-gpu">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/15 via-purple-600/12 to-rose-600/18 [mask-image:linear-gradient(to_top,black_50%,transparent)]" />
        </div>
      )}
      
      {/* Texture Overlay (Soft Holographic Micro-grain) */}
      <div 
        className={cn(
          "absolute inset-0 z-15 pointer-events-none",
          theme === 'light' ? "opacity-3" : "opacity-20"
        )}
        style={{
            backgroundImage: theme === 'light'
              ? "linear-gradient(rgba(0,0,0,0) 50%, rgba(0,0,0,0.03) 50%), linear-gradient(90deg, rgba(29,78,216,0.04), rgba(147,51,234,0.03), rgba(225,29,72,0.04))"
              : "linear-gradient(rgba(0,0,0,0) 50%, rgba(0,0,0,1) 50%), linear-gradient(90deg, rgba(255,0,0,0.06), rgba(0,255,0,0.02), rgba(0,0,255,0.06))",
            backgroundSize: "100% 4px, 3px 100%"
        }}
      />
      
      {/* Vignette */}
      <div className={cn(
        "absolute inset-0 z-20",
        theme === 'light'
          ? "bg-[radial-gradient(circle_at_center,transparent_0%,rgba(252,251,248,0.35)_100%)]"
          : "bg-[radial-gradient(circle_at_center,transparent_0%,#000_100%)]"
      )} />
    </div>
  );
};

export default HolographicBeams;
