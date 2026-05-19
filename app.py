"""
Streamlit application for visualizing CPU scheduling algorithms.

Implements:
 - FCFS
 - SJF (non-preemptive)
 - SRTF (preemptive)
 - Priority (preemptive and non-preemptive)
 - RR (Round Robin)

The app focuses on educational clarity: Gantt charts (Plotly),
per-process metrics table, step-by-step execution trace, and
formula substitutions for average TAT and WT.

Run with:
  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


### Data models
@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    remaining: int = field(init=False)
    priority: Optional[int] = None

    def __post_init__(self):
        self.remaining = self.burst


### Simulation helpers & contracts
def parse_csv_list(txt: str) -> List[int]:
    """Parse comma/space separated integers, robust to empty strings."""
    if not txt:
        return []
    parts = [p.strip() for p in txt.replace(';', ',').split(',') if p.strip()]
    vals: List[int] = []
    for p in parts:
        try:
            vals.append(int(p))
        except Exception:
            raise ValueError(f"Invalid integer value: '{p}'")
    return vals


def to_processes(arrivals: List[int], bursts: List[int], priorities: Optional[List[int]] = None) -> List[Process]:
    if len(arrivals) != len(bursts):
        raise ValueError("Arrival and Burst lists must be the same length")
    if priorities is not None and len(priorities) != len(arrivals):
        raise ValueError("Priority list length must match arrivals/bursts")
    procs: List[Process] = []
    for i, (a, b) in enumerate(zip(arrivals, bursts), start=1):
        if a < 0 or b <= 0:
            raise ValueError("Arrival times must be >= 0 and Burst times must be > 0")
        p = Process(pid=f"P{i}", arrival=a, burst=b, priority=(priorities[i-1] if priorities else None))
        procs.append(p)
    return procs


def build_metrics_df(procs: List[Process], completion: Dict[str, int], arrivals: Dict[str, int]) -> pd.DataFrame:
    rows = []
    for p in procs:
        ct = completion[p.pid]
        tat = ct - arrivals[p.pid]
        wt = tat - p.burst
        rows.append({"PID": p.pid, "AT": arrivals[p.pid], "BT": p.burst, "Priority": p.priority, "CT": ct, "TAT": tat, "WT": wt})
    df = pd.DataFrame(rows)
    return df


def avg_and_formula(df: pd.DataFrame) -> Tuple[float, float, str]:
    vals_tat = df["TAT"].tolist()
    vals_wt = df["WT"].tolist()
    avg_tat = float(np.mean(vals_tat)) if vals_tat else 0.0
    avg_wt = float(np.mean(vals_wt)) if vals_wt else 0.0
    formula_lines = []
    for idx, row in df.iterrows():
        formula_lines.append(f"TAT({row['PID']}) = CT - AT = {row['CT']} - {row['AT']} = {row['TAT']}")
        formula_lines.append(f"WT({row['PID']}) = TAT - BT = {row['TAT']} - {row['BT']} = {row['WT']}")
    formula_lines.append(f"Average TAT = ({' + '.join(map(str, vals_tat))}) / {len(vals_tat)} = {avg_tat:.2f}")
    formula_lines.append(f"Average WT = ({' + '.join(map(str, vals_wt))}) / {len(vals_wt)} = {avg_wt:.2f}")
    return avg_tat, avg_wt, "\n".join(formula_lines)


### Scheduler implementations
def simulate_fcfs(procs: List[Process]) -> Dict[str, Any]:
    """Non-preemptive FCFS simulation. Returns trace list, completion times, and human trace."""
    procs_sorted = sorted(procs, key=lambda p: (p.arrival, int(p.pid[1:])))
    time = 0
    trace = []
    completion = {}
    human_steps = []
    arrivals_map = {p.pid: p.arrival for p in procs_sorted}
    for p in procs_sorted:
        if time < p.arrival:
            # CPU idle until p arrives
            trace.append({"start": time, "end": p.arrival, "pid": "IDLE"})
            human_steps.append(f"t={time}..{p.arrival}: CPU idle until {p.pid} arrives")
            time = p.arrival
        start = time
        end = time + p.burst
        trace.append({"start": start, "end": end, "pid": p.pid})
        human_steps.append(f"t={start}: {p.pid} starts (burst={p.burst}) and runs till t={end}")
        time = end
        completion[p.pid] = time
    return {"trace": trace, "completion": completion, "human": human_steps, "arrivals": arrivals_map}


def simulate_sjf(procs: List[Process]) -> Dict[str, Any]:
    # Non-preemptive SJF
    time = 0
    pending = procs.copy()
    trace = []
    completion = {}
    human = []
    arrivals_map = {p.pid: p.arrival for p in pending}
    finished = set()
    n = len(pending)
    while len(finished) < n:
        # gather arrived and unfinished
        ready = [p for p in pending if p.arrival <= time and p.pid not in finished]
        if not ready:
            # idle until next arrival
            nxt = min([p.arrival for p in pending if p.pid not in finished])
            trace.append({"start": time, "end": nxt, "pid": "IDLE"})
            human.append(f"t={time}..{nxt}: CPU idle (no arrived jobs)")
            time = nxt
            continue
        # pick shortest burst; tie-breaker: original PID order
        ready_sorted = sorted(ready, key=lambda p: (p.burst, int(p.pid[1:])))
        p = ready_sorted[0]
        start = time
        end = time + p.burst
        trace.append({"start": start, "end": end, "pid": p.pid})
        human.append(f"t={start}: {p.pid} selected (BT={p.burst}) -> runs till t={end}")
        time = end
        completion[p.pid] = time
        finished.add(p.pid)
    return {"trace": trace, "completion": completion, "human": human, "arrivals": arrivals_map}


def simulate_srtf(procs: List[Process]) -> Dict[str, Any]:
    # Preemptive shortest remaining time
    time = 0
    pending = [Process(p.pid, p.arrival, p.burst, p.priority) for p in procs]
    trace = []
    completion = {}
    human = []
    arrivals_map = {p.pid: p.arrival for p in pending}
    last_pid = None
    skip_next_log: Optional[str] = None
    n = len(pending)
    finished = set()
    # run until all finished
    while len(finished) < n:
        # find ready processes
        ready = [p for p in pending if p.arrival <= time and p.pid not in finished]
        if not ready:
            # idle until next arrival (inclusive end in human message)
            nxt_arr = min([p.arrival for p in pending if p.pid not in finished])
            trace.append({"start": time, "end": nxt_arr, "pid": "IDLE"})
            human.append(f"t={time}..{nxt_arr}: CPU is Idle. Waiting for processes to arrive.")
            time = nxt_arr
            last_pid = None
            continue

        # pick shortest remaining; tie-breaker: PID index
        ready_sorted = sorted(ready, key=lambda p: (p.remaining, int(p.pid[1:])))
        cur = ready_sorted[0]

        # detect arrivals at this exact time (for explanatory preemption messages)
        arrivals_now = [p for p in pending if p.arrival == time and p.pid not in finished]

        # Emit a concise message only when a context switch/start occurs
        if last_pid != cur.pid:
            # If previous completion set a skip flag for this pid, skip duplicate log
            if skip_next_log == cur.pid:
                skip_next_log = None
            else:
                if last_pid is None:
                    # CPU was idle or this is the initial start/resume
                    human.append(f"t={time}: {cur.pid} starts execution (remaining={cur.remaining})")
                else:
                    # context switch: determine if caused by an arriving process preempting
                    preempting = None
                    last_proc = next((p for p in pending if p.pid == last_pid), None)
                    if arrivals_now:
                        # if the selected process arrived now and has shorter remaining than last
                        for a in arrivals_now:
                            if a.pid == cur.pid and last_proc is not None and cur.remaining < last_proc.remaining:
                                preempting = a
                                break
                    if preempting is not None and last_proc is not None:
                        human.append(f"t={time}: {preempting.pid} arrives with shorter remaining time ({preempting.remaining} < {last_proc.remaining}). {preempting.pid} preempts {last_pid} and starts running.")
                    else:
                        # general context switch explanation (use current remaining)
                        human.append(f"t={time}: {cur.pid} selected (remaining={cur.remaining}) — context switch from {last_pid}.")

        # update trace segments (group continuous execution)
        if last_pid != cur.pid:
            trace.append({"start": time, "end": time + 1, "pid": cur.pid})
        else:
            trace[-1]["end"] += 1

        # execute one time unit
        cur.remaining -= 1
        time += 1

        # check completion and log it with the absolute completion time
        if cur.remaining == 0:
            completion[cur.pid] = time
            finished.add(cur.pid)
            # decide if a next process is immediately selected
            next_ready = [p for p in pending if p.arrival <= time and p.pid not in finished]
            if next_ready:
                nxt = sorted(next_ready, key=lambda p: (p.remaining, int(p.pid[1:])))[0]
                human.append(f"t={time}: {cur.pid} finishes completely. {nxt.pid} is selected next (remaining={nxt.remaining}).")
                # suppress the next automatic context-switch message for the selected pid
                skip_next_log = nxt.pid
            else:
                human.append(f"t={time}: {cur.pid} finishes completely.")
        last_pid = cur.pid
    return {"trace": trace, "completion": completion, "human": human, "arrivals": arrivals_map}


def simulate_priority(procs: List[Process], preemptive: bool = False, lower_is_higher: bool = True) -> Dict[str, Any]:
    # Priority scheduling with optional preemption
    time = 0
    pending = [Process(p.pid, p.arrival, p.burst, p.priority) for p in procs]
    trace = []
    completion = {}
    human = []
    arrivals_map = {p.pid: p.arrival for p in pending}
    finished = set()
    last_pid = None
    skip_next_log: Optional[str] = None
    n = len(pending)
    while len(finished) < n:
        ready = [p for p in pending if p.arrival <= time and p.pid not in finished]
        if not ready:
            nxt = min([p.arrival for p in pending if p.pid not in finished])
            trace.append({"start": time, "end": nxt, "pid": "IDLE"})
            human.append(f"t={time}..{nxt - 1}: CPU idle (no arrived jobs)")
            time = nxt
            last_pid = None
            continue
        # sort by priority, then PID index
        if lower_is_higher:
            ready_sorted = sorted(ready, key=lambda p: (p.priority if p.priority is not None else float('inf'), int(p.pid[1:])))
        else:
            ready_sorted = sorted(ready, key=lambda p: (-(p.priority if p.priority is not None else -float('inf')), int(p.pid[1:])))
        cur = ready_sorted[0]
        if preemptive:
            # compress logs: only emit on start/context-switch/completion using remaining values
            arrivals_now = [p for p in pending if p.arrival == time and p.pid not in finished]
            if last_pid != cur.pid:
                if skip_next_log == cur.pid:
                    skip_next_log = None
                else:
                    if last_pid is None:
                        human.append(f"t={time}: {cur.pid} starts execution (remaining={cur.remaining})")
                    else:
                        # check if arrival caused preemption
                        preempting = None
                        last_proc = next((p for p in pending if p.pid == last_pid), None)
                        if arrivals_now:
                            for a in arrivals_now:
                                if a.pid == cur.pid and last_proc is not None and cur.remaining < last_proc.remaining:
                                    preempting = a
                                    break
                        if preempting is not None and last_proc is not None:
                            human.append(f"t={time}: {preempting.pid} arrives with shorter remaining time ({preempting.remaining} < {last_proc.remaining}). {preempting.pid} preempts {last_pid} and starts running.")
                        else:
                            human.append(f"t={time}: {cur.pid} selected (remaining={cur.remaining}) — context switch from {last_pid}.")
            # update trace segments
            if last_pid != cur.pid:
                trace.append({"start": time, "end": time + 1, "pid": cur.pid})
            else:
                trace[-1]["end"] += 1
            # execute one time unit
            cur.remaining -= 1
            time += 1
            if cur.remaining == 0:
                completion[cur.pid] = time
                finished.add(cur.pid)
                next_ready = [p for p in pending if p.arrival <= time and p.pid not in finished]
                if next_ready:
                    nxt = sorted(next_ready, key=lambda p: (p.remaining, int(p.pid[1:])))[0]
                    human.append(f"t={time}: {cur.pid} finishes completely. {nxt.pid} is selected next (remaining={nxt.remaining}).")
                    skip_next_log = nxt.pid
                else:
                    human.append(f"t={time}: {cur.pid} finishes completely.")
            last_pid = cur.pid
        else:
            # non-preemptive: run to completion
            start = time
            end = time + cur.burst
            trace.append({"start": start, "end": end, "pid": cur.pid})
            human.append(f"t={start}: {cur.pid} selected by priority (BT={cur.burst}) -> runs till t={end}")
            time = end
            completion[cur.pid] = time
            finished.add(cur.pid)
            last_pid = None
    return {"trace": trace, "completion": completion, "human": human, "arrivals": arrivals_map}


def simulate_rr(procs: List[Process], quantum: int) -> Dict[str, Any]:
    # Round Robin preemptive with time quantum
    if quantum <= 0:
        raise ValueError("Quantum must be > 0")
    pending = [Process(p.pid, p.arrival, p.burst, p.priority) for p in procs]
    time = 0
    queue: List[Process] = []
    trace = []
    completion = {}
    human = []
    arrivals_map = {p.pid: p.arrival for p in pending}
    n = len(pending)
    finished = set()
    # Use index to stable-order processes
    pending_by_arr = sorted(pending, key=lambda p: (p.arrival, int(p.pid[1:])))
    i = 0  # pointer to pending_by_arr
    last_pid = None
    skip_next_log: Optional[str] = None
    while len(finished) < n:
        # enqueue any newly arrived
        while i < len(pending_by_arr) and pending_by_arr[i].arrival <= time:
            queue.append(pending_by_arr[i])
            # arrival noted only when it causes a context change; suppress per-arrival spam
            # (we will mention arrivals in context-switch messages)
            i += 1
        if not queue:
            if i < len(pending_by_arr):
                nxt = pending_by_arr[i].arrival
                trace.append({"start": time, "end": nxt, "pid": "IDLE"})
                human.append(f"t={time}..{nxt}: CPU is Idle. Waiting for processes to arrive.")
                time = nxt
                continue
            else:
                break
        cur = queue.pop(0)
        run = min(quantum, cur.remaining)
        if last_pid != cur.pid:
            trace.append({"start": time, "end": time + run, "pid": cur.pid})
        else:
            trace[-1]["end"] += run
        # Log the assignment to CPU for this time-slice
        if skip_next_log == cur.pid:
            skip_next_log = None
        else:
            human.append(f"t={time}: {cur.pid} assigned CPU slice for time quantum block of {run} units.")
        cur.remaining -= run
        time += run
        # enqueue newly arrived during this quantum
        while i < len(pending_by_arr) and pending_by_arr[i].arrival <= time:
            queue.append(pending_by_arr[i])
            # defer arrival mentions to subsequent context switches
            i += 1
        # decide whether the quantum expired or process completed
        if cur.remaining > 0:
            # quantum expired: moved to back of queue
            queue.append(cur)
            # Next process (if any) will start at current time
            if queue:
                next_pid = queue[0].pid
                human.append(f"t={time}: Time quantum expired. {cur.pid} moved to back of queue. {next_pid} takes CPU.")
            else:
                human.append(f"t={time}: Time quantum expired. {cur.pid} moved to back of queue. CPU is idle.")
        else:
            completion[cur.pid] = time
            finished.add(cur.pid)
            # If there's a next process, announce it and suppress its immediate start log
            if queue:
                next_pid = queue[0].pid
                human.append(f"t={time}: {cur.pid} finishes execution completely. {next_pid} takes CPU next.")
                skip_next_log = next_pid
            else:
                human.append(f"t={time}: {cur.pid} finishes execution completely.")
        last_pid = cur.pid
    return {"trace": trace, "completion": completion, "human": human, "arrivals": arrivals_map}


### Visualization helpers
def plot_gantt(trace: List[Dict[str, Any]]) -> go.Figure:
    # Build a timeline where each PID is a row; include IDLE as separate row
    items = []
    pids = list({seg['pid'] for seg in trace})
    # Keep a stable order: IDLE last
    if 'IDLE' in pids:
        pids.remove('IDLE')
        pids.append('IDLE')
    y_map = {pid: idx for idx, pid in enumerate(pids)}
    fig = go.Figure()
    colors = {}
    for seg in trace:
        pid = seg['pid']
        start = seg['start']
        end = seg['end']
        if pid == 'IDLE':
            color = 'rgba(100,100,100,0.3)'
        else:
            # deterministic color per pid
            color = f'rgba({(hash(pid) % 200) + 30},{(hash(pid[::-1]) % 200) + 30},255,0.9)'
        fig.add_trace(go.Bar(x=[end - start], y=[pid], base=[start], orientation='h', marker=dict(color=color), showlegend=False, hovertemplate=f"{pid}: {start} -> {end}<extra></extra>"))
    fig.update_layout(barmode='stack', xaxis=dict(title='Time'), yaxis=dict(autorange='reversed'), plot_bgcolor='#0b1020', paper_bgcolor='#0b1020', font_color='#cfe8ff')
    return fig


def render_table_and_summary(df: pd.DataFrame):
    st.dataframe(df.set_index('PID'))
    avg_tat, avg_wt, formula = avg_and_formula(df)
    st.markdown("**Formulas & substitution**")
    st.code(formula)
    st.markdown(f"**Average TAT:** {avg_tat:.2f}  \n**Average WT:** {avg_wt:.2f}")


### Streamlit UI
def main():
    st.set_page_config(page_title="CPU Scheduling Simulator", layout="wide")
    # Dark theme styling via safe Streamlit settings
    st.markdown("<style>body {background-color: #0b1020; color: #cfe8ff;} .stSidebar {background-color: #071029;} </style>", unsafe_allow_html=True)
    st.sidebar.title("CPU Scheduling Simulator")
    algo = st.sidebar.radio("Algorithm", ["Home", "FCFS( First Come First Serve)", "SJF(Shortest Job First)", "SRTF(Shortest Remaining Time First)", "Priority Scheduling", "RR(Round Robin)"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("Inputs: comma-separated lists for Arrival Times and Burst Times. Example: 0,2,4")

    if algo == 'Home':
        st.title("CPU Scheduling Visualizer")
        st.markdown("Choose an algorithm from the sidebar. This app is designed for step-by-step educational traces and Gantt charts.")
        return

    with st.form(key='input_form'):
        st.subheader(algo)
        arrivals_txt = st.text_input('Arrival times (comma-separated)', value='0,2,4')
        bursts_txt = st.text_input('Burst times (comma-separated)', value='5,3,1')
        priorities_txt = st.text_input('Priorities (comma-separated, optional)', value='')
        quantum = st.number_input('Time Quantum (for Round Robin only)', min_value=1, value=2)
        preemptive = st.checkbox('Preemptive (for Priority)', value=False)
        lower_is_higher = st.checkbox('Lower number = higher priority', value=True)
        submitted = st.form_submit_button('Run')

    if not submitted:
        st.info('Fill inputs and press Run')
        return

    try:
        arrivals = parse_csv_list(arrivals_txt)
        bursts = parse_csv_list(bursts_txt)
        priorities = parse_csv_list(priorities_txt) if priorities_txt.strip() else None
        procs = to_processes(arrivals, bursts, priorities)
    except Exception as e:
        st.error(str(e))
        return

    # dispatch
    if algo == 'FCFS( First Come First Serve)':
        res = simulate_fcfs(procs)
    elif algo == 'SJF(Shortest Job First)':
        res = simulate_sjf(procs)
    elif algo == 'SRTF(Shortest Remaining Time First)':
        res = simulate_srtf(procs)
    elif algo == 'Priority Scheduling':
        res = simulate_priority(procs, preemptive=preemptive, lower_is_higher=lower_is_higher)
    elif algo == 'RR(Round Robin)':
        res = simulate_rr(procs, int(quantum))
    else:
        st.error('Unknown algorithm')
        return

    # Build metrics
    trace = res['trace']
    completion = res['completion']
    arrivals_map = res['arrivals']
    human = res['human']
    # ensure completion has entries for all
    for p in procs:
        if p.pid not in completion:
            # if not completed (shouldn't happen), set to last time
            completion[p.pid] = max([seg['end'] for seg in trace]) if trace else 0
    df = build_metrics_df(procs, completion, arrivals_map)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(plot_gantt(trace), use_container_width=True)
        st.markdown('---')
        st.markdown('**Execution trace (human-readable)**')
        for line in human:
            st.text(line)
    with col2:
        st.markdown('**Per-process metrics**')
        render_table_and_summary(df)


if __name__ == '__main__':
    main()
