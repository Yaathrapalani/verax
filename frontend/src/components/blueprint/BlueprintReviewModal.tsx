import React, { useState } from 'react';
import { BlueprintIngestionEngine } from '../../blueprint/blueprintIngestion';
import { GraphReconstructionEngine } from '../../blueprint/graphReconstruction';
import type { ReconstructedPlantGraph } from '../../blueprint/graphReconstruction';
import { SpatialSolver } from '../../blueprint/spatialSolver';
import { SceneCompiler } from '../../blueprint/sceneCompiler';

interface BlueprintReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSceneCompiled?: (sceneNotice: string) => void;
}

export const BlueprintReviewModal: React.FC<BlueprintReviewModalProps> = ({
  isOpen,
  onClose,
  onSceneCompiled,
}) => {
  const [doc] = useState(() => BlueprintIngestionEngine.ingestCanonicalPID());
  const [graph, setGraph] = useState<ReconstructedPlantGraph>(() =>
    GraphReconstructionEngine.reconstruct(doc)
  );
  const [compiledNotice, setCompiledNotice] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleConfirmAlternative = (connId: string, targetTag: string, note: string) => {
    const updated = GraphReconstructionEngine.confirmAmbiguousConnection(graph, connId, targetTag, note);
    setGraph(updated);
  };

  const handleBuild3D = () => {
    const spatialLayout = SpatialSolver.solve(graph);
    const scene = SceneCompiler.compile(spatialLayout);
    const notice = `Procedural 3D compiled from ${doc.filename}: ${scene.nodes.length} equipment units, ${scene.pipes.length} piping segments (${scene.qualityLevel}).`;
    setCompiledNotice(notice);
    onSceneCompiled?.(notice);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.85)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        width: '840px',
        maxHeight: '90vh',
        backgroundColor: '#0f172a',
        border: '1px solid #334155',
        borderRadius: '4px',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 20px 25px -5px rgba(0,0,0,0.5)',
        fontFamily: 'monospace',
      }}>
        {/* Header */}
        <div style={{
          padding: '12px 16px',
          borderBottom: '1px solid #1e293b',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#1e293b',
        }}>
          <div>
            <span style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>
              BLUEPRINT REVIEW & 3D RECONSTRUCTION
            </span>
            <span style={{ marginLeft: '12px', fontSize: '11px', color: '#94a3b8' }}>
              {doc.filename} ({doc.checksum})
            </span>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '16px',
            }}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '16px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Quality Level & Truth Badge */}
          <div style={{
            padding: '10px 12px',
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '4px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}>
            <div>
              <div style={{ fontSize: '11px', color: '#94a3b8' }}>SPATIAL MODEL QUALITY:</div>
              <div style={{ fontSize: '13px', color: '#38bdf8', fontWeight: 600 }}>{doc.qualityLevel}</div>
            </div>
            <div style={{
              fontSize: '10px',
              padding: '4px 8px',
              backgroundColor: '#0284c7',
              color: '#ffffff',
              borderRadius: '2px',
              fontWeight: 600,
            }}>
              REPRESENTATIVE / ILLUSTRATIVE (NOT MEASURED CAD)
            </div>
          </div>

          {/* Extracted Equipment Table */}
          <div>
            <div style={{ fontSize: '12px', color: '#cbd5e1', fontWeight: 600, marginBottom: '6px' }}>
              EXTRACTED EQUIPMENT NODES ({doc.extractedEntities.length})
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px', textAlign: 'left' }}>
              <thead>
                <tr style={{ backgroundColor: '#1e293b', color: '#94a3b8' }}>
                  <th style={{ padding: '6px 8px', border: '1px solid #334155' }}>TAG</th>
                  <th style={{ padding: '6px 8px', border: '1px solid #334155' }}>TYPE</th>
                  <th style={{ padding: '6px 8px', border: '1px solid #334155' }}>BOUNDING BOX</th>
                  <th style={{ padding: '6px 8px', border: '1px solid #334155' }}>CONFIDENCE</th>
                  <th style={{ padding: '6px 8px', border: '1px solid #334155' }}>TRUTH STATE</th>
                </tr>
              </thead>
              <tbody>
                {doc.extractedEntities.map(e => (
                  <tr key={e.id} style={{ borderBottom: '1px solid #1e293b', color: '#e2e8f0' }}>
                    <td style={{ padding: '6px 8px', border: '1px solid #334155', fontWeight: 600, color: '#38bdf8' }}>{e.tag}</td>
                    <td style={{ padding: '6px 8px', border: '1px solid #334155' }}>{e.type}</td>
                    <td style={{ padding: '6px 8px', border: '1px solid #334155', color: '#94a3b8' }}>
                      [{e.boundingBox.x}, {e.boundingBox.y}, {e.boundingBox.width}, {e.boundingBox.height}]
                    </td>
                    <td style={{ padding: '6px 8px', border: '1px solid #334155' }}>{(e.confidence * 100).toFixed(0)}%</td>
                    <td style={{ padding: '6px 8px', border: '1px solid #334155', color: '#4ade80' }}>{e.truthState}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Connection Reconstruction & Human Ambiguity Review */}
          <div>
            <div style={{ fontSize: '12px', color: '#cbd5e1', fontWeight: 600, marginBottom: '6px' }}>
              PROCESS CONNECTIONS & AMBIGUITY RESOLUTION ({graph.edges.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {graph.edges.map(edge => (
                <div
                  key={edge.id}
                  style={{
                    padding: '8px 12px',
                    backgroundColor: edge.isAmbiguous ? '#451a03' : '#1e293b',
                    border: `1px solid ${edge.isAmbiguous ? '#b45309' : '#334155'}`,
                    borderRadius: '4px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '11px',
                  }}
                >
                  <div>
                    <span style={{ color: '#38bdf8', fontWeight: 600 }}>{edge.from}</span>
                    <span style={{ color: '#94a3b8', margin: '0 8px' }}>──[{edge.streamTag}]──▶</span>
                    <span style={{ color: '#38bdf8', fontWeight: 600 }}>{edge.to}</span>
                    <span style={{
                      marginLeft: '12px',
                      padding: '2px 6px',
                      borderRadius: '2px',
                      fontSize: '10px',
                      backgroundColor: edge.status === 'HUMAN_AUDITED' ? '#065f46' : (edge.isAmbiguous ? '#78350f' : '#0f766e'),
                      color: '#ffffff',
                    }}>
                      {edge.status}
                    </span>
                  </div>

                  {edge.isAmbiguous && (
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        onClick={() => handleConfirmAlternative(edge.id, 'E-103', 'Engineer confirmed upper line to E-103')}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#2563eb',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '2px',
                          fontSize: '10px',
                          cursor: 'pointer',
                        }}
                      >
                        Confirm Upper (E-103)
                      </button>
                      <button
                        onClick={() => handleConfirmAlternative(edge.id, 'E-104', 'Engineer confirmed lower bypass to E-104')}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#475569',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '2px',
                          fontSize: '10px',
                          cursor: 'pointer',
                        }}
                      >
                        Confirm Bypass (E-104)
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Audit Trail */}
          <div style={{ padding: '10px 12px', backgroundColor: '#0b1120', border: '1px solid #1e293b', borderRadius: '4px' }}>
            <div style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600, marginBottom: '4px' }}>
              EXTRACTION & HUMAN VALIDATION AUDIT TRAIL
            </div>
            {graph.auditTrail.map((item, idx) => (
              <div key={idx} style={{ fontSize: '10px', color: '#64748b' }}>
                • {item}
              </div>
            ))}
          </div>

          {compiledNotice && (
            <div style={{ padding: '10px', backgroundColor: '#064e3b', color: '#34d399', fontSize: '11px', borderRadius: '4px' }}>
              ✓ {compiledNotice}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '12px 16px',
          borderTop: '1px solid #1e293b',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#1e293b',
        }}>
          <div style={{ fontSize: '11px', color: '#94a3b8' }}>
            Unresolved Ambiguities: <strong style={{ color: graph.unresolvedAmbiguitiesCount > 0 ? '#fbbf24' : '#34d399' }}>{graph.unresolvedAmbiguitiesCount}</strong>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={onClose}
              style={{
                padding: '6px 12px',
                backgroundColor: '#334155',
                color: '#e2e8f0',
                border: 'none',
                borderRadius: '2px',
                fontSize: '11px',
                cursor: 'pointer',
              }}
            >
              Close
            </button>
            <button
              onClick={handleBuild3D}
              style={{
                padding: '6px 14px',
                backgroundColor: '#0284c7',
                color: '#ffffff',
                border: 'none',
                borderRadius: '2px',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Compile Procedural 3D
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
