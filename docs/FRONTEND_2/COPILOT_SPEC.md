# Engineering Copilot Specification

The `EngineeringCopilot` is a contextual tool layer rather than a dominant chatbot panel.

## Modes & Interaction
- **Default State**: Compact bottom/top command bar (`Ctrl+K` command palette).
- **Expanded State**: Collapsible right side panel.
- **Commands**:
  - `/inspect <tag>` — Selects object and opens inspector.
  - `/simulate <parameter>` — Sets counterfactual scenario slider.
  - `/trace <node>` — Launches evidence trace.
  - `/trust-gate` — Displays reliability gate status.
- **Boundary**: Voice and NLP inputs map strictly to command palette tool calls. Copilot cannot mutate engineering physics or compute unvalidated metrics.
