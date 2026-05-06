import sys
import pprint

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


def main() -> None:
    # If user passes command-line values, use them.
    if len(sys.argv) >= 2:
        tracePath = sys.argv[1]
        numberOfCores = int(sys.argv[2]) if len(sys.argv) >= 3 else 4
        numberOfCacheLines = int(sys.argv[3]) if len(sys.argv) >= 4 else 8
        memorySize = int(sys.argv[4]) if len(sys.argv) >= 5 else 64
        runSimulation(tracePath, numberOfCores, numberOfCacheLines, memorySize)
        return

    # Otherwise show usage and run a very explicit default example.
    printUsage()
    print("")
    print("No command-line arguments were provided.")
    print("Trying default demo trace: traces/smoke_trace.txt")
    print("")
    runSimulation(
        tracePath="traces/smoke_trace.txt",
        numberOfCores=4,
        numberOfCacheLines=8,
        memorySize=64,
    )


if __name__ == "__main__":
    main()
