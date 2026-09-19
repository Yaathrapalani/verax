/**
 * PLANT-X Spatial Arrangement Solver.
 * 
 * Strictly separates engineering topology (what connects to what)
 * from spatial arrangement (where physical equipment and piping are reasonably placed).
 * Computes 3D coordinates using flow direction, equipment clearance, and port alignment.
 */

import type { ReconstructedPlantGraph } from './graphReconstruction';

export interface SpatialEquipmentPlacement {
  tag: string;
  type: string;
  position: [number, number, number];
  rotation: [number, number, number];
  clearanceBox: [number, number, number];
  ports: Array<{ id: string; offset: [number, number, number]; direction: [number, number, number] }>;
}

export interface SpatialPipeSegment {
  streamTag: string;
  points: Array<[number, number, number]>;
}

export interface SolvedSpatialLayout {
  documentId: string;
  equipmentPlacements: SpatialEquipmentPlacement[];
  pipeSegments: SpatialPipeSegment[];
  qualityLevel: string;
  isRepresentative: boolean;
}

export class SpatialSolver {
  private static readonly UNIT_SPACING_X = 6.0;

  public static solve(graph: ReconstructedPlantGraph): SolvedSpatialLayout {
    const equipmentPlacements: SpatialEquipmentPlacement[] = [];
    const pipeSegments: SpatialPipeSegment[] = [];

    // Topological placement along process flow axis (X-axis)
    graph.nodes.forEach((node, index) => {
      const posX = (index - (graph.nodes.length - 1) / 2) * this.UNIT_SPACING_X;
      const posY = node.type === 'PUMP' ? 0.0 : (node.type === 'VESSEL' ? 1.5 : 1.0);
      const posZ = 0.0;

      let clearance: [number, number, number] = [3, 2, 2];
      if (node.type === 'VESSEL') clearance = [3, 5, 3];
      if (node.type === 'PUMP') clearance = [2, 1.5, 2];

      equipmentPlacements.push({
        tag: node.tag,
        type: node.type,
        position: [posX, posY, posZ],
        rotation: [0, 0, 0],
        clearanceBox: clearance,
        ports: [
          { id: 'inlet', offset: [-1.2, 0, 0], direction: [-1, 0, 0] },
          { id: 'outlet', offset: [1.2, 0, 0], direction: [1, 0, 0] },
        ],
      });
    });

    // Pipe route computation between equipment ports
    graph.edges.forEach(edge => {
      const fromEq = equipmentPlacements.find(e => e.tag === edge.from);
      const toEq = equipmentPlacements.find(e => e.tag === edge.to);

      if (fromEq && toEq) {
        const pStart: [number, number, number] = [
          fromEq.position[0] + 1.2,
          fromEq.position[1],
          fromEq.position[2],
        ];
        const pEnd: [number, number, number] = [
          toEq.position[0] - 1.2,
          toEq.position[1],
          toEq.position[2],
        ];

        // Orthogonal pipe run
        const midX = (pStart[0] + pEnd[0]) / 2;
        pipeSegments.push({
          streamTag: edge.streamTag,
          points: [
            pStart,
            [midX, pStart[1], pStart[2]],
            [midX, pEnd[1], pEnd[2]],
            pEnd,
          ],
        });
      }
    });

    return {
      documentId: graph.documentId,
      equipmentPlacements,
      pipeSegments,
      qualityLevel: 'L2_PARAMETRIC_REPRESENTATIVE_3D',
      isRepresentative: true,
    };
  }
}
