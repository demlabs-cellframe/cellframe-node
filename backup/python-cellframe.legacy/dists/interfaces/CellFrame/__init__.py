from typing import Protocol, Callable, Iterator


# PyModule_AddObject(cellframeModule, "error", CellFrame_error);

class ReplyObject(Protocol):
    pass


# DapAppCliObjectType
class AppCli(Protocol):
    pass


# DapChainNodeCliObjectType
class AppCliServer(Protocol):
    @staticmethod
    def cmdItemCreate(command: str,
                      callback: Callable[[Iterator, ReplyObject], None],
                      help_text: str, doc_ex: str, /) -> None:
        """
        [my]Add cli command
        :param callback: Iterator - command arguments
        :param doc_ex: неведомая хрень
        """
        pass

    @staticmethod
    def setReplyText(reply_text: str, reply_obj: ReplyObject) -> None:
        pass

    @staticmethod
    def getByAlias(chain_net, alias: str):
        pass
