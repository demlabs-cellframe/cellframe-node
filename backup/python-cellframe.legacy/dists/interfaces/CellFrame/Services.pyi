from typing import Protocol
from Network import Net
from DAP.Core import Math


# PyDapChainNetSrvStakePosDelegateObjectType
class StakePosDelegate(Protocol):
    def __init__(self, net) -> None: ...
    def checkValidator(self) -> bool: ...
    def checkValidatorFullInfo(self) -> StreamChChainValidatorTest: ...
    @property
    def CountValidators(self) -> dict: ...
    @property
    def TotalWeight(self) -> Math: ...


# PyDapStreamChChainValidatorTestObjectType
class StreamChChainValidatorTest(Protocol):
    pass

