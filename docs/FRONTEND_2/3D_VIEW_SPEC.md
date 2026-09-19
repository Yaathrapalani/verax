# 3D View Specification

The 3D View provides an interactive WebGL spatial representation using Three.js and React Three Fiber.

## Architectural Guidelines
- **Scene Design**: Clean engineering grid background with orthographic/perspective camera toggle.
- **Controls**: Fit Plant, Reset Camera, Orbit, Pan, Zoom, Focus Asset.
- **Visuals**: Realistic metallic materials; no neon glow or cyberpunk effects.
- **Labels**: Spatial 3D tags (`HTML Drei`) displaying canonical asset tags (e.g. `E-102`).
- **Representative Geometry Badge**: Clearly displays `REPRESENTATIVE GEOMETRY` when physical dimensions are not fully validated by backend.
