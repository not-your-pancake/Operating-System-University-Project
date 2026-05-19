## Purpose

This file gives concise, actionable guidance to AI coding agents working on the Operating-System-University-Project repository.

### Quick summary
- Repo type: single-page Streamlit application (monolithic script expected at `app.py`).
- Goal: simulate visual, step-by-step CPU scheduling algorithms (FCFS, SJF, SRTF, Priority preemptive/non-preemptive, RR) as described in `README.md`.

### Big-picture architecture (what to expect)
- Single entrypoint: `app.py` (Streamlit app). Treat it as the UI + orchestration layer that:
  1. normalizes user inputs (Arrival Times, Burst Times, optional Priorities, Quantum for RR),
  2. calls pure simulation functions that return a Gantt-style execution trace, per-process metrics, and a step-by-step execution log,
  3. renders Plotly/Altair Gantt charts, a Pandas-like metrics table, and the human-readable trace/security-explanations.
- Dataflow example: user CSV/comma lists -> List[Process] with fields {id, arrival, burst, remaining, priority} -> scheduler(simulator) -> {trace[], metrics_df, summary_stats} -> Streamlit render.

### Project-specific conventions and patterns
- Inputs are expected as comma-separated lists in the UI (see `README.md`). Example: Arrival: `0,2,4`; Burst: `5,3,1`; Priority (optional): `2,1,3`; Quantum: `2`.
- Time is integer-valued and simulations should step in discrete 1-unit increments for preemptive algorithms (SRTF, RR).
- Tie-breaking: when multiple processes are eligible (same arrival or same remaining time), preserve original input order (stable ordering by PID / index) unless a priority rule is explicitly selected.
- Priority mode must support a toggle for "lower number = higher priority" vs "higher number = higher priority" as required by `README.md`.
- Visual output: prefer Plotly for Gantt charts (explicitly mentioned in README) but Altair is acceptable if it produces clear timeline blocks and idle segments.

### Files of interest (reference points)
- `README.md` — contains the detailed feature/UX requirements (Gantt, trace logs, formula substitution, dark mode color palette).
- `app.py` — main Streamlit entrypoint (currently empty). Implement simulation functions here or import from a small helper module you add.

### Dependencies & run commands (discovered from README)
- Likely dependencies: `streamlit`, `pandas`, `numpy`, `plotly` (or `altair`). If you add a `requirements.txt`, pin these packages. Example install (PowerShell):

```powershell
python -m pip install --upgrade pip; \
  pip install streamlit pandas numpy plotly
```

- To run locally:

```powershell
streamlit run app.py
```

### Expected simulator contract (inputs / outputs)
- Inputs: List[Process] where Process is {id: str, arrival: int, burst: int, remaining: int, priority?: int}
- Outputs: {
  trace: List[ {time_start:int, time_end:int, pid:str, note?:string} ],
  metrics: Table with columns [PID, AT, BT, Priority?, CT, TAT, WT],
  summary: {avg_tat: float, avg_wt: float, formula_steps: str}
}

### Edge cases to handle (explicit, non-generic)
- Simultaneous arrivals at the same time unit — maintain stable input ordering for deterministic results.
- CPU idling before the first arrival or gaps between processes — include explicit idle segments in the Gantt trace.
- Zero or negative inputs: reject in UI with a clear message; arrival and burst must be non-negative integers and burst > 0.
- Priority absent: fall back to non-priority algorithms and hide priority controls.

### Rendering & educational requirements (must-haves)
- Show a human-readable, step-by-step execution log next to the chart (e.g., "t=3: P2 arrived, remaining 1 < P1 remaining 2 → preempt P1").
- For summary statistics, render substitution steps for the formulas, e.g., show 
  TAT(P1) = CT - AT = 7 - 0 = 7, then compute averages explicitly.
- Use a dark-themed Streamlit layout. `README.md` specifies color palette guidance; prefer navy/slate backgrounds and electric-blue accents for active Gantt bars.

### Where to be conservative / avoid assumptions
- Don't invent additional microservices, config files, or CI integrations — this repo is single-file focused. If you add files, keep them minimal and update README.
- Avoid changing the UX contract described in `README.md` (inputs as comma lists, per-process breakdown, and explicit trace). If you change behavior, document it in README.

### If `.github/copilot-instructions.md` already exists
- Merge strategy: keep any existing algorithm-specific tests or examples, but update the Quick summary and Files of interest sections above. Preserve any author notes at top.

---
If anything here is unclear or you want me to seed the repository with a starter `app.py` and `requirements.txt`, tell me which preference you want (complete monolithic `app.py` vs. split `simulators.py` + `app.py`) and I'll implement it.

Please review this draft and tell me if you'd like more examples (sample inputs/outputs) or a starter implementation scaffold.
