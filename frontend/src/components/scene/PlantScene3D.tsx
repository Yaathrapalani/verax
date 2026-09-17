import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import type { InspectionMode } from '../../types/plant';
import { REPRESENTATIVE_CDU_EQUIPMENT } from '../../data/representativePlant';

interface PlantScene2DProps {
  selectedAssetTag: string;
  setSelectedAssetTag: (tag: string) => void;
  inspectionMode: InspectionMode;
  scenario: 'normal' | 'disturbed';
}

export const PlantScene3D: React.FC<PlantScene2DProps> = ({
  selectedAssetTag,
  setSelectedAssetTag,
  inspectionMode,
  scenario,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene & Camera Setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x071018);
    scene.fog = new THREE.FogExp2(0x071018, 0.015);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    // Elevated isometric angle looking down at CDU preheat train
    camera.position.set(10, 18, 30);
    camera.lookAt(10, 2, 0);

    // 2. Renderer Setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // 3. Industrial Neutral Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(20, 40, 20);
    dirLight.castShadow = true;
    scene.add(dirLight);

    const rimLight = new THREE.DirectionalLight(0x27b7e8, 0.5);
    rimLight.position.set(-20, 20, -20);
    scene.add(rimLight);

    // 4. Industrial Floor / Ground Grid & Structural Pipe Rack
    const gridHelper = new THREE.GridHelper(100, 50, 0x15212d, 0x0e1722);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    // Structural Pipe Rack Beams (Metal Gray)
    const rackMat = new THREE.MeshStandardMaterial({ color: 0x1b2838, roughness: 0.7, metalness: 0.8 });
    for (let x = -15; x <= 35; x += 10) {
      const pillarGeo = new THREE.BoxGeometry(0.3, 5, 0.3);
      const p1 = new THREE.Mesh(pillarGeo, rackMat);
      p1.position.set(x, 2.5, -4);
      scene.add(p1);
      const p2 = new THREE.Mesh(pillarGeo, rackMat);
      p2.position.set(x, 2.5, 4);
      scene.add(p2);
    }

    // Main Crude Line Pipe
    const crudePipeGeo = new THREE.CylinderGeometry(0.25, 0.25, 52, 16);
    const crudePipeMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.4, metalness: 0.8 });
    const crudePipe = new THREE.Mesh(crudePipeGeo, crudePipeMat);
    crudePipe.rotation.z = Math.PI / 2;
    crudePipe.position.set(9, 1.2, 0);
    scene.add(crudePipe);

    // 5. Equipment Mesh Generators
    const equipmentGroup = new THREE.Group();

    const matSteel = new THREE.MeshStandardMaterial({ color: 0x3a4b5c, roughness: 0.5, metalness: 0.7 });
    const matExchangerShell = new THREE.MeshStandardMaterial({ color: 0x2a3848, roughness: 0.4, metalness: 0.8 });
    const matAttention = new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.3, metalness: 0.6 });
    const matNominal = new THREE.MeshStandardMaterial({ color: 0x065f46, roughness: 0.3, metalness: 0.6 });

    REPRESENTATIVE_CDU_EQUIPMENT.forEach((eq) => {
      const eqContainer = new THREE.Group();
      eqContainer.position.set(...eq.position);

      if (eq.category === 'EXCHANGER') {
        // Realistic Shell & Tube Geometry
        const shellLength = eq.scale ? eq.scale[0] : 2.2;
        const shellRadius = eq.scale ? eq.scale[1] / 2 : 0.6;

        // Main Cylindrical Shell
        const shellGeo = new THREE.CylinderGeometry(shellRadius, shellRadius, shellLength, 32);
        const isSelected = selectedAssetTag === eq.datasetTag || selectedAssetTag === eq.tag;
        const isAttn = (eq.datasetTag === 'E02' && (scenario === 'disturbed' || eq.status === 'ATTENTION'));
        
        let shellMat = matExchangerShell.clone();
        if (isSelected) {
          shellMat.color.setHex(0x0284c7);
        } else if (isAttn) {
          shellMat.color.setHex(0x7f1d1d);
        }

        const shellMesh = new THREE.Mesh(shellGeo, shellMat);
        shellMesh.rotation.z = Math.PI / 2;
        eqContainer.add(shellMesh);

        // Channel Head & Rear Head (Dished Domes)
        const domeGeo = new THREE.SphereGeometry(shellRadius, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2);
        const head1 = new THREE.Mesh(domeGeo, shellMat);
        head1.rotation.z = -Math.PI / 2;
        head1.position.x = shellLength / 2;
        eqContainer.add(head1);

        const head2 = new THREE.Mesh(domeGeo, shellMat);
        head2.rotation.z = Math.PI / 2;
        head2.position.x = -shellLength / 2;
        eqContainer.add(head2);

        // Support Saddles
        const saddleGeo = new THREE.BoxGeometry(0.2, 0.6, shellRadius * 2.2);
        const saddle1 = new THREE.Mesh(saddleGeo, matSteel);
        saddle1.position.set(shellLength * 0.25, -0.4, 0);
        eqContainer.add(saddle1);
        const saddle2 = new THREE.Mesh(saddleGeo, matSteel);
        saddle2.position.set(-shellLength * 0.25, -0.4, 0);
        eqContainer.add(saddle2);

        // Status Ring Indicator
        const ringGeo = new THREE.TorusGeometry(shellRadius + 0.05, 0.03, 16, 32);
        const ringMat = isAttn ? matAttention : matNominal;
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.y = Math.PI / 2;
        eqContainer.add(ring);

        // Cutaway Tube Bundle (If Cutaway Inspection Mode active for selected exchanger)
        if (inspectionMode === 'CUTAWAY' && isSelected) {
          const innerTubeMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.3, metalness: 0.9 });
          for (let r = -0.3; r <= 0.3; r += 0.15) {
            for (let c = -0.3; c <= 0.3; c += 0.15) {
              const tubeGeo = new THREE.CylinderGeometry(0.04, 0.04, shellLength * 0.9, 8);
              const tubeMesh = new THREE.Mesh(tubeGeo, innerTubeMat);
              tubeMesh.rotation.z = Math.PI / 2;
              tubeMesh.position.set(0, r, c);
              eqContainer.add(tubeMesh);
            }
          }
        }
      } else if (eq.category === 'PUMP') {
        const pumpGeo = new THREE.BoxGeometry(1.2, 0.8, 1.2);
        const pumpMesh = new THREE.Mesh(pumpGeo, matSteel);
        eqContainer.add(pumpMesh);
      } else if (eq.category === 'DESALTER' || eq.category === 'FLASH_DRUM') {
        const vesLength = eq.scale ? eq.scale[1] : 3.0;
        const vesRad = eq.scale ? eq.scale[0] / 2 : 1.0;
        const vesGeo = new THREE.CylinderGeometry(vesRad, vesRad, vesLength, 24);
        const vesMesh = new THREE.Mesh(vesGeo, matSteel);
        eqContainer.add(vesMesh);
      } else if (eq.category === 'FURNACE') {
        const furnGeo = new THREE.BoxGeometry(3.5, 4.0, 3.5);
        const furnMesh = new THREE.Mesh(furnGeo, new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.6 }));
        eqContainer.add(furnMesh);
        // Chimney Stack
        const stackGeo = new THREE.CylinderGeometry(0.4, 0.4, 4.0, 16);
        const stackMesh = new THREE.Mesh(stackGeo, matSteel);
        stackMesh.position.set(0, 4.0, 0);
        eqContainer.add(stackMesh);
      } else if (eq.category === 'COLUMN') {
        const colGeo = new THREE.CylinderGeometry(1.25, 1.25, 12, 32);
        const colMesh = new THREE.Mesh(colGeo, new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.3, metalness: 0.8 }));
        eqContainer.add(colMesh);
      }

      equipmentGroup.add(eqContainer);
    });

    scene.add(equipmentGroup);

    // 6. Camera Animation & Smooth Target Focusing
    let animationFrameId: number;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      // Smooth camera focus if equipment selected
      if (selectedAssetTag) {
        const targetEq = REPRESENTATIVE_CDU_EQUIPMENT.find(
          (e) => e.datasetTag === selectedAssetTag || e.tag === selectedAssetTag
        );
        if (targetEq) {
          const targetPos = new THREE.Vector3(...targetEq.position);
          if (inspectionMode === 'CUTAWAY') {
            camera.position.lerp(new THREE.Vector3(targetPos.x, targetPos.y + 2, targetPos.z + 5), 0.05);
            camera.lookAt(targetPos);
          } else if (inspectionMode === 'PROCESS') {
            camera.position.lerp(new THREE.Vector3(10, 35, 1), 0.05);
            camera.lookAt(10, 0, 0);
          } else {
            camera.position.lerp(new THREE.Vector3(targetPos.x, targetPos.y + 6, targetPos.z + 12), 0.05);
            camera.lookAt(targetPos);
          }
        }
      }

      renderer.render(scene, camera);
    };

    animate();

    // Handle Resize
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [selectedAssetTag, inspectionMode, scenario]);

  return (
    <div className="relative w-full h-full bg-[#071018] overflow-hidden">
      {/* 3D WebGL Canvas Container */}
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Floating Equipment Tag Labels Overlay */}
      <div className="absolute top-4 left-4 z-10 pointer-events-none flex flex-wrap gap-2 text-[10px] font-mono">
        {REPRESENTATIVE_CDU_EQUIPMENT.filter((e) => e.isMonitoredByFoulX).map((eq) => {
          const isSelected = selectedAssetTag === eq.datasetTag || selectedAssetTag === eq.tag;
          const isAttn = eq.datasetTag === 'E02' && (scenario === 'disturbed' || eq.status === 'ATTENTION');
          return (
            <div
              key={eq.tag}
              onClick={() => setSelectedAssetTag(eq.datasetTag || eq.tag)}
              className={`pointer-events-auto px-2.5 py-1 rounded border shadow-lg transition cursor-pointer flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-[#0284c7] text-white border-[#38bdf8] font-bold'
                  : isAttn
                  ? 'bg-[#7f1d1d] text-[#fca5a5] border-[#ef4444] font-bold'
                  : 'bg-[#0b1118]/90 text-[#9ca3af] border-[#1b2a3a] hover:text-white'
              }`}
            >
              <span>{eq.tag}</span>
              {isAttn && <span className="w-2 h-2 rounded-full bg-[#f87171] animate-pulse"></span>}
            </div>
          );
        })}
      </div>
    </div>
  );
};
