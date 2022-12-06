from typing import BinaryIO
import sys
from pyls_jsonrpc.dispatchers import MethodDispatcher
from pyls_jsonrpc.endpoint import Endpoint
from pyls_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter


class TentirisServer(MethodDispatcher):
    def __init__(self, stdin: BinaryIO, stdout: BinaryIO):
        self.jsonrpc_stream_reader = JsonRpcStreamReader(stdin)
        self.jsonrpc_stream_writer = JsonRpcStreamWriter(stdout)
        self.endpoint = Endpoint(self, self.jsonrpc_stream_writer.write)

    def start(self):
        self.jsonrpc_stream_reader.listen(self.endpoint.consume)

    def m_initialize(self, rootUri=None, **kwargs):
        return {
            "capabilities": {
                # クイックフィックス機能
                "codeActionProvider": True,
                # コード補完機能
                "completionProvider": {
                    "resolveProvider": False,
                    "triggerCharacters": [".", "#"],
                },
                # ドキュメントのフォーマット機能
                "documentFormattingProvider": True,
                # 保存や変更時の機能
                "textDocumentSync": {
                    "change": 1,  # 変更時のリクエストにファイル内容をすべて含める（2にすると差分のみになる）
                    "save": {
                        "includeText": True,  # 保存時のリクエストに本文を含める
                    },
                    "openClose": True,  # 開閉時にイベントを発火させる
                },
                # 多分ワークスペースの切り替わりも監視するみたいな機能？（よくわかってない）
                "workspace": {
                    "workspaceFolders": {"supported": True, "changeNotifications": True}
                },
            }
        }


def launch(stdin: BinaryIO, stdout: BinaryIO):
    sls = TentirisServer(stdin, stdout)
    sls.start()


if __name__ == "__main__":
    launch(sys.stdin.buffer, sys.stdout.buffer)
