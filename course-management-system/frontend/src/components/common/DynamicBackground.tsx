import React, { useEffect, useMemo, useRef } from 'react';

interface DynamicBackgroundProps {
  className?: string;
  /** Approximate number of points per 100,000 pixels of area */
  density?: number; // default 0.12
  /** Base speed multiplier */
  speed?: number; // default 1
  /** Max connection distance in pixels (CSS pixels) */
  lineMaxDist?: number; // default 140
  /** Max triangle distance (stricter than line) */
  triMaxDist?: number; // default 90
  /** Base opacity for strokes/fills */
  opacity?: number; // default 0.6
  /** Dot radius in CSS pixels */
  dotSize?: number; // default 1.6
}

// Utility: get current theme (light/dark)
function getTheme(): 'light' | 'dark' {
  const fromAttr = document.documentElement.getAttribute('data-theme');
  if (fromAttr === 'dark') return 'dark';
  if (fromAttr === 'light') return 'light';
  // fallback to media query
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

const DynamicBackground: React.FC<DynamicBackgroundProps> = ({
  className,
  density = 0.12,
  speed = 1,
  lineMaxDist = 140,
  triMaxDist = 90,
  opacity = 0.6,
  dotSize = 1.6,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const rafRef = useRef<number | null>(null);
  const pointsRef = useRef<{
    x: number;
    y: number;
    vx: number;
    vy: number;
  }[]>([]);
  const themeRef = useRef<'light' | 'dark'>(getTheme());
  const reducedMotion = useMemo(
    () => window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    []
  );

  useEffect(() => {
    themeRef.current = getTheme();
    const listener = () => {
      themeRef.current = getTheme();
    };
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener?.('change', listener);
    const observer = new MutationObserver(listener);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    return () => {
      mq.removeEventListener?.('change', listener);
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    const container = containerRef.current!;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = 0;
    let height = 0;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);

    function resize() {
      const rect = container.getBoundingClientRect();
      width = Math.floor(rect.width);
      height = Math.floor(rect.height);
      canvas.width = Math.max(1, Math.floor(width * dpr));
      canvas.height = Math.max(1, Math.floor(height * dpr));
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      initPoints();
    }

    function initPoints() {
      const area = width * height;
      const count = Math.max(20, Math.floor((area / 100000) * density * 100)); // scaled for reasonable counts
      const pts: { x: number; y: number; vx: number; vy: number }[] = [];
      for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speedBase = (0.15 + Math.random() * 0.35) * speed; // 0.15~0.5
        pts.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: Math.cos(angle) * speedBase,
          vy: Math.sin(angle) * speedBase,
        });
      }
      pointsRef.current = pts;
    }

    let lastTime = performance.now();

    function step(now: number) {
      const dt = Math.min(40, now - lastTime) / 16.6667; // clamp ~24fps min dt for stability
      lastTime = now;
      draw(dt);
      rafRef.current = requestAnimationFrame(step);
    }

    function draw(dt: number) {
      const pts = pointsRef.current;
      if (!pts.length) return;

      // clear with subtle fade to create motion trails when reducedMotion is false
      ctx.clearRect(0, 0, width, height);

      // theme-aware colors
      const dark = themeRef.current === 'dark';
      const dot = dark ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.9)';
      const line = dark ? `rgba(180,200,255,${opacity})` : `rgba(0,40,120,${opacity * 0.75})`;
      const tri = dark ? 'rgba(120,160,255,0.06)' : 'rgba(24,144,255,0.06)';

      const maxLineDist = lineMaxDist;
      const maxTriDist = triMaxDist;

      // update positions
      if (!reducedMotion) {
        for (const p of pts) {
          p.x += p.vx * dt;
          p.y += p.vy * dt;
          if (p.x <= 0 || p.x >= width) p.vx *= -1;
          if (p.y <= 0 || p.y >= height) p.vy *= -1;
          p.x = Math.max(0, Math.min(width, p.x));
          p.y = Math.max(0, Math.min(height, p.y));
        }
      }

      // draw lines and collect nearest neighbors
      ctx.lineWidth = 1;
      for (let i = 0; i < pts.length; i++) {
        const a = pts[i];
        // nearest two for triangle fill
        let n1 = -1, n2 = -1, d1 = Infinity, d2 = Infinity;
        for (let j = i + 1; j < pts.length; j++) {
          const b = pts[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.hypot(dx, dy);
          if (dist < maxLineDist) {
            const alpha = Math.max(0, 1 - dist / maxLineDist);
            ctx.strokeStyle = line.replace(/\d?\.\d+\)$/,(m)=>`${(alpha * opacity).toFixed(3)})`);
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
          if (dist < maxTriDist) {
            if (dist < d1) {
              d2 = d1; n2 = n1; d1 = dist; n1 = j;
            } else if (dist < d2) {
              d2 = dist; n2 = j;
            }
          }
        }
        // draw subtle triangle
        if (n1 !== -1 && n2 !== -1) {
          const b = pts[n1];
          const c = pts[n2];
          const avgDist = (d1 + d2) / 2;
          const tAlpha = Math.max(0, 1 - avgDist / maxTriDist) * 0.6; // softer
          if (tAlpha > 0.02) {
            ctx.fillStyle = tri.replace(/\d?\.\d+\)$/,(m)=>`${tAlpha.toFixed(3)})`);
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.lineTo(c.x, c.y);
            ctx.closePath();
            ctx.fill();
          }
        }
      }

      // draw dots on top
      ctx.fillStyle = dot;
      for (const p of pts) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, dotSize, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    const onResize = () => resize();
    resize();
    rafRef.current = requestAnimationFrame(step);
    window.addEventListener('resize', onResize);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      window.removeEventListener('resize', onResize);
    };
  }, [density, speed, lineMaxDist, triMaxDist, opacity, dotSize, reducedMotion]);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      <canvas ref={canvasRef} />
    </div>
  );
};

export default DynamicBackground;

