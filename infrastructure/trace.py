from __future__ import annotations

from pathlib import Path

from msi_sim.types import OpType, TraceEvent

# function to read trace file and convert to list of TraceEvent objects

def parseTraceFile(path: str | Path) -> list[TraceEvent]:
    """
    Expected format per line:
      coreId,op,address
    Example:
      0,R,15
      2,W,15
    """
    events: list[TraceEvent] = []
    for lineNumber, raw in enumerate(Path(path).read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Invalid trace line {lineNumber}: {raw}")
        coreId = int(parts[0])
        op = OpType(parts[1])
        address = int(parts[2])
        events.append(TraceEvent(coreId=coreId, op=op, address=address))
    return events
