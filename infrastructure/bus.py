from __future__ import annotations

from infrastructure.stats import Stats
from infrastructure.types import BusTxn, BusTxnType, SnoopResult


class Bus:
    """
    Atomic bus model: one transaction at a time, all caches snoop immediately.
    """

    def __init__(self, stats: Stats) -> None:
        self.stats = stats
        self.caches = []

    def attachCaches(self, caches: list) -> None:
        self.caches = caches

    def broadcast(self, txn: BusTxn) -> SnoopResult:
        if txn.txnType == BusTxnType.BUSRD:
            self.stats.bus.busRd += 1
        elif txn.txnType == BusTxnType.BUSRDX:
            self.stats.bus.busRdx += 1
        elif txn.txnType == BusTxnType.BUSWB:
            self.stats.bus.busWb += 1

        result = SnoopResult()
        for cache in self.caches:
            if cache.coreId == txn.srcCore:
                continue
            observed = cache.snoop(txn)
            result.sharedHit = result.sharedHit or observed.sharedHit
            result.writebackDone = result.writebackDone or observed.writebackDone
            result.invalidations += observed.invalidations
        return result
