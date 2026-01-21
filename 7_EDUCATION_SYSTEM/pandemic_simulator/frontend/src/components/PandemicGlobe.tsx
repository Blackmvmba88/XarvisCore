/**
 * PandemicGlobe Component
 * 3D visualization of pandemic spread (simplified placeholder)
 * BlackMamba University - Pandemic Simulator
 */

import React, { useRef, useEffect } from 'react';

interface PandemicGlobeProps {
  infectionLevel: number; // 0.0 to 1.0
}

export function PandemicGlobe({ infectionLevel }: PandemicGlobeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Clear canvas
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw earth (simplified)
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.35;

    // Background space
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw stars
    for (let i = 0; i < 100; i++) {
      const x = Math.random() * canvas.width;
      const y = Math.random() * canvas.height;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.fillRect(x, y, 1, 1);
    }

    // Draw globe base
    const gradient = ctx.createRadialGradient(
      centerX - radius * 0.3,
      centerY - radius * 0.3,
      radius * 0.1,
      centerX,
      centerY,
      radius
    );
    gradient.addColorStop(0, '#2563eb');
    gradient.addColorStop(0.5, '#1e40af');
    gradient.addColorStop(1, '#1e3a8a');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fill();

    // Draw infection overlay
    if (infectionLevel > 0) {
      const infectionGradient = ctx.createRadialGradient(
        centerX,
        centerY,
        radius * 0.5,
        centerX,
        centerY,
        radius
      );
      infectionGradient.addColorStop(0, `rgba(239, 68, 68, ${infectionLevel * 0.5})`);
      infectionGradient.addColorStop(1, `rgba(220, 38, 38, ${infectionLevel * 0.3})`);
      
      ctx.fillStyle = infectionGradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    
    // Latitude lines
    for (let i = 0; i < 5; i++) {
      const y = centerY - radius + (radius * 2 * i / 4);
      ctx.beginPath();
      const width = Math.sqrt(radius * radius - Math.pow(y - centerY, 2)) * 2;
      ctx.ellipse(centerX, y, width / 2, 10, 0, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Longitude lines
    for (let i = 0; i < 8; i++) {
      ctx.beginPath();
      ctx.ellipse(centerX, centerY, radius * Math.abs(Math.cos(i * Math.PI / 8)), radius, 0, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Add glow effect
    ctx.shadowBlur = 20;
    ctx.shadowColor = infectionLevel > 0.5 ? 'rgba(239, 68, 68, 0.5)' : 'rgba(37, 99, 235, 0.5)';
    ctx.strokeStyle = infectionLevel > 0.5 ? '#ef4444' : '#2563eb';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.stroke();

  }, [infectionLevel]);

  return (
    <div className="relative w-full h-full flex items-center justify-center bg-black">
      <canvas 
        ref={canvasRef}
        className="w-full h-full"
        style={{ maxWidth: '800px', maxHeight: '800px' }}
      />
      
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
        <h1 className="text-5xl font-bold text-green-400 mb-2 drop-shadow-2xl">
          🦠 Pandemic Simulator
        </h1>
        <p className="text-xl text-gray-400 drop-shadow-lg">
          BlackMamba University
        </p>
      </div>

      {infectionLevel > 0.7 && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-red-900/80 backdrop-blur-md border border-red-500 rounded-lg px-6 py-3">
          <p className="text-red-200 font-bold text-lg">
            ⚠️ Crisis Pandémica Global
          </p>
        </div>
      )}
    </div>
  );
}

export default PandemicGlobe;
