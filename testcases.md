# 🧪 SRTF CPU Scheduling Test Cases

## Test Case 1: Standard Preemption & Tie-Breaker
This checks if your code can successfully interrupt a running process and handle a tie correctly based on arrival context.

### 📊 Process Details
| Process | Arrival Time | Burst Time |
| :--- | :---: | :---: |
| **P1** | 0 | 6 |
| **P2** | 1 | 2 |
| **P3** | 2 | 1 |

### 🔄 Expected SRTF Behavior
* **$t=0$:** **P1** starts running because it is the only option.
* **$t=1$:** **P2** arrives with $\text{BT}=2$. **P1** has 5 units left. Since $2 < 5$, **P2** preempts **P1**.
* **$t=2$:** **P3** arrives with $\text{BT}=1$. **P2** has 1 unit left. They are tied ($1 = 1$). Since **P2** arrived earlier, it keeps the CPU and finishes at $t=3$.
* **$t=3$:** Queue has **P3** ($\text{BT}=1$) and **P1** ($\text{Remaining BT}=5$). **P3** runs and finishes at $t=4$.
* **$t=4$:** **P1** finishes its remaining execution blocks from $t=4$ to $t=9$.

### 📊 Expected Gantt Chart
```text
[ P1 ] [ P2  ] [ P3 ] [   P1   ]
0      1       3      4        9

# 🧪 SRTF CPU Scheduling Test Cases

## Test Case 1: Standard Preemption & Tie-Breaker
This checks if your code can successfully interrupt a running process and handle a tie correctly based on arrival context.

### 📊 Process Details
| Process | Arrival Time | Burst Time |
| :--- | :---: | :---: |
| **P1** | 0 | 6 |
| **P2** | 1 | 2 |
| **P3** | 2 | 1 |

### 🔄 Expected SRTF Behavior
* **$t=0$:** **P1** starts running because it is the only option.
* **$t=1$:** **P2** arrives with $\text{BT}=2$. **P1** has 5 units left. Since $2 < 5$, **P2** preempts **P1**.
* **$t=2$:** **P3** arrives with $\text{BT}=1$. **P2** has 1 unit left. They are tied ($1 = 1$). Since **P2** arrived earlier, it keeps the CPU and finishes at $t=3$.
* **$t=3$:** Queue has **P3** ($\text{BT}=1$) and **P1** ($\text{Remaining BT}=5$). **P3** runs and finishes at $t=4$.
* **$t=4$:** **P1** finishes its remaining execution blocks from $t=4$ to $t=9$.

---

## Test Case 2: Multi-Stage Preemption Chain
This checks if your system can handle a cascading sequence of multiple preemptions in a row.

### 📊 Process Details
| Process | Arrival Time | Burst Time |
| :--- | :---: | :---: |
| **P1** | 0 | 9 |
| **P2** | 1 | 4 |
| **P3** | 2 | 1 |

### 🔄 Expected SRTF Behavior
* **$t=0$:** **P1** starts running.
* **$t=1$:** **P2** arrives ($\text{BT}=4$). **P1** has 8 left. Since $4 < 8$, **P2** preempts **P1**.
* **$t=2$:** **P3** arrives ($\text{BT}=1$). **P2** has 3 left. Since $1 < 3$, **P3** preempts **P2**.
* **$t=3$:** **P3** finishes at $t=3$. Now the queue has **P2** ($\text{Remaining BT}=3$) and **P1** ($\text{Remaining BT}=8$). **P2** resumes execution and runs from $t=3$ to $t=6$.
* **$t=6$:** **P2** finishes. **P1** resumes and runs until completion from $t=6$ to $t=14$.

---

## Test Case 3: The Idle Preemption Test
This checks if your preemptive loop breaks or handles things correctly when a process arrives after a period of total CPU inactivity.

### 📊 Process Details
| Process | Arrival Time | Burst Time |
| :--- | :---: | :---: |
| **P1** | 0 | 2 |
| **P2** | 5 | 3 |

### 🔄 Expected SRTF Behavior
* **$t=0$:** **P1** runs to completion from $t=0$ to $t=2$.
* **$t=2 \rightarrow t=5$:** The CPU must drop into an **IDLE** state for 3 units because the queue is empty.
* **$t=5$:** **P2** arrives and executes immediately from $t=5$ to $t=8$.

## 🧪 Priority Test Case 1: Non-Preemptive (Lower Number = Higher Priority)
This case tests if the algorithm waits for a process to finish completely before checking the priority numbers of the waiting processes.

### ⚙️ Scheduler Configuration
* **Preemptive:** ⬜ Unchecked (Non-Preemptive)
* **Priority Rule:** ☑️ Checked (Lower number = higher priority)

### 📊 Process Details
| Process | Arrival Time | Burst Time | Priority |
| :--- | :---: | :---: | :---: |
| **P1** | 0 | 5 | 3 |
| **P2** | 2 | 3 | 1 |
| **P3** | 4 | 2 | 2 |

### 🔄 Expected Behavior
* **$t=0 \rightarrow t=5$:** **P1** executes to completion. Even though it has the lowest priority (3), it is the only process in the queue at $t=0$. Because it is non-preemptive, it ignores the arrivals of **P2** (at $t=2$) and **P3** (at $t=4$).
* **$t=5 \rightarrow t=8$:** At $t=5$, **P1** finishes. Both **P2** and **P3** are waiting in the queue. **P2** wins the CPU because its priority number (1) is lower than **P3**'s (2). **P2** runs to completion.
* **$t=8 \rightarrow t=10$:** **P2** finishes, leaving only **P3** in the queue. **P3** runs until completion.

### 📊 Expected Gantt Chart
```text
[   P1   ] [  P2  ] [ P3 ]
0        5        8      10

## 🧪 RR Test Case 1: Interleaved Execution & Simultaneous Arrival
This checks if your queue structure accurately manages newly arriving processes versus processes getting kicked to the back of the line.

### ⚙️ Scheduler Configuration
* **Algorithm:** Round Robin (RR)
* **Time Quantum:** 2

### 📊 Process Details
| Process | Arrival Time | Burst Time |
| :--- | :---: | :---: |
| **P1** | 0 | 5 |
| **P2** | 1 | 2 |
| **P3** | 4 | 3 |

### 🔄 Expected RR Behavior
* **$t=0 \rightarrow t=2$:** **P1** executes. At $t=1$, **P2** arrives and enters the ready queue. At $t=2$, **P1** hits its quantum limit ($\text{Remaining BT}=3$) and is sent to the back of the queue, right behind **P2**.
* **$t=2 \rightarrow t=4$:** **P2** executes for its full burst of 2 units and finishes.
* **$t=4$:** Simultaneously, **P2** finishes and **P3** arrives. Since **P1** was already waiting in the ready queue before $t=4$, **P1** must be positioned ahead of the newcomer **P3** in the ready queue.
* **$t=4 \rightarrow t=6$:** **P1** executes ($\text{Remaining BT}=1$), hits its quantum limit, and moves behind **P3**.
* **$t=6 \rightarrow t=8$:** **P3** executes for 2 units ($\text{Remaining BT}=1$), hits its quantum limit, and moves behind **P1**.
* **$t=8 \rightarrow t=9$:** **P1** returns to the CPU and finishes its final remaining unit.
* **$t=9 \rightarrow t=10$:** **P3** returns to the CPU and finishes its final remaining unit.

### 📊 Expected Gantt Chart
```text
[ P1 ] [ P2 ] [ P1 ] [ P3 ] [P1] [P3]
0    2      4      6      8    9    10