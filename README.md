# MSI Cache Coherence Protocol Simulator

Python-based simulation of the MSI cache coherence protocol, modeling cache states, bus transactions, and memory interactions.
Developed as part of EECE 422: Parallel Computer Architecture and Programming (AUB).

---

## Table of Contents
1. [Design](#1-design)
2. [Implementation](#2-implementation)
3. [How to Run](#how-to-run)
4. [Experiments & Results](#3-experiments--results)
5. [Analysis](#4-analysis)

---

## 1. Design

The goal of this project is to implement a snooping-based cache coherence simulator using the MSI protocol. The system models a shared-memory multiprocessor consisting of multiple cores, each with a private cache, connected through a single atomic bus.

### System Architecture

The simulator is composed of four main components:

- **Caches:** Each core has a private direct-mapped cache with *C* lines. Each cache line stores a tag and a coherence state (M, S, or I).
- **Bus:** A shared atomic bus that serializes all transactions and broadcasts them to all caches.
- **Memory:** A simplified main memory that services read requests and accepts writebacks.
- **Statistics Module:** Tracks per-core and global metrics such as hits, misses, invalidations, and bus transactions.

### MSI Protocol Overview

Each cache line can be in one of three states:

| State | Description |
|---|---|
| **Modified (M)** | The cache has the only valid copy; memory is stale. |
| **Shared (S)** | Multiple caches may hold the line; memory is up-to-date. |
| **Invalid (I)** | The line is not valid. |

The system supports three bus transactions:

| Transaction | Issued when |
|---|---|
| **BusRd** | Read miss |
| **BusRdX** | Write miss or S→M upgrade |
| **BusWB** | Writeback to memory |

### State Transitions

| Event | Bus Transaction | Initial State | Next State |
|---|---|---|---|
| PrRd (read hit) | — | S | S |
| PrRd (read hit) | — | M | M |
| PrRd (read miss) | BusRd | I | S |
| PrWr (write hit) | — | M | M |
| PrWr (write hit/upgrade) | BusRdX | S | M |
| PrWr (write miss) | BusRdX | I | M |
| Eviction | BusWB | M | I |
| Snoop BusRd | — | S | S |
| Snoop BusRd | BusWB | M | S |
| Snoop BusRdX | — | S | I |
| Snoop BusRdX | BusWB | M | I |
| Snoop BusWB | — | any | (unchanged) |

---

## 2. Implementation

The simulator is implemented in Python using a modular design separating cache logic, bus behavior, and statistics collection.

### Cache Design

Each cache line stores a tag and a state. Address mapping is direct:

```
index = address mod C
tag   = floor(address / C)
```

### Processor Operations

**Read:**
- Hit (S or M): increment read hit counter; no bus transaction.
- Miss: evict occupant if in M (BusWB), then issue BusRd, fetch from memory, install in S.

**Write:**
- Hit in M: silent write; increment write hit counter.
- Hit in S: issue BusRdX (upgrade); invalidate all other S-state copies; transition to M.
- Miss: evict occupant if in M (BusWB), then issue BusRdX, fetch from memory, install in M.

### Snoop Logic

| Observed Transaction | Cache State | Action |
|---|---|---|
| BusRd | S | No action; report shared hit |
| BusRd | M | Broadcast BusWB; transition to S |
| BusRdX | S | Transition to I; increment `invalidationsReceived` |
| BusRdX | M | Broadcast BusWB; transition to I; increment `invalidationsReceived` |
| BusWB | any | No state change |

### Writeback Handling

All writebacks are issued as explicit **BusWB** bus transactions and simultaneously reported to memory. This covers three cases:

1. **Capacity eviction** — dirty line displaced by a new miss.
2. **Snoop BusRd** — cache holding M observes another core's read; writes back and goes S.
3. **Snoop BusRdX** — cache holding M observes another core's write; writes back and goes I.

### Bus Implementation

The bus processes one transaction at a time and broadcasts it to all caches. Each cache responds with a `SnoopResult` containing a shared-hit indicator, a writeback flag, and an invalidation count. For BusRdX transactions, the total invalidation count is attributed to the requesting core as `invalidationsCaused`.

### Statistics Collected

- Read hits / misses per core and globally
- Write hits / misses per core and globally
- Bus transaction counts: BusRd, BusRdX, BusWB
- Invalidations **received** per core
- Invalidations **caused** per core
- Writebacks per core

---

## How to Run

> **Requirements:** Python 3.10 or higher. No external libraries required.

### Step 1 — Generate a trace file

```
python generate_traces.py
```

You will be prompted to select a trace type (A, B, or C), the number of rounds, and the system configuration (N, C, M). Each run writes a `trace_a.txt`, `trace_b.txt`, or `trace_c.txt` file.

> **Note:** Three default trace files are already included in the repository (generated with N=4, C=8, M=64). If you want to run with a different number of cores, you **must** regenerate the trace to match — reusing a trace generated for N=4 with N=2 will cause a `ValueError` (invalid core ID).

### Step 2 — Run the simulator

```
python main.py <tracefile> [numCores] [cacheLines] [memorySize]
```

**Examples:**
```
python main.py trace_a.txt
python main.py trace_b.txt 4 8 64
```

If no arguments are provided, the simulator prompts you to select a trace and configuration interactively.

> Make sure the number of cores passed to `main.py` matches the number used when generating the trace.

### Project Structure

```
main.py                  — Entry point, runs the simulator
generate_traces.py       — Generates trace_a.txt / trace_b.txt / trace_c.txt
infrastructure/
    cache.py             — Cache logic and MSI state transitions
    bus.py               — Atomic bus and snoop broadcast
    memory.py            — Main memory
    stats.py             — Per-core and global statistics
    simulator.py         — Top-level simulation loop
    trace.py             — Trace file parser
    types.py             — Shared data types and enums
```

---

## 3. Experiments & Results

All experiments use the default configuration (N=4, C=8, M=64) unless otherwise stated.

### Experiment 1 — Baseline Protocol Behavior

#### Trace A: Read-Dominated Private Access
Each core repeatedly reads a disjoint set of 4 addresses over 200 rounds (200 events per core, 800 total). No two cores share a cache index.

#### Trace B: Producer-Consumer
Core 0 writes 4 shared addresses each round; Cores 1–3 read them. Repeated for 50 rounds (800 total events).

#### Trace C: Migratory Sharing
All 4 cores write a single shared address (address 0) in round-robin order, repeated for 50 rounds (200 total events).

#### Hit/Miss and Writeback Summary

| Trace | Read Hits | Read Misses | Write Hits | Write Misses | Writebacks |
|---|---|---|---|---|---|
| A | 784 | 16  | 0   | 0   | 0   |
| B | 0   | 600 | 196 | 4   | 200 |
| C | 0   | 0   | 0   | 200 | 199 |

#### Bus Transaction Summary

| Trace | BusRd | BusRdX | BusWB | Total |
|---|---|---|---|---|
| A | 16  | 0   | 0   | 16   |
| B | 600 | 200 | 200 | 1000 |
| C | 0   | 200 | 199 | 399  |

#### Invalidation Summary

| Trace | Invalidations Received | Invalidations Caused |
|---|---|---|
| A | 0   | 0   |
| B | 588 | 588 |
| C | 199 | 199 |

---

### Experiment 2 — Effect of Number of Cores

Trace B re-generated for N ∈ {2, 4, 6, 8} with C=8, M=64, 50 rounds.

| N | BusRd | BusRdX | BusWB | Total Bus Txns | Total Inv. Received |
|---|---|---|---|---|---|
| 2 | 200  | 200 | 200 | 600  | 196  |
| 4 | 600  | 200 | 200 | 1000 | 588  |
| 6 | 1000 | 200 | 200 | 1400 | 980  |
| 8 | 1400 | 200 | 200 | 1800 | 1372 |

---

### Experiment 3 — Effect of Cache Size

Trace C run with N=4, M=64, varying C ∈ {4, 8, 16, 32}.

| C  | Write Misses | Total Accesses | Miss Rate | Total Bus Txns |
|---|---|---|---|---|
| 4  | 200 | 200 | 1.000 | 399 |
| 8  | 200 | 200 | 1.000 | 399 |
| 16 | 200 | 200 | 1.000 | 399 |
| 32 | 200 | 200 | 1.000 | 399 |

---

## 4. Analysis

### Experiment 1

**Trace A:** After 16 cold misses (one BusRd per address on the first round), all 784 subsequent accesses are read hits. Lines stay in state S indefinitely since no writes occur. BusRdX, BusWB, and invalidations are all zero — the best-case outcome for MSI.

**Trace B:** Core 0's four initial writes are write misses (I→M via BusRdX). From round 2 onward, consumers leave lines in state S, so Core 0's writes become S→M upgrades via BusRdX (196 = 4×49). Each upgrade invalidates the 3 consumer caches, giving 196×3 = 588 total invalidations. Consumers always encounter read misses because Core 0's BusRdX in the same round invalidated their S copies. The 200 BusWB transactions reflect Core 0 writing back its M-state line on every consumer BusRd.

**Trace C:** A single address is written in strict round-robin by 4 cores for 50 rounds (200 events). Every write invalidates the previous M-state owner via BusRdX and triggers a BusWB — except the very first write, which finds the line in state I everywhere. This gives 200 BusRdX and 200−1 = 199 BusWB. Every access is a write miss; the 100% miss rate confirms pure migratory behavior.

### Experiment 2

BusRdX and BusWB stay constant at 200 regardless of N — Core 0's write pattern does not change. BusRd grows linearly: each additional consumer core contributes 4 addresses × 50 rounds = 200 more BusRd transactions per run. This linear scaling is a fundamental bottleneck of shared-bus snooping, motivating directory-based protocols for large core counts.

### Experiment 3

Cache size has no effect on Trace C. The single address always fits in the cache, so there are zero capacity evictions. Every miss is caused by a BusRdX invalidation from another core — a coherence miss, not a capacity miss. The miss rate stays at 1.000 and bus traffic stays at 399 across all values of C. This highlights a key insight: increasing cache size cannot help when the bottleneck is coherence invalidations.
