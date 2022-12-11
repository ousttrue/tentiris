from typing import Optional
import json
import re
import lsprotocol.types as lsp_types
from pygls.server import LanguageServer

import tree_sitter
import logging

LOGGER = logging.getLogger(__name__)

NAME = "tentiris"

MD_LANGUAGE = tree_sitter.Language("build/my-languages.dll", "markdown")


def _validate_markdown(source: str):

    parser = tree_sitter.Parser()
    parser.set_language(MD_LANGUAGE)
    try:
        parsed = parser.parse(source.encode("utf-8"))
        return []
    except Exception as e:
        LOGGER.warn(e)
        raise e


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
    ls.show_message_log("Validating markdown...")

    text_doc = ls.workspace.get_document(params.text_document.uri)

    source = text_doc.source
    diagnostics = _validate_markdown(source) if source else []

    ls.publish_diagnostics(text_doc.uri, diagnostics)


def did_open(ls, params: lsp_types.DidOpenTextDocumentParams):
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

    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)

    parser = tree_sitter.Parser()
    parser.set_language(MD_LANGUAGE)
    parsed = parser.parse(doc.source.encode("utf-8"))

    def traverse(node: tree_sitter.Node):
        LOGGER.info(node)

        cursor = node.walk()
        if cursor.goto_first_child():
            while True:
                traverse(cursor.node)
                if not cursor.goto_next_sibling():
                    break

    traverse(parsed.root_node)

    data = []

    return lsp_types.SemanticTokens(data=data)
