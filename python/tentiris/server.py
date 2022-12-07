from pygls.server import LanguageServer
from lsprotocol import types
import logging

LOGGER = logging.getLogger(__name__)


def launch(host: str, port: int):
    server = LanguageServer("example-server", "v0.1")

    LOGGER.info(f"launch: {host}:{port}...")
    server.start_tcp(host, port)

    @server.feature(
        types.TEXT_DOCUMENT_COMPLETION,
        types.CompletionOptions(trigger_characters=[","]),
    )
    def completions(params: types.CompletionParams):
        """Returns completion items."""
        return types.CompletionList(
            is_incomplete=False,
            items=[
                types.CompletionItem(label="Item1"),
                types.CompletionItem(label="Item2"),
                types.CompletionItem(label="Item3"),
            ],
        )

    @server.command("myVerySpecialCommandName")
    def cmd_return_hello_world(ls, *args):
        return "Hello World!"


def main():
    logging.basicConfig(level=logging.INFO)
    launch("localhost", 32123)


if __name__ == "__main__":
    main()
