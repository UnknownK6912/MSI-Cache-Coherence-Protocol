from __future__ import annotations


class Memory:
    """
    The handout says data values are irrelevant.
    We still keep counters in case you want memory-side metrics later.
    """

    def __init__(self, size: int) -> None:
        self.size = size
        self.readCount = 0
        self.writebackCount = 0

    def readLine(self, address: int) -> None:
        self._checkAddress(address)
        self.readCount += 1

    def acceptWriteback(self, address: int) -> None:
        self._checkAddress(address)
        self.writebackCount += 1

    def _checkAddress(self, address: int) -> None:
        if not 0 <= address < self.size:
            raise ValueError(f"Address {address} out of range [0, {self.size - 1}]")
