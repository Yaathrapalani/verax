# PLANT-X Voice System Testing & Verification Suite

## 1. Automated Test Suites

The test matrix is implemented across both frontend and backend environments:

### Frontend Unit & E2E Tests (Node 24 Native Test Runner)
Command:
```bash
npm test
```
Execution: `npx -y tsx --test tests/workstation_test.ts`
Current Count: **60 / 60 tests PASS**

Key areas covered:
1. **Tool Registry & Execution** (Tests 1–3, 18–21)
2. **Intent Parsing & Pronoun Resolution** (Tests 4–9)
3. **Timer Service & Countdown Cancellation** (Tests 10–11, 22)
4. **Epistemic Truth Firewall** (Tests 14, 26)
5. **Turn Management & Barge-In** (Tests 24–25, 39, 59–60)
6. **Voice Provider Registry & Fallback** (Tests 23, 46)
7. **Session Resumption & Stale Result Invalidation** (Tests 40, 47)
8. **3D Projection & Version Management** (Tests 33–34, 43–45, 50)
9. **Persistent Voice Controller Integration** (Test 51)
10. **Screen Awareness & Context Queries** (Tests 52–54)
11. **Attention & Triage** (Test 55)
12. **Multi-Turn Engineering Conversation Sequence** (Test 56)
13. **Operator Greeting & Hypotheses Selection** (Tests 57–58)

### Backend Pytest Regression Suite
Command:
```bash
./.venv/bin/pytest -q
```
Current Count: **523 / 523 tests PASS**

Covers:
- Stage 0–14 scientific baseline
- FOUL-X predictive intelligence
- Trust Gate and fixed policy fallback
- Thermodynamic property calculation engine
- Equipment simulation runtime
- Voice token brokering and authentication

## 2. Manual Acceptance Procedure (Flagship 12-Step Test)

1. **Activate Voice**: Click microphone or press `Cmd+K`. Say: *"Hello"*.
   - *Expected*: Assistant responds with readiness greeting indicating active asset E-102.
2. **Attention Triage**: Say: *"FOUL-X, show me the exchanger with the highest uncertainty."*
   - *Expected*: E-102 is selected across P&ID, 3D viewport, and Inspector.
3. **Contextual Explanation**: Say: *"Why?"*
   - *Expected*: Assistant reports reliability gate status and regime shift without hallucinating.
4. **Data Gaps**: Say: *"What's missing?"*
   - *Expected*: Assistant audits missing sensor channels (e.g., differential pressure $\Delta P$).
5. **Investigation Recommendations**: Say: *"What should I investigate next?"*
   - *Expected*: Assistant recommends next action (velocity decoupling test).
6. **Scheduled Action**: Say: *"Run the irregular-sampling scenario in ten seconds."*
   - *Expected*: Visual countdown timer appears on workstation control bar.
7. **Cancellation**: Immediately say: *"Cancel"*.
   - *Expected*: Pending scenario is aborted immediately.
8. **Navigation Awareness**: Click to navigate to Evidence view. Ask: *"What am I looking at?"*
   - *Expected*: Assistant describes the active Evidence view and selected asset E-102.
9. **Barge-In**: While assistant is speaking, say: *"Stop speaking"*.
   - *Expected*: Audio stops immediately while keeping workstation state intact.
10. **Comparative Analysis**: Say: *"Compare that with baseline"*.
    - *Expected*: Assistant reports baseline comparison on E-102 and navigates to Trends.
11. **Network Resilience**: Switch provider to Demo or disconnect.
    - *Expected*: Explicit provider indicator updates; session context remains preserved.
12. **Epistemic Limitation**: Ask: *"What is the dynamic viscosity of the crude feed?"*
    - *Expected*: Assistant states transport properties are UNAVAILABLE.
