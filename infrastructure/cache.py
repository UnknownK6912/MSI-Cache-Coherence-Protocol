from __future__ import annotations

from infrastructure.memory import Memory
from infrastructure.stats import Stats
from infrastructure.types import BusTxn, BusTxnType, CacheLine, LineState, OpType, SnoopResult


class Cache:
    def __init__(self, coreId: int, cacheLines: int, memory: Memory, bus, stats: Stats,) -> None:
        self.coreId = coreId
        self.cacheLines = cacheLines
        self.memory = memory
        self.bus = bus
        self.stats = stats
        self.lines = [CacheLine() for c in range(cacheLines)]
    
    def access(self, op: OpType, address: int) -> None:
        if op == OpType.READ:
            self.processProcessorRead(address)
        else:
            self.processProcessorWrite(address)

    def processProcessorRead(self, address: int) -> None:
        cacheIndex, addressTag = self.computeCacheIndexAndTag(address)
        cacheLine = self.lines[cacheIndex]
        isHit = cacheLine.tag == addressTag and cacheLine.state != LineState.I
        if isHit:
            self.stats.core[self.coreId].readHits += 1
            return

        self.stats.core[self.coreId].readMisses += 1
        self.evictLineIfNeeded(cacheIndex)

        self.bus.broadcast(BusTxn(self.coreId, BusTxnType.BUSRD, address)) # no need to wait for snoop results
        self.memory.readLine(address)

        # MSI rule: read miss installs in S.
        cacheLine.tag = addressTag
        cacheLine.state = LineState.S

    def processProcessorWrite(self, address: int) -> None:
        cacheIndex, addressTag = self.computeCacheIndexAndTag(address)
        cacheLine = self.lines[cacheIndex]
        isHit = cacheLine.tag == addressTag and cacheLine.state != LineState.I

        if isHit and cacheLine.state == LineState.M:
            self.stats.core[self.coreId].writeHits += 1
            return

        if isHit and cacheLine.state == LineState.S:
            self.stats.core[self.coreId].writeHits += 1
            self.bus.broadcast(BusTxn(self.coreId, BusTxnType.BUSRDX, address))
            cacheLine.state = LineState.M
            return

        self.stats.core[self.coreId].writeMisses += 1
        self.evictLineIfNeeded(cacheIndex)
        self.bus.broadcast(BusTxn(self.coreId, BusTxnType.BUSRDX, address))
        self.memory.readLine(address)
        cacheLine.tag = addressTag
        cacheLine.state = LineState.M

    def snoop(self, txn: BusTxn) -> SnoopResult:
        cacheIndex, addressTag = self.computeCacheIndexAndTag(txn.address)
        cacheLine = self.lines[cacheIndex]
        if cacheLine.tag != addressTag or cacheLine.state == LineState.I:
            return SnoopResult()
        
        if txn.txnType == BusTxnType.BUSRD:
            if cacheLine.state == LineState.M:
                self.memory.acceptWriteback(txn.address)
                self.stats.core[self.coreId].writebacks += 1
                cacheLine.state = LineState.S
                return SnoopResult(sharedHit=True, writebackDone=True)
            if cacheLine.state == LineState.S:
                return SnoopResult(sharedHit=True)

        if txn.txnType == BusTxnType.BUSRDX:
            if cacheLine.state in (LineState.S, LineState.M):
                if cacheLine.state == LineState.M:
                    self.memory.acceptWriteback(txn.address)
                    self.stats.core[self.coreId].writebacks += 1
                cacheLine.state = LineState.I
                self.stats.core[self.coreId].invalidationsReceived += 1
                return SnoopResult(sharedHit=True, invalidations=1)
        
        if txn.txnType == BusTxnType.BUSWB:
            # Other caches only observe writeback in this simplified model.
            return SnoopResult()

        return SnoopResult()

    def evictLineIfNeeded(self, cacheIndex: int) -> None:
        cacheLine = self.lines[cacheIndex]
        if cacheLine.state != LineState.M:
            return

        # Reconstruct evicted address base from old tag+index for accounting
        evictedAddress = (cacheLine.tag * self.cacheLines) + cacheIndex
        self.bus.broadcast(BusTxn(self.coreId, BusTxnType.BUSWB, evictedAddress))
        self.memory.acceptWriteback(evictedAddress)
        self.stats.core[self.coreId].writebacks += 1

    def computeCacheIndexAndTag(self, address: int) -> tuple[int, int]:
        cacheIndex = address % self.cacheLines
        addressTag = address // self.cacheLines
        return cacheIndex, addressTag
