from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CoreStats:
    readHits: int = 0
    readMisses: int = 0
    writeHits: int = 0
    writeMisses: int = 0
    invalidationsReceived: int = 0
    invalidationsCaused: int = 0
    writebacks: int = 0


@dataclass
class BusStats:
    busRd: int = 0
    busRdx: int = 0
    busWb: int = 0


@dataclass
class Stats:
    core: list[CoreStats] = field(default_factory=list)
    bus: BusStats = field(default_factory=BusStats)

    @classmethod
    def forCores(cls, numCores: int) -> "Stats":
        return cls(core=[CoreStats() for _ in range(numCores)])

    def summary(self) -> dict:
        total = CoreStats(
            readHits=sum(c.readHits for c in self.core),
            readMisses=sum(c.readMisses for c in self.core),
            writeHits=sum(c.writeHits for c in self.core),
            writeMisses=sum(c.writeMisses for c in self.core),
            invalidationsReceived=sum(c.invalidationsReceived for c in self.core),
            writebacks=sum(c.writebacks for c in self.core),
        )
        return {
            "total": total,
            "perCore": self.core,
            "bus": self.bus,
            "totalBusTransactions": self.bus.busRd + self.bus.busRdx + self.bus.busWb,
        }
