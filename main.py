import sys
import pprint
from pathlib import Path

from infrastructure.simulator import Simulator
from infrastructure.trace import parseTraceFile
from infrastructure.types import Config


def printUsage() -> None:
    print("Usage:")
    print("  python main.py <tracePath> [numCores] [cacheLines] [memorySize]")
    print("")
    print("Examples:")
    print("  python main.py traces/trace_a.txt")
    print("  python main.py traces/trace_b.txt 4 8 64")


def runSimulation(tracePath: str, numberOfCores: int, numberOfCacheLines: int, memorySize: int) -> None:
    simulatorConfig = Config(
        numCores=numberOfCores,
        cacheLines=numberOfCacheLines,
        memorySize=memorySize,
    )
    traceEvents = parseTraceFile(tracePath)
    simulator = Simulator(simulatorConfig)
    simulationReport = simulator.run(traceEvents)
    pprint.pp(simulationReport, sort_dicts=False)


def pickTraceInteractive() -> str:
    available = sorted(Path(".").glob("trace_*.txt"))

    if not available:
        print("No trace files found in the current directory.")
        print("Run generate_traces.py first to create trace_a.txt / trace_b.txt / trace_c.txt")
        sys.exit(1)

    print("Available traces:")
    for i, path in enumerate(available):
        print(f"  [{i + 1}] {path.name}")

    try:
        choice = int(input("Select trace number: "))
        assert 1 <= choice <= len(available), f"Enter a number between 1 and {len(available)}"
    except ValueError:
        print("Error: Input must be a valid number")
        sys.exit(1)
    except AssertionError as e:
        print(f"Error: {e}")
        sys.exit(1)

    return str(available[choice - 1])


def main() -> None:
    # If user passes command-line values, use them.
    if len(sys.argv) >= 2:
        tracePath = sys.argv[1]
        numberOfCores = int(sys.argv[2]) if len(sys.argv) >= 3 else 4
        numberOfCacheLines = int(sys.argv[3]) if len(sys.argv) >= 4 else 8
        memorySize = int(sys.argv[4]) if len(sys.argv) >= 5 else 64
        runSimulation(tracePath, numberOfCores, numberOfCacheLines, memorySize)
        return

    # Otherwise show usage and let the user pick a trace interactively.
    printUsage()
    print("")
    print("No command-line arguments were provided.")
    print("")

    tracePath = pickTraceInteractive()

    try:
        numberOfCores = int(input("Number of cores       [default 4]: ").strip() or 4)
        numberOfCacheLines = int(input("Cache lines per cache [default 8]: ").strip() or 8)
        memorySize = int(input("Memory size (addrs)  [default 64]: ").strip() or 64)
    except ValueError:
        print("Error: configuration values must be valid integers")
        sys.exit(1)

    print("")
    runSimulation(tracePath, numberOfCores, numberOfCacheLines, memorySize)


if __name__ == "__main__":
    main()