from typing import Optional, Any
import argparse
import logging
import lsprotocol.types as lsp_types
from pygls.server import LanguageServer
import logging
from . import commands, features
from .colorful_log_handler import ColorfulHandler


LOGGER = logging.getLogger(__name__)


def init_language_server() -> LanguageServer:
    language_server = LanguageServer("tentiris", "v0.1")

    def register_feature(
        tentiris_server, feature_name: str, f, options: Optional[Any] = None
    ):
        @tentiris_server.feature(feature_name, options)
        def wrapper(*args, **keys):
            f(tentiris_server, *args, **keys)

        return wrapper

    def register_command(tentiris_server, command_name: str, f):
        @tentiris_server.command(command_name)
        def wrapper(*args, **keys):
            f(tentiris_server, *args, **keys)

        return wrapper

    def register_thread_command(tentiris_server, command_name: str, f):
        @tentiris_server.thread()
        @tentiris_server.command(command_name)
        def wrapper(*args, **keys):
            f(tentiris_server, *args, **keys)

        return wrapper

    register_feature(
        language_server,
        lsp_types.TEXT_DOCUMENT_COMPLETION,
        features.completions,
        lsp_types.CompletionOptions(trigger_characters=[","]),
    )
    register_command(
        language_server,
        "countDownBlocking",
        commands.count_down_10_seconds_blocking,
    )
    register_command(
        language_server,
        "countDownNonBlocking",
        commands.count_down_10_seconds_non_blocking,
    )
    register_feature(
        language_server, lsp_types.TEXT_DOCUMENT_DID_CHANGE, features.did_change
    )
    register_feature(
        language_server, lsp_types.TEXT_DOCUMENT_DID_CLOSE, features.did_close
    )
    register_feature(
        language_server, lsp_types.TEXT_DOCUMENT_DID_OPEN, features.did_open
    )
    register_feature(
        language_server,
        lsp_types.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
        features.semantic_tokens,
        lsp_types.SemanticTokensLegend(token_types=["operator"], token_modifiers=[]),
    )
    register_command(language_server, "progress", commands.progress)
    register_command(
        language_server,
        "registerCompletions",
        commands.register_completions,
    )
    register_command(
        language_server,
        "showConfigurationAsync",
        commands.show_configuration_async,
    )
    register_command(
        language_server,
        "showConfigurationCallback",
        commands.show_configuration_callback,
    )
    register_thread_command(
        language_server, "showConfigurationThread", commands.show_configuration_thread
    )
    register_command(
        language_server,
        "unregisterCompletions",
        commands.unregister_completions,
    )

    return language_server


def main():
    logging.basicConfig(level=logging.INFO, handlers=[ColorfulHandler()])

    # args
    parser = argparse.ArgumentParser()
    parser.description = "simple json server example"
    parser.add_argument("--tcp", action="store_true", help="Use TCP server")
    parser.add_argument("--ws", action="store_true", help="Use WebSocket server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", type=int, default=32123, help="Bind to this port")
    args = parser.parse_args()

    # language server
    language_server = init_language_server()
    if args.tcp:
        language_server.start_tcp(args.host, args.port)
    elif args.ws:
        language_server.start_ws(args.host, args.port)
    else:
        language_server.start_io()


if __name__ == "__main__":
    main()
