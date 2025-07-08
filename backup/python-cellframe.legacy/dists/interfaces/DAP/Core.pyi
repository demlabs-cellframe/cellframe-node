from typing import Protocol


# DapLogitObjectType
class logIt(Protocol):
    @staticmethod
    def debug(message: str, name_plugin: str = "", /):
        """
        Log a message with the DEBUG level.
        """
        pass

    @staticmethod
    def info(message: str, name_plugin: str = "", /):
        """
        Log a message with the INFO level.
        """
        pass

    @staticmethod
    def notice(message: str, name_plugin: str = "", /):
        """
        Log a message with the NOTICE level.
        """
        pass

    @staticmethod
    def message(message: str, name_plugin: str = "", /):
        """
        Log a message with the MESSAGE level.
        """
        pass

    @staticmethod
    def dap(message: str, name_plugin: str = "", /):
        """
        Log a message with the DAP level.
        """
        pass

    @staticmethod
    def warning(message: str, name_plugin: str = "", /):
        """
        Log a message with the WARNING level.
        """
        pass

    @staticmethod
    def att(message: str, name_plugin: str = "", /):
        """
        Log a message with the ATT level.
        """
        pass

    @staticmethod
    def error(message: str, name_plugin: str = "", /):
        """
        Log a message with the ERROR level.
        """
        pass

    @staticmethod
    def critical(message: str, name_plugin: str = "", /):
        """
        Log a message with the CRITICAL level.
        """
        pass

# DapCommonObjectType
class Common(Protocol):
    pass

# DapMathObjectType
class Math(Protocol):
    def __init__(self, number: str) -> None: ...
    def __add__(self, other: Math | int) -> Math: ...
    def __sub__(self, other: Math | int) -> Math: ...
    def __mul__(self, other: Math | int) -> Math: ...
    def __truediv__(self, other: Math | int) -> Math: ...
    def __floordiv__(self, other: Math | int) -> Math: ...
    def __mod__(self, other: Math | int) -> Math: ...
    def __divmod__(self, other: Math | int) -> Math: ...
    def __pow__(self, power: Math, modulo=None) -> Math: ...
    def __float__(self) -> float: ...
    def __lt__(self, other: Math) -> bool: ...
    def __le__(self, other: Math) -> bool: ...
    def __eq__(self, other: Math) -> bool: ...
    def __ne__(self, other: Math) -> bool: ...
    def __gt__(self, other: Math) -> bool: ...
    def __ge__(self, other: Math) -> bool: ...
    @property
    def coins(self) -> str: ...
    @property
    def balance(self) -> str: ...
    @staticmethod
    def balance_to_coins(value: int) -> str: ...
    def percent(self, value: Math | int) -> Math: ...

    pass

#D apAppContextObjectType
class AppContext(Protocol):
    @staticmethod
    def getServer(server, /):
        """Get main server from node"""
        pass

    @staticmethod
    def getHttp(server, /):
        pass

class NodeAddr(Protocol):
    def __init__(self, address : str) -> None: ...
    def __str__(self) -> str: ...
    pass