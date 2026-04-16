import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface GeoGlobeProps {
  mode: 'quiz' | 'explore' | 'challenge';
  highlightCountry?: string;
  onCountryClick?: (country: string) => void;
}

export function GeoGlobe({ mode, highlightCountry, onCountryClick }: GeoGlobeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const globeRef = useRef<THREE.Mesh | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const isVisibleRef = useRef(true);
  const frameCountRef = useRef(0);
  const sampleStartRef = useRef<number | null>(null);
  const visibleMsRef = useRef(0);
  const hiddenMsRef = useRef(0);
  const pauseReasonRef = useRef<'none' | 'hidden' | 'viewport'>('none');

  useEffect(() => {
    if (!canvasRef.current) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000814);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(
      75,
      canvasRef.current.clientWidth / canvasRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 5;
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      antialias: true,
      powerPreference: 'low-power',
    });
    const pixelRatio = Math.min(window.devicePixelRatio || 1, 1.5);
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(canvasRef.current.clientWidth, canvasRef.current.clientHeight, false);
    rendererRef.current = renderer;

    const geometry = new THREE.SphereGeometry(2, 32, 24);
    const material = new THREE.MeshPhongMaterial({
      color: 0x2c5f2d,
      emissive: 0x112211,
      shininess: 25,
    });

    const globe = new THREE.Mesh(geometry, material);
    scene.add(globe);
    globeRef.current = globe;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    const animate = () => {
      const now = performance.now();
      if (sampleStartRef.current === null) sampleStartRef.current = now;
      animationFrameRef.current = requestAnimationFrame(animate);

      if (globeRef.current) globeRef.current.rotation.y += 0.002;
      renderer.render(scene, camera);

      frameCountRef.current += 1;
      const elapsed = now - sampleStartRef.current;
      if (elapsed >= 2000) {
        const fps = (frameCountRef.current * 1000) / elapsed;
        console.info(
          `[GeoGlobe] fps=${fps.toFixed(1)} visible=${(visibleMsRef.current / 1000).toFixed(1)}s hidden=${(hiddenMsRef.current / 1000).toFixed(1)}s pixelRatio=${renderer.getPixelRatio()} pause=${pauseReasonRef.current}`
        );
        frameCountRef.current = 0;
        sampleStartRef.current = now;
        visibleMsRef.current = 0;
        hiddenMsRef.current = 0;
      }
    };

    const stopAnimation = (reason: 'hidden' | 'viewport') => {
      pauseReasonRef.current = reason;
      sampleStartRef.current = null;
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };

    const startAnimation = () => {
      pauseReasonRef.current = 'none';
      if (animationFrameRef.current === null && !document.hidden && isVisibleRef.current) {
        animate();
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        stopAnimation('hidden');
        return;
      }
      startAnimation();
    };

    const intersectionObserver = new IntersectionObserver(
      ([entry]) => {
        isVisibleRef.current = entry.isIntersecting;
        if (!entry.isIntersecting) {
          stopAnimation('viewport');
          return;
        }
        startAnimation();
      },
      { threshold: 0.1 }
    );

    intersectionObserver.observe(canvasRef.current);

    const handleResize = () => {
      if (!canvasRef.current || !cameraRef.current || !rendererRef.current) return;
      const width = canvasRef.current.clientWidth;
      const height = canvasRef.current.clientHeight;
      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, height, false);
    };

    const perfTick = window.setInterval(() => {
      if (document.hidden || !isVisibleRef.current) {
        hiddenMsRef.current += 1000;
      } else {
        visibleMsRef.current += 1000;
      }
    }, 1000);

    window.addEventListener('resize', handleResize);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    startAnimation();

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      window.clearInterval(perfTick);
      window.removeEventListener('resize', handleResize);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      intersectionObserver.disconnect();
      rendererRef.current?.dispose();
      sceneRef.current = null;
      cameraRef.current = null;
      globeRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (highlightCountry && globeRef.current) {
      console.log(`Highlighting country: ${highlightCountry}`);
    }
  }, [highlightCountry]);

  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      if (!canvasRef.current || !onCountryClick) return;
      console.log('Globe clicked', event);
    };

    if (canvasRef.current) {
      canvasRef.current.addEventListener('click', handleClick);
    }

    return () => {
      if (canvasRef.current) {
        canvasRef.current.removeEventListener('click', handleClick);
      }
    };
  }, [onCountryClick]);

  return (
    <div className="w-full h-full relative">
      <canvas ref={canvasRef} className="w-full h-full" />
      <div className="absolute top-4 left-4 bg-black/70 text-white px-4 py-2 rounded-lg">
        <div className="text-sm font-bold">🌍 GeoMaster Globe</div>
        <div className="text-xs opacity-70">Mode: {mode}</div>
        <div className="text-xs opacity-70">Telemetry: dev FPS sample in console</div>
      </div>
    </div>
  );
}
