from typing import Optional
import json
import re
import lsprotocol.types as lsp_types
from pygls.server import LanguageServer

NAME = "tentiris"


def _validate_json(source: str):
    """Validates json file."""
    diagnostics = []

    try:
        json.loads(source)
    except json.JSONDecodeError as err:
        msg = err.msg
        col = err.colno
        line = err.lineno

        d = lsp_types.Diagnostic(
            range=lsp_types.Range(
                start=lsp_types.Position(line=line - 1, character=col - 1),
                end=lsp_types.Position(line=line - 1, character=col),
            ),
            message=msg,
            source=NAME,
        )

        diagnostics.append(d)

    return diagnostics


def _validate(ls: LanguageServer, params):
    ls.show_message_log("Validating json...")

    text_doc = ls.workspace.get_document(params.text_document.uri)

    source = text_doc.source
    diagnostics = _validate_json(source) if source else []

    ls.publish_diagnostics(text_doc.uri, diagnostics)


async def did_open(ls, params: lsp_types.DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message("Text Document Did Open")
    _validate(ls, params)


def did_change(ls, params: lsp_types.DidChangeTextDocumentParams):
    """Text document did change notification."""
    _validate(ls, params)


def did_close(ls: LanguageServer, params: lsp_types.DidCloseTextDocumentParams):
    """Text document did close notification."""
    ls.show_message("Text Document Did Close")


def completions(
    ls,
    params: Optional[lsp_types.CompletionParams] = None,
) -> lsp_types.CompletionList:
    """Returns completion items."""
    return lsp_types.CompletionList(
        is_incomplete=False,
        items=[
            lsp_types.CompletionItem(label='"'),
            lsp_types.CompletionItem(label="["),
            lsp_types.CompletionItem(label="]"),
            lsp_types.CompletionItem(label="{"),
            lsp_types.CompletionItem(label="}"),
        ],
    )


def semantic_tokens(ls: LanguageServer, params: lsp_types.SemanticTokensParams):
    """See https://microsoft.github.io/language-server-protocol/specification#textDocument_semanticTokens
    for details on how semantic tokens are encoded."""

    TOKENS = re.compile('".*"(?=:)')

    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)

    last_line = 0
    last_start = 0

    data = []

    for lineno, line in enumerate(doc.lines):
        last_start = 0

        for match in TOKENS.finditer(line):
            start, end = match.span()
            data += [(lineno - last_line), (start - last_start), (end - start), 0, 0]

            last_line = lineno
            last_start = start

    return lsp_types.SemanticTokens(data=data)
