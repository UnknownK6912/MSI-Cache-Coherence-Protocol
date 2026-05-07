MSI Cache Coherence Protocol Simulator
EECE 422 - Parallel Computer Architecture and Programming
Authors: Michael Iskandar, Karim Fayad

HOW TO RUN

Step 1: Generate a trace file (Not Necessary For Experiment 1 Since We Already Included Trace.txt Files)

Open generate_traces.py and run.
You will be prompted to choose a trace (A, B, or C) and the number of rounds to generate.
Each run will output a corresponding .txt file which will be read later on by main.py.

IMPORTANT: The included trace files (trace_a.txt, trace_b.txt, trace_c.txt) were
generated with N=4 cores (suitable for Experiment 1). If you want to run the simulator with a different number
of cores (for example N=2), you must regenerate the trace file using generate_traces.py
so that it only contains valid core IDs for that configuration. Reusing a trace
generated for N=4 with N=2 will cause a ValueError in Python (invalid core ID).

Step 2: Run the simulator

Open main.py, you will be asked which trace you want to use, alongside
selecting custom parameters for Number of Cores, Number of Cache Lines
and Memory Size.

Make sure the Number of Cores you select matches the number of coresused when the trace was generated.

Project Structure:

main.py                   - Entry point, runs the simulator
generate_traces.py        - Generates trace_a.txt / trace_b.txt / trace_c.txt
infrastructure/
    cache.py              - Cache logic and MSI state transitions
    bus.py                - Atomic bus and snoop broadcast
    memory.py             - Main memory
    stats.py              - Per-core and global statistics
    simulator.py          - Top-level simulation loop
    trace.py              - Trace file parser
    types.py              - Shared data types and enums