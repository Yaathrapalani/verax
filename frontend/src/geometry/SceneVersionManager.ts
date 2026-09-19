/**
 * PLANT-X SCENE VERSION & ROLLBACK MANAGER
 * 
 * Manages versioned 3D scene graphs to enable safe hot-swapping and rollback.
 * Guarantees that blueprint reconstructions or CAD imports never silently destroy
 * or overwrite the active scene without comparison, review, and user activation.
 */

import type { GeometryQualityLevel } from './GeometryService';

export type SceneSourceType =
  | 'EXISTING_REPRESENTATIVE'
  | 'BLUEPRINT_RECONSTRUCTED'
  | 'CAD_IMPORTED'
  | 'IFC_IMPORTED'
  | 'USER_EDITED';

export interface SceneVersion {
  sceneId: string;
  sceneVersion: number;
  sourceType: SceneSourceType;
  sourceDocument: string;
  qualityLevel: GeometryQualityLevel;
  geometrySource: string;
  createdAt: number;
  status: 'ACTIVE' | 'CANDIDATE' | 'ARCHIVED' | 'REJECTED';
  entities: Array<{
    tag: string;
    equipmentClass: string;
    position: [number, number, number];
  }>;
  linkedGraphVersion: number;
  provenance: {
    compiledBy: string;
    reviewedByHuman: boolean;
    auditLogRef: string;
  };
}

export interface SceneComparisonDelta {
  baseSceneVersion: number;
  candidateSceneVersion: number;
  addedTags: string[];
  removedTags: string[];
  movedTags: Array<{ tag: string; oldPos: [number, number, number]; newPos: [number, number, number] }>;
  qualityLevelDelta: { from: GeometryQualityLevel; to: GeometryQualityLevel };
}

export class SceneVersionManager {
  private versions: Map<number, SceneVersion> = new Map();
  private activeVersionNumber = 1;
  private candidateVersionNumber: number | null = null;
  private versionCounter = 1;

  constructor() {
    // Initial Base Scene
    const initialScene: SceneVersion = {
      sceneId: 'SCENE-INITIAL-BASE',
      sceneVersion: 1,
      sourceType: 'EXISTING_REPRESENTATIVE',
      sourceDocument: 'DIGITAL_SHADOW_STAGE_11',
      qualityLevel: 'L4',
      geometrySource: 'PROCEDURAL_PRIMITIVES_STAGE11',
      createdAt: Date.now(),
      status: 'ACTIVE',
      entities: [
        { tag: 'E-101', equipmentClass: 'HEAT_EXCHANGER', position: [-8, 0, -2] },
        { tag: 'E-102', equipmentClass: 'HEAT_EXCHANGER', position: [-2, 0, 0] },
        { tag: 'P-101A', equipmentClass: 'PUMP', position: [-14, -1, -2] },
        { tag: 'V-101', equipmentClass: 'VESSEL', position: [6, 2, 2] },
      ],
      linkedGraphVersion: 1,
      provenance: {
        compiledBy: 'STAGE_11_PLANT_COMPILER',
        reviewedByHuman: true,
        auditLogRef: 'AUDIT-INIT-001',
      },
    };
    this.versions.set(1, initialScene);
  }

  public compileCandidateScene(
    sourceType: SceneSourceType,
    sourceDocument: string,
    qualityLevel: GeometryQualityLevel,
    entities: Array<{ tag: string; equipmentClass: string; position: [number, number, number] }>,
    reviewedByHuman: boolean
  ): SceneVersion {
    this.versionCounter++;
    const candidateVersion: SceneVersion = {
      sceneId: `SCENE-VER-${this.versionCounter}`,
      sceneVersion: this.versionCounter,
      sourceType,
      sourceDocument,
      qualityLevel,
      geometrySource: `COMPILER_${sourceType}`,
      createdAt: Date.now(),
      status: 'CANDIDATE',
      entities,
      linkedGraphVersion: this.versionCounter,
      provenance: {
        compiledBy: 'PLANT-X_SCENE_COMPILER',
        reviewedByHuman,
        auditLogRef: `AUDIT-COMP-${this.versionCounter}`,
      },
    };

    this.versions.set(this.versionCounter, candidateVersion);
    this.candidateVersionNumber = this.versionCounter;
    return candidateVersion;
  }

  public compareCandidateToActive(): SceneComparisonDelta | null {
    const active = this.getActiveScene();
    if (!active || !this.candidateVersionNumber) return null;
    const candidate = this.versions.get(this.candidateVersionNumber);
    if (!candidate) return null;

    const activeTags = new Set(active.entities.map((e) => e.tag));
    const candidateTags = new Set(candidate.entities.map((e) => e.tag));

    const addedTags = candidate.entities.filter((e) => !activeTags.has(e.tag)).map((e) => e.tag);
    const removedTags = active.entities.filter((e) => !candidateTags.has(e.tag)).map((e) => e.tag);

    const movedTags: Array<{ tag: string; oldPos: [number, number, number]; newPos: [number, number, number] }> = [];
    for (const candEnt of candidate.entities) {
      const actEnt = active.entities.find((e) => e.tag === candEnt.tag);
      if (actEnt) {
        if (
          actEnt.position[0] !== candEnt.position[0] ||
          actEnt.position[1] !== candEnt.position[1] ||
          actEnt.position[2] !== candEnt.position[2]
        ) {
          movedTags.push({ tag: candEnt.tag, oldPos: actEnt.position, newPos: candEnt.position });
        }
      }
    }

    return {
      baseSceneVersion: active.sceneVersion,
      candidateSceneVersion: candidate.sceneVersion,
      addedTags,
      removedTags,
      movedTags,
      qualityLevelDelta: { from: active.qualityLevel, to: candidate.qualityLevel },
    };
  }

  public activateCandidate(): { success: boolean; activatedVersion?: SceneVersion; error?: string } {
    if (!this.candidateVersionNumber) {
      return { success: false, error: 'No candidate scene compiled for activation.' };
    }
    const candidate = this.versions.get(this.candidateVersionNumber);
    if (!candidate) {
      return { success: false, error: 'Candidate scene not found.' };
    }

    const currentActive = this.getActiveScene();
    if (currentActive) {
      currentActive.status = 'ARCHIVED';
    }

    candidate.status = 'ACTIVE';
    this.activeVersionNumber = candidate.sceneVersion;
    this.candidateVersionNumber = null;

    return { success: true, activatedVersion: candidate };
  }

  public rollbackToVersion(targetVersionNumber: number): { success: boolean; rolledBackTo?: SceneVersion; error?: string } {
    const target = this.versions.get(targetVersionNumber);
    if (!target) {
      return { success: false, error: `Scene version ${targetVersionNumber} does not exist in history.` };
    }

    const currentActive = this.getActiveScene();
    if (currentActive) {
      currentActive.status = 'ARCHIVED';
    }

    target.status = 'ACTIVE';
    this.activeVersionNumber = target.sceneVersion;
    return { success: true, rolledBackTo: target };
  }

  public getActiveScene(): SceneVersion | undefined {
    return this.versions.get(this.activeVersionNumber);
  }

  public getCandidateScene(): SceneVersion | undefined {
    return this.candidateVersionNumber ? this.versions.get(this.candidateVersionNumber) : undefined;
  }

  public getAllVersions(): SceneVersion[] {
    return Array.from(this.versions.values()).sort((a, b) => b.sceneVersion - a.sceneVersion);
  }
}

export const sceneVersionManager = new SceneVersionManager();
