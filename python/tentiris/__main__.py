import argparse
import logging

from .server import json_server

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def add_arguments(parser):
    parser.description = "simple json server example"

    parser.add_argument("--tcp", action="store_true", help="Use TCP server")
    parser.add_argument("--ws", action="store_true", help="Use WebSocket server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", type=int, default=32123, help="Bind to this port")


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.tcp:
        json_server.start_tcp(args.host, args.port)
    elif args.ws:
        json_server.start_ws(args.host, args.port)
    else:
        json_server.start_io()


if __name__ == "__main__":
    main()
