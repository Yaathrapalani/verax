/**
 * PLANT-X 3D Scene Compiler.
 * 
 * Compiles canonical plant graph topology and solved spatial arrangements
 * into a renderable 3D scene representation with canonical IDs,
 * representative geometry tags, and quality level metadata.
 * 
 * Architecture:
 * PlantGraph -> SceneCompiler -> SceneGraph -> Renderer.
 * 3D never becomes the source of engineering truth.
 */

import type { SolvedSpatialLayout } from './spatialSolver';
import { ProceduralEquipmentLibrary } from './proceduralLibrary';
import type { ProceduralGeometryParams } from './proceduralLibrary';

export interface CompiledSceneNode {
  canonicalId: string;
  tag: string;
  type: string;
  position: [number, number, number];
  rotation: [number, number, number];
  geometry: ProceduralGeometryParams;
  truthState: string;
  representationState: string;
}

export interface CompiledScenePipe {
  streamTag: string;
  points: Array<[number, number, number]>;
  truthState: string;
}

export interface CompiledPlantScene {
  sceneId: string;
  qualityLevel: string;
  isRepresentative: boolean;
  truthDisclaimer: string;
  nodes: CompiledSceneNode[];
  pipes: CompiledScenePipe[];
}

export class SceneCompiler {
  public static compile(spatialLayout: SolvedSpatialLayout): CompiledPlantScene {
    const nodes: CompiledSceneNode[] = spatialLayout.equipmentPlacements.map(eq => ({
      canonicalId: `node_${eq.tag}`,
      tag: eq.tag,
      type: eq.type,
      position: eq.position,
      rotation: eq.rotation,
      geometry: ProceduralEquipmentLibrary.getEquipmentGeometry(eq.type, eq.tag),
      truthState: 'REPRESENTATIVE',
      representationState: 'PARAMETRIC_3D_L2',
    }));

    const pipes: CompiledScenePipe[] = spatialLayout.pipeSegments.map(pipe => ({
      streamTag: pipe.streamTag,
      points: pipe.points,
      truthState: 'REPRESENTATIVE',
    }));

    return {
      sceneId: `scene_${spatialLayout.documentId}`,
      qualityLevel: spatialLayout.qualityLevel,
      isRepresentative: spatialLayout.isRepresentative,
      truthDisclaimer: 'REPRESENTATIVE PROCESS TOPOLOGY — SYNTHETIC / ILLUSTRATIVE (NOT VALIDATED PLANT CAD)',
      nodes,
      pipes,
    };
  }
}
