# 使い方
## 初期化
```python
from pygls.server import LanguageServer
language_server = LanguageServer("tentiris", "v0.1")
```

## server に feature を追加する

```python
@language_server.feature(feature_name, options)
def feature_impl(ls: language_server, params):
    ...
```

`params` は `feature_name` で決まっていて、 `lsprotocol.types.DidOpenTextDocumentParams` など。

## server に command を追加する


## 開始
標準入出力。一般的な用途
```
language_server.start_io()
```

TCP。デバッグ用途
```python
language_server.start_tcp(args.host, args.port)
```

WEBSOCKET(web browser based editor ?)
```python
language_server.start_ws(args.host, args.port)
```
