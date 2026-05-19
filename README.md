# Operating-System-University-Project
FCFS — First Come First Serve SJF — Shortest Job First SRTF — Shortest Remaining Time First Priority Scheduling RR — Round Robin

Act as an expert Full-Stack Python Developer and Operating Systems Instructor. I need you to build a complete, production-ready Streamlit application for my University OS Lab project (worth 20 marks). The app must simulate and visualize 5 CPU Scheduling Algorithms:

1. FCFS (First Come First Serve)

2. SJF (Shortest Job First - Non-preemptive)

3. SRTF (Shortest Remaining Time First - Preemptive)

4. Priority Scheduling (Support both Preemptive and Non-preemptive modes, with a toggle to define whether lower or higher numbers mean higher priority)

5. RR (Round Robin - Preemptive, requiring a Time Quantum input)

### CRITICAL CORE REQUIREMENTS:

1. THE CORE REWARD METRIC IS DETAILED EXPRESSION: The faculty rewards deep, granular mathematical and logical clarity. The app cannot just show final numbers. It must display:

   - Dynamic Gantt Charts: Built using Plotly or clean Altair/Streamlit native containers, clearly showing timeline blocks, idle times, and process context switches.

   - Comprehensive Metrics Table: Tracking Process ID, Arrival Time (AT), Burst Time (BT), Priority (if applicable), Completion Time (CT), Turnaround Time (TAT), and Waiting Time (WT) for every process.

   - Step-by-Step Execution Log/Trace: A sequence breakdown explaining *why* a process was chosen at time 't' (e.g., "At t=3, P2 arrived with shorter remaining time than P1, causing a preemption...").

   - Summary Statistics: Average Turnaround Time and Average Waiting Time, explicitly showing the mathematical formulas and substitution steps used to calculate them.

2. ARCHITECTURE & UX (Streamlit Native):

   - Home Page / Navigation: Implement a clean sidebar or radio menu to let users easily select an algorithm, with a persistent option to return Home or switch algorithms instantly.

   - Inputs: Users must be able to dynamically add rows for processes, or enter comma-separated values for Arrival Times, Burst Times, and Priorities. Do not hardcode inputs.

   - Visual Styling: Apply a modern, professional, ultra-clean Dark Mode UI using a rich Blue-shade color palette (e.g., deep navy backgrounds, slate sidebar, electric blue accents for active states and Gantt bars). 

3. EDUCATIONAL RIGOR (Since I am still learning):

   - Comment the Python code heavily, explaining the logic loops, arrival queue management, and preemption checks.

   - For preemptive algorithms (SRTF, RR), explicitly handle edge cases like simultaneous arrivals, CPU idling when no process has arrived, and tracking remaining burst times accurately down to 1-unit time steps.

Provide the complete, monolithic `app.py` script so I can directly run it and deploy it to my GitHub repository. Do not use placeholders or omit complex logic loops. Write robust, error-checked, math-accurate code.
