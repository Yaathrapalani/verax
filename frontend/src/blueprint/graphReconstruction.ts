/**
 * PLANT-X Graph Reconstruction & Human-in-the-Loop Review.
 * 
 * Reconstructs canonical process graph topology from extracted P&ID entities,
 * detects ambiguous connections, and audits human engineer validations/corrections.
 */

import type { BlueprintDocument } from './blueprintTypes';

export interface ReconstructedGraphNode {
  id: string;
  tag: string;
  type: string;
  sourceDoc: string;
  confidence: number;
}

export interface ReconstructedGraphEdge {
  id: string;
  from: string;
  to: string;
  streamTag: string;
  isAmbiguous: boolean;
  status: 'CONFIRMED' | 'UNRESOLVED' | 'HUMAN_AUDITED';
}

export interface ReconstructedPlantGraph {
  documentId: string;
  nodes: ReconstructedGraphNode[];
  edges: ReconstructedGraphEdge[];
  unresolvedAmbiguitiesCount: number;
  auditTrail: string[];
}

export class GraphReconstructionEngine {
  public static reconstruct(doc: BlueprintDocument): ReconstructedPlantGraph {
    const nodes: ReconstructedGraphNode[] = doc.extractedEntities.map(e => ({
      id: e.id,
      tag: e.tag,
      type: e.type,
      sourceDoc: e.sourceDoc,
      confidence: e.confidence,
    }));

    const edges: ReconstructedGraphEdge[] = doc.extractedConnections.map(c => ({
      id: c.id,
      from: c.fromTag,
      to: c.toTag,
      streamTag: c.lineTag,
      isAmbiguous: c.ambiguityState === 'AMBIGUOUS',
      status: c.ambiguityState === 'CONFIRMED' ? 'CONFIRMED' : 'UNRESOLVED',
    }));

    const unresolved = edges.filter(e => e.isAmbiguous && e.status === 'UNRESOLVED').length;

    return {
      documentId: doc.id,
      nodes,
      edges,
      unresolvedAmbiguitiesCount: unresolved,
      auditTrail: [`Initial extraction: ${nodes.length} equipment nodes, ${edges.length} connections from ${doc.filename}.`],
    };
  }

  /**
   * Applies human engineer correction to resolve ambiguous connection.
   */
  public static confirmAmbiguousConnection(
    graph: ReconstructedPlantGraph,
    connectionId: string,
    targetTag: string,
    engineerNote: string = 'Engineer confirmed via P&ID review'
  ): ReconstructedPlantGraph {
    const updatedEdges = graph.edges.map(edge => {
      if (edge.id === connectionId) {
        return {
          ...edge,
          to: targetTag,
          isAmbiguous: false,
          status: 'HUMAN_AUDITED' as const,
        };
      }
      return edge;
    });

    const unresolved = updatedEdges.filter(e => e.isAmbiguous && e.status === 'UNRESOLVED').length;

    return {
      ...graph,
      edges: updatedEdges,
      unresolvedAmbiguitiesCount: unresolved,
      auditTrail: [
        ...graph.auditTrail,
        `AUDITED CORRECTION: Connection ${connectionId} confirmed to ${targetTag} (${engineerNote}).`,
      ],
    };
  }
}
