import React, { useEffect, useRef } from 'react';

interface ScrollCanvasProps {
  frameCount?: number;
}

export const ScrollCanvas: React.FC<ScrollCanvasProps> = ({ frameCount = 285 }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const pad = (n: number, width: number) => {
      let s = n + '';
      while (s.length < width) s = '0' + s;
      return s;
    };

    const currentFrameUrl = (index: number) => `/frames/ezgif-frame-${pad(index, 3)}.jpg`;
    const images: HTMLImageElement[] = new Array(frameCount);

    let currentProgressFrame = 1;
    let targetFrame = 1;
    let smoothFrame = 1;
    let animationFrameId: number;

    const render = (frameIndex: number) => {
      const idx = Math.min(frameCount, Math.max(1, frameIndex));
      const img = images[idx - 1];
      if (!img || !img.complete || img.naturalWidth === 0) return;

      const cw = canvas.width;
      const ch = canvas.height;
      const iw = img.naturalWidth;
      const ih = img.naturalHeight;

      // Fit / Cover scaling
      const scale = Math.max(cw / iw, ch / ih);
      const nw = iw * scale;
      const nh = ih * scale;
      const cx = (cw - nw) / 2;
      const cy = (ch - nh) / 2;

      ctx.clearRect(0, 0, cw, ch);
      ctx.drawImage(img, cx, cy, nw, nh);
    };

    const resizeCanvas = () => {
      canvas.width = window.innerWidth * (window.devicePixelRatio || 1);
      canvas.height = window.innerHeight * (window.devicePixelRatio || 1);
      render(currentProgressFrame);
    };

    const updateTargetFrame = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
      const maxScroll = (document.documentElement.scrollHeight || document.body.scrollHeight) - window.innerHeight;
      const scrollFraction = maxScroll > 0 ? Math.min(Math.max(scrollTop / maxScroll, 0), 1) : 0;
      targetFrame = Math.min(frameCount, Math.max(1, Math.round(scrollFraction * (frameCount - 1)) + 1));
    };

    const loop = () => {
      const diff = targetFrame - smoothFrame;
      if (Math.abs(diff) < 0.05) {
        smoothFrame = targetFrame;
      } else {
        smoothFrame += diff * 0.2;
      }

      const frameToDraw = Math.round(smoothFrame);
      if (frameToDraw !== currentProgressFrame) {
        currentProgressFrame = frameToDraw;
        render(frameToDraw);
      }

      animationFrameId = requestAnimationFrame(loop);
    };

    // Preload frames
    for (let i = 1; i <= frameCount; i++) {
      const img = new Image();
      img.src = currentFrameUrl(i);
      img.onload = () => {
        if (i === 1) render(1);
      };
      images[i - 1] = img;
    }

    window.addEventListener('resize', resizeCanvas);
    window.addEventListener('scroll', updateTargetFrame, { passive: true });

    resizeCanvas();
    updateTargetFrame();
    smoothFrame = targetFrame;
    animationFrameId = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      window.removeEventListener('scroll', updateTargetFrame);
      cancelAnimationFrame(animationFrameId);
    };
  }, [frameCount]);

  return (
    <div className="fixed inset-0 w-screen h-screen pointer-events-none z-0 overflow-hidden">
      <canvas 
        ref={canvasRef} 
        className="w-full h-full block" 
      />
      {/* Crystal clear transparent view - subtle vignette only to ensure text pop without masking the video animation */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-black/40 pointer-events-none" />
    </div>
  );
};