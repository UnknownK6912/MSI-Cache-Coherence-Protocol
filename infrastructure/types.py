from dataclasses import dataclass
from enum import Enum


class LineState(str, Enum):
    I = "I"
    S = "S"
    M = "M"


class BusTxnType(str, Enum):
    BUSRD = "BusRd"
    BUSRDX = "BusRdX"
    BUSWB = "BusWB"


class OpType(str, Enum):
    READ = "R"
    WRITE = "W"


@dataclass
class Config:
    numCores: int = 4
    cacheLines: int = 8
    memorySize: int = 64


@dataclass
class CacheLine:
    tag: int | None = None
    state: LineState = LineState.I


@dataclass(frozen=True)
class TraceEvent:
    coreId: int
    op: OpType
    address: int


@dataclass(frozen=True)
class BusTxn:
    srcCore: int
    txnType: BusTxnType
    address: int


@dataclass
class SnoopResult:
    sharedHit: bool = False # Indicates another cache has a valid copy (S or M).
    writebackDone: bool = False # Indicates a dirty line was written back to memory as part of this snoop.
    invalidations: int = 0 # Number of lines invalidated in this snoop (0 or 1).
