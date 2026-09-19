/**
 * PLANT-X Blueprint-to-3D Subsystem Types.
 * 
 * Formal data structures for P&ID document intake, entity recognition,
 * graph reconstruction, spatial arrangement, and procedural 3D compilation.
 */

import type { TruthState } from '../agent/types';

export type BlueprintFormat = 'PDF' | 'SVG' | 'PNG' | 'JPG' | 'JSON' | 'DXF';

export type SpatialQualityLevel =
  | 'L0_GRAPH_ONLY'
  | 'L1_TOPOLOGICAL_3D'
  | 'L2_PARAMETRIC_REPRESENTATIVE_3D'
  | 'L3_DIMENSIONALLY_INFORMED_3D'
  | 'L4_SOURCE_CAD_ALIGNED_3D'
  | 'L5_VALIDATED_ENGINEERING_MODEL';

export type ExtractionAmbiguityState = 'CONFIRMED' | 'LIKELY' | 'AMBIGUOUS' | 'UNRESOLVED';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ExtractedEntity {
  id: string;
  tag: string;
  type: 'HEAT_EXCHANGER' | 'PUMP' | 'VALVE' | 'VESSEL' | 'COLUMN' | 'INSTRUMENT';
  boundingBox: BoundingBox;
  sourceText: string;
  extractionMethod: 'OCR_AND_SYMBOL_RECOGNITION' | 'VECTOR_PRIMITIVE_PARSING' | 'HUMAN_AUDITED_CORRECTION';
  confidence: number;
  truthState: TruthState;
  sourceDoc: string;
  page: number;
  parameters?: Record<string, unknown>;
}

export interface ExtractedConnection {
  id: string;
  fromTag: string;
  toTag: string;
  lineTag: string;
  direction: 'FORWARD' | 'BIDIRECTIONAL' | 'UNKNOWN';
  ambiguityState: ExtractionAmbiguityState;
  candidateAlternatives?: Array<{ fromTag: string; toTag: string; note: string }>;
  confidence: number;
  truthState: TruthState;
}

export interface BlueprintDocument {
  id: string;
  filename: string;
  format: BlueprintFormat;
  pageCount: number;
  checksum: string;
  extractedEntities: ExtractedEntity[];
  extractedConnections: ExtractedConnection[];
  qualityLevel: SpatialQualityLevel;
}
