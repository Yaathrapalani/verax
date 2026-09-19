# Fallback Policy Specification

## Protocol
When Reliability Gate evaluates status = `ABSTAIN`, AI-assisted maintenance recommendations are withheld, and system falls back strictly to the configured `FIXED_TIME_BASED_MAINTENANCE_POLICY`.
No silent fallback or autonomous process control is permitted.
