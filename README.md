# CPU Scheduling Visualizer (University OS Lab)

This repository contains a single-file Streamlit application that simulates and visualizes five classic CPU scheduling algorithms for educational use in an Operating Systems lab.

Supported algorithms

- FCFS — First-Come, First-Served (non-preemptive)
- SJF — Shortest Job First (non-preemptive)
- SRTF — Shortest Remaining Time First (preemptive)
- Priority Scheduling — preemptive and non-preemptive modes (toggleable ordering)
- RR — Round Robin (preemptive, configurable time quantum)

What the app provides

- Interactive Gantt charts (Plotly) that show process execution blocks and explicit IDLE ranges.
- Per-process metrics table with AT, BT, Priority (if given), CT, TAT, and WT.
- Step-by-step human-readable execution trace explaining starts, preemptions, completions, and idle intervals.
- Explicit formula substitutions for TAT/WT calculations and average statistics (for teaching and grading transparency).

Quick start

1. Create a virtual environment (recommended) and install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Run the Streamlit app:

```powershell
streamlit run app.py
```

UI & input expectations

- The UI is sidebar-driven. Select an algorithm and enter inputs in the provided form.
- Inputs are comma-separated lists. Example:

   - Arrival times: `0,2,4`
   - Burst times: `5,3,1`
   - Priorities (optional): `2,1,3`
   - Time quantum (RR): `2`

- The app validates inputs (arrival >= 0, burst > 0) and preserves stable tie-breaking by PID index when values match.

Design & educational choices

- Time is simulated in integer units. Preemptive algorithms step at 1-unit resolution.
- Tie-breaking preserves original input order (P1, P2, ...).
- Priority mode supports both conventions (lower number = higher priority or the opposite) via a toggle.
- Idle ranges are shown explicitly in the Gantt trace and in the human trace for clarity.

Files of interest

- `app.py` — main Streamlit application (UI + simulators). This is a single-file, runnable app.
- `requirements.txt` — minimal dependencies (Streamlit, pandas, numpy, plotly).
- `.github/copilot-instructions.md` — guidance for AI coding agents working on this project.

Developer notes (simulator contract)

- Input: list of Process records {pid, arrival, burst, remaining, priority?}
- Output: `trace` (list of timeline segments for Gantt), `completion` times, `human` (ordered trace strings), and `arrivals` map.
- Edge cases handled: simultaneous arrivals, CPU idling before first arrival, stable tie-breaking, priority toggles, and invalid input validation.

Acknowledgements

This project was implemented with assistance from several AI tools to speed development and ensure clarity: GitHub Copilot, Anthropic Claude, and Google Gemini. The author reviewed and validated all outputs; any remaining errors are the author's responsibility.

License

See the `LICENSE` file in the repository.

If you'd like a shorter or longer README, or a separate `DEVELOPER.md` with implementation details and tests, tell me which format you prefer and I will add it.
Provide the complete, monolithic `app.py` script so I can directly run it and deploy it to my GitHub repository. Do not use placeholders or omit complex logic loops. Write robust, error-checked, math-accurate code.



