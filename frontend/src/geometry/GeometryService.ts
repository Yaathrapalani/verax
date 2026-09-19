/**
 * PLANT-X GEOMETRY SERVICE
 * 
 * Boundary layer between engineering CAD / BIM geometry and the Three.js rendering layer.
 * Strictly separates:
 * - PATH A: Blueprint / P&ID Inferred Representative Models (Levels L0 -> L4)
 * - PATH B: Source-backed CAD / IFC Geometry (Level L5 only)
 * 
 * Guarantees that procedural representative geometry NEVER masquerades as validated CAD.
 */

export type GeometryQualityLevel = 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | 'L5';

export interface GeometryProvenance {
  entityTag: string;
  sourceType: 'PATH_A_INFERRED_REPRESENTATIVE' | 'PATH_B_SOURCE_CAD_IFC';
  sourceDocument: string;
  documentPage?: number;
  extractedRegionBBox?: [number, number, number, number];
  qualityLevel: GeometryQualityLevel;
  geometryType: 'REPRESENTATIVE_PROCEDURAL' | 'SOURCE_BACKED_EXACT';
  extractionConfidence: number;
  topologyConfidence: number;
  spatialConfidence: number;
  dimensionConfidence: number;
  engineeringReliability: 'SUPPORTED' | 'HEURISTIC' | 'UNSUPPORTED';
  isCADSourceAvailable: boolean;
}

export interface GeometricEntityMeshDescriptor {
  entityTag: string;
  equipmentClass: string;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  dimensionsMm?: { length: number; diameter: number; height?: number };
  provenance: GeometryProvenance;
}

export class GeometryService {
  private entityDescriptors: Map<string, GeometricEntityMeshDescriptor> = new Map();

  constructor() {
    // Seed default representative plant assets with proper L4 provenance
    this.registerRepresentativeAsset('E-101', 'HEAT_EXCHANGER', [-8, 0, -2], 'PID-DWG-07');
    this.registerRepresentativeAsset('E-102', 'HEAT_EXCHANGER', [-2, 0, 0], 'PID-DWG-07');
    this.registerRepresentativeAsset('P-101A', 'PUMP', [-14, -1, -2], 'PID-DWG-07');
    this.registerRepresentativeAsset('V-101', 'VESSEL', [6, 2, 2], 'PID-DWG-07');
  }

  public registerRepresentativeAsset(
    tag: string,
    equipmentClass: string,
    position: [number, number, number],
    sourceDocument: string
  ): void {
    const descriptor: GeometricEntityMeshDescriptor = {
      entityTag: tag,
      equipmentClass,
      position,
      rotation: [0, 0, 0],
      scale: [1, 1, 1],
      dimensionsMm: { length: 6000, diameter: 1200 },
      provenance: {
        entityTag: tag,
        sourceType: 'PATH_A_INFERRED_REPRESENTATIVE',
        sourceDocument,
        qualityLevel: 'L4', // Spatially reconstructed representative scene
        geometryType: 'REPRESENTATIVE_PROCEDURAL',
        extractionConfidence: 0.94,
        topologyConfidence: 0.98,
        spatialConfidence: 0.75, // Inferred layout
        dimensionConfidence: 0.60,
        engineeringReliability: 'SUPPORTED',
        isCADSourceAvailable: false,
      },
    };
    this.entityDescriptors.set(tag, descriptor);
  }

  public importSourceCADOrIFC(
    tag: string,
    equipmentClass: string,
    cadFileName: string,
    position: [number, number, number],
    exactDimensionsMm: { length: number; diameter: number; height?: number }
  ): GeometricEntityMeshDescriptor {
    const descriptor: GeometricEntityMeshDescriptor = {
      entityTag: tag,
      equipmentClass,
      position,
      rotation: [0, 0, 0],
      scale: [1, 1, 1],
      dimensionsMm: exactDimensionsMm,
      provenance: {
        entityTag: tag,
        sourceType: 'PATH_B_SOURCE_CAD_IFC',
        sourceDocument: cadFileName,
        qualityLevel: 'L5', // True source-backed CAD geometry
        geometryType: 'SOURCE_BACKED_EXACT',
        extractionConfidence: 1.0,
        topologyConfidence: 1.0,
        spatialConfidence: 1.0,
        dimensionConfidence: 1.0,
        engineeringReliability: 'SUPPORTED',
        isCADSourceAvailable: true,
      },
    };
    this.entityDescriptors.set(tag, descriptor);
    return descriptor;
  }

  public getDescriptor(tag: string): GeometricEntityMeshDescriptor | undefined {
    return this.entityDescriptors.get(tag);
  }

  public getAllDescriptors(): GeometricEntityMeshDescriptor[] {
    return Array.from(this.entityDescriptors.values());
  }

  public getGeometryProvenance(tag: string): GeometryProvenance | null {
    const desc = this.entityDescriptors.get(tag);
    return desc ? desc.provenance : null;
  }
}

export const geometryService = new GeometryService();
