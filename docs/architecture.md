# FOUL-X Architecture

```text
                 HISTORIAN / REPLAY
                        │
                        ▼
               ┌─────────────────┐
               │ Data Validation │
               └────────┬────────┘
                        ▼
               ┌─────────────────┐
               │ Physics / State │
               └────────┬────────┘
                        ▼
               ┌─────────────────┐
               │ Feature Layer   │
               └────────┬────────┘
                        ▼
               ┌─────────────────┐
               │ Forecast Model  │
               └────────┬────────┘
                        ▼
               ┌─────────────────┐
               │ Reliability Gate│
               └──────┬───┬──────┘
                      │   │
                 PASS │   │ FAIL
                      ▼   ▼
              Decision   Abstain
                 │        │
                 ▼        ▼
              CLEAN/WAIT Fixed Policy
                 │        │
                 └────┬───┘
                      ▼
                 Audit Record
                      │
                      ▼
                 API / Dashboard
```

The core separation is intentional: prediction is not permission to act.
