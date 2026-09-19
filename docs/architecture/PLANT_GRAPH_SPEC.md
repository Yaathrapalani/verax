# Plant Graph Specification

**Version:** 1.0.0  
**Status:** Approved Stage 0 Baseline  

---

## Topological Graph Representation

PLANT-X models facilities as strongly typed, directed plant graphs.

### Core Graph Nodes
- **`Plant`**
- **`Asset`**
- **`Stream`**
- **`Measurement`**
- **`Event`**

### Typed Relationships
- **`CONNECTED_TO`**: Physical equipment coupling.
- **`FEEDS`**: Upstream stream feeding downstream asset.
- **`RECEIVES`**: Downstream asset receiving fluid stream.
- **`MEASURES`**: Sensor tag measuring stream or asset variable.
- **`HAS_EVENT`**: Incident or maintenance record associated with asset.
- **`DEPENDS_ON`**: Functional dependency.
