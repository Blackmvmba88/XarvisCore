import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface GeoGlobeProps {
  mode: 'quiz' | 'explore' | 'challenge';
  highlightCountry?: string;
  onCountryClick?: (country: string) => void;
}

/**
 * GeoGlobe Component
 * 
 * Renders an interactive 3D globe using Three.js
 * Integrates with the quiz system to highlight countries
 * 
 * @param mode - Current mode (quiz, explore, challenge)
 * @param highlightCountry - Country code to highlight
 * @param onCountryClick - Callback when a country is clicked
 */
export function GeoGlobe({ mode, highlightCountry, onCountryClick }: GeoGlobeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const globeRef = useRef<THREE.Mesh | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialize Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000814);
    sceneRef.current = scene;

    // Setup camera
    const camera = new THREE.PerspectiveCamera(
      75,
      canvasRef.current.clientWidth / canvasRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 5;
    cameraRef.current = camera;

    // Setup renderer
    const renderer = new THREE.WebGLRenderer({
      canvas: canvasRef.current,
      antialias: true,
    });
    renderer.setSize(canvasRef.current.clientWidth, canvasRef.current.clientHeight);
    rendererRef.current = renderer;

    // Create globe
    const geometry = new THREE.SphereGeometry(2, 64, 64);
    
    // Create a basic material (in production, this would use Earth texture)
    const material = new THREE.MeshPhongMaterial({
      color: 0x2c5f2d,
      emissive: 0x112211,
      shininess: 25,
    });

    const globe = new THREE.Mesh(geometry, material);
    scene.add(globe);
    globeRef.current = globe;

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);

      if (globeRef.current) {
        globeRef.current.rotation.y += 0.002;
      }

      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      if (!canvasRef.current || !cameraRef.current || !rendererRef.current) return;

      const width = canvasRef.current.clientWidth;
      const height = canvasRef.current.clientHeight;

      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (rendererRef.current) {
        rendererRef.current.dispose();
      }
    };
  }, []);

  // Handle country highlighting
  useEffect(() => {
    if (highlightCountry && globeRef.current) {
      // In production, this would highlight the specific country on the globe
      console.log(`Highlighting country: ${highlightCountry}`);
    }
  }, [highlightCountry]);

  // Handle click events
  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      if (!canvasRef.current || !onCountryClick) return;

      // In production, this would use raycasting to detect which country was clicked
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
      </div>
    </div>
  );
}
