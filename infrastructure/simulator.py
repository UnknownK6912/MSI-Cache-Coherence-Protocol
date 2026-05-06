from __future__ import annotations

from dataclasses import asdict

from infrastructure.bus import Bus
from infrastructure.cache import Cache
from infrastructure.memory import Memory
from infrastructure.stats import Stats
from infrastructure.types import Config, TraceEvent


class Simulator:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.stats = Stats.forCores(config.numCores)
        self.memory = Memory(config.memorySize)
        self.bus = Bus(self.stats)
        self.caches = [
            Cache(
                coreId=i,
                cacheLines=config.cacheLines,
                memory=self.memory,
                bus=self.bus,
                stats=self.stats,
            )
            for i in range(config.numCores)
        ]
        self.bus.attachCaches(self.caches)

    def run(self, trace: list[TraceEvent]) -> dict:
        for traceEvent in trace:
            self.validateEvent(traceEvent)
            self.caches[traceEvent.coreId].access(traceEvent.op, traceEvent.address)
        return self.report()

    def report(self) -> dict:
        summary = self.stats.summary()
        return {
            "config": asdict(self.config),
            "stats": summary,
            "memory": {
                "reads": self.memory.readCount,
                "writebacks": self.memory.writebackCount,
            },
        }

    def validateEvent(self, traceEvent: TraceEvent) -> None:
        if traceEvent.coreId < 0 or traceEvent.coreId >= self.config.numCores:
            raise ValueError(f"Invalid coreId {traceEvent.coreId}")
        if traceEvent.address < 0 or traceEvent.address >= self.config.memorySize:
            raise ValueError(f"Address {traceEvent.address} out of memory range")
