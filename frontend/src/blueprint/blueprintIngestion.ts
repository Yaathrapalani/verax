/**
 * PLANT-X Blueprint Ingestion & Parsing Engine.
 * 
 * Ingests engineering documents (P&ID schematics, PDFs, JSON manifests)
 * and extracts equipment tags, connections, and annotations while preserving provenance.
 */

import type { BlueprintDocument, ExtractedEntity, ExtractedConnection } from './blueprintTypes';

export class BlueprintIngestionEngine {
  /**
   * Ingests canonical crude preheat train P&ID blueprint fixture.
   */
  public static ingestCanonicalPID(): BlueprintDocument {
    const extractedEntities: ExtractedEntity[] = [
      {
        id: 'ent_p101',
        tag: 'P-101',
        type: 'PUMP',
        boundingBox: { x: 0.12, y: 0.45, width: 0.08, height: 0.1 },
        sourceText: 'P-101 A/B CRUDE CHARGE PUMP',
        extractionMethod: 'OCR_AND_SYMBOL_RECOGNITION',
        confidence: 0.98,
        truthState: 'OBSERVED',
        sourceDoc: 'PID-001-CRUDE-PREHEAT.pdf',
        page: 1,
      },
      {
        id: 'ent_e101',
        tag: 'E-101',
        type: 'HEAT_EXCHANGER',
        boundingBox: { x: 0.28, y: 0.42, width: 0.12, height: 0.14 },
        sourceText: 'E-101 CRUDE/RESIDUE EXCHANGER',
        extractionMethod: 'OCR_AND_SYMBOL_RECOGNITION',
        confidence: 0.96,
        truthState: 'OBSERVED',
        sourceDoc: 'PID-001-CRUDE-PREHEAT.pdf',
        page: 1,
      },
      {
        id: 'ent_e102',
        tag: 'E-102',
        type: 'HEAT_EXCHANGER',
        boundingBox: { x: 0.46, y: 0.42, width: 0.12, height: 0.14 },
        sourceText: 'E-102 CRUDE/HVGO EXCHANGER',
        extractionMethod: 'OCR_AND_SYMBOL_RECOGNITION',
        confidence: 0.95,
        truthState: 'OBSERVED',
        sourceDoc: 'PID-001-CRUDE-PREHEAT.pdf',
        page: 1,
      },
      {
        id: 'ent_v101',
        tag: 'V-101',
        type: 'VESSEL',
        boundingBox: { x: 0.65, y: 0.38, width: 0.14, height: 0.24 },
        sourceText: 'V-101 DESALTER VESSEL',
        extractionMethod: 'OCR_AND_SYMBOL_RECOGNITION',
        confidence: 0.97,
        truthState: 'OBSERVED',
        sourceDoc: 'PID-001-CRUDE-PREHEAT.pdf',
        page: 1,
      },
      {
        id: 'ent_e103',
        tag: 'E-103',
        type: 'HEAT_EXCHANGER',
        boundingBox: { x: 0.82, y: 0.42, width: 0.12, height: 0.14 },
        sourceText: 'E-103 CRUDE/PA EXCHANGER',
        extractionMethod: 'OCR_AND_SYMBOL_RECOGNITION',
        confidence: 0.94,
        truthState: 'OBSERVED',
        sourceDoc: 'PID-001-CRUDE-PREHEAT.pdf',
        page: 1,
      },
    ];

    const extractedConnections: ExtractedConnection[] = [
      {
        id: 'conn_1',
        fromTag: 'P-101',
        toTag: 'E-101',
        lineTag: 'S-101',
        direction: 'FORWARD',
        ambiguityState: 'CONFIRMED',
        confidence: 0.96,
        truthState: 'OBSERVED',
      },
      {
        id: 'conn_2',
        fromTag: 'E-101',
        toTag: 'E-102',
        lineTag: 'S-102',
        direction: 'FORWARD',
        ambiguityState: 'CONFIRMED',
        confidence: 0.95,
        truthState: 'OBSERVED',
      },
      {
        id: 'conn_3',
        fromTag: 'E-102',
        toTag: 'V-101',
        lineTag: 'S-103',
        direction: 'FORWARD',
        ambiguityState: 'CONFIRMED',
        confidence: 0.97,
        truthState: 'OBSERVED',
      },
      {
        id: 'conn_4',
        fromTag: 'V-101',
        toTag: 'E-103',
        lineTag: 'S-104',
        direction: 'FORWARD',
        ambiguityState: 'AMBIGUOUS', // Deliberate ambiguity for human review mode
        candidateAlternatives: [
          { fromTag: 'V-101', toTag: 'E-103', note: 'Upper nozzle desalted crude line (Standard PFD flow)' },
          { fromTag: 'V-101', toTag: 'E-104', note: 'Lower bypass connection (Auxiliary drain line)' },
        ],
        confidence: 0.72,
        truthState: 'INFERRED',
      },
    ];

    return {
      id: 'doc_pid_001',
      filename: 'PID-001-CRUDE-PREHEAT.pdf',
      format: 'PDF',
      pageCount: 1,
      checksum: 'sha256_b39f72c693a104e76d912e9b9c02',
      extractedEntities,
      extractedConnections,
      qualityLevel: 'L2_PARAMETRIC_REPRESENTATIVE_3D',
    };
  }
}
