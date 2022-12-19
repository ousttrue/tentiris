from typing import Optional, List, NamedTuple, Tuple, Iterable
import json
import lsprotocol.types as lsp_types
from pygls.server import LanguageServer


import tree_sitter
import logging

LOGGER = logging.getLogger(__name__)

NAME = "tentiris"

MD_LANGUAGE = tree_sitter.Language("build/my-languages.dll", "markdown")


def treesitter_parse(utf8_bytes: bytes) -> tree_sitter.Tree:
    parser = tree_sitter.Parser()
    parser.set_language(MD_LANGUAGE)
    return parser.parse(utf8_bytes)


def iter_node(
    node: tree_sitter.Node, parent: List[tree_sitter.Node]
) -> Iterable[List[tree_sitter.Node]]:
    path = [node] + parent
    yield path

    cursor = node.walk()
    if cursor.goto_first_child():
        while True:
            for child in iter_node(cursor.node, path):
                yield child
            if not cursor.goto_next_sibling():
                break


def node_contains(node: tree_sitter.Node, position: lsp_types.Position) -> bool:
    if position.line < node.start_point[0]:
        return False
    if position.line > node.end_point[0]:
        return False
    if position.line == node.start_point[0]:
        if position.character < node.start_point[1]:
            return False
        if position.line == node.end_point[0]:
            return position.character <= node.end_point[1]
        else:
            return True
    else:
        if position.line == node.end_point[0]:
            return position.character <= node.end_point[1]
        else:
            return True


def _validate_markdown(source: str):
    try:
        parsed = treesitter_parse(source.encode("utf-8"))
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
    ls: LanguageServer,
    params: lsp_types.CompletionParams,
) -> lsp_types.CompletionList:
    """ """
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    tree = treesitter_parse(doc.source.encode("utf-8"))

    active_node = None
    active_path = []
    for path in iter_node(tree.root_node, []):
        node = path[0]
        if params.position.line < node.start_point[0]:
            break
        if node_contains(node, params.position):
            active_node = node
            active_path = path

    assert active_node
    match active_node.type:
        case "document":
            return lsp_types.CompletionList(
                is_incomplete=False,
                items=[
                    lsp_types.CompletionItem(label='"', detail="quote"),
                    lsp_types.CompletionItem(label="["),
                    lsp_types.CompletionItem(label="]"),
                    lsp_types.CompletionItem(label="{"),
                    lsp_types.CompletionItem(label="}"),
                ],
            )

        case _:
            LOGGER.warn(active_path)
            return lsp_types.CompletionList(
                is_incomplete=False,
                items=[
                    lsp_types.CompletionItem(label='"', detail="quote"),
                    lsp_types.CompletionItem(label="["),
                    lsp_types.CompletionItem(label="]"),
                    lsp_types.CompletionItem(label="{"),
                    lsp_types.CompletionItem(label="}"),
                ],
            )


class SemanticToken(NamedTuple):
    start: Tuple[int, int]
    byte_len: int
    type: str
    modifiers: List[str]

    @staticmethod
    def create(node: tree_sitter.Node, type: str) -> "SemanticToken":
        # node.start_point,
        byte_len = node.end_byte - node.start_byte
        if node.start_point[0] != node.end_point[0] and node.end_point[1] == 0:
            byte_len -= 1
        return SemanticToken(node.start_point, byte_len, type, [])


def semantic_tokens_from_utf8bytes(src: bytes) -> List[SemanticToken]:
    parsed = treesitter_parse(src)

    data: List[SemanticToken] = []

    def traverse(node: tree_sitter.Node, indent=""):
        # print(f"{indent}{node}")

        match node.type:
            case "document" | "section" | "list" | "atx_heading":
                cursor = node.walk()
                if cursor.goto_first_child():
                    while True:
                        traverse(cursor.node, indent + "  ")
                        if not cursor.goto_next_sibling():
                            break
            case "inline" | "paragraph" | "fenced_code_block":
                pass
            case "atx_h1_marker" | "atx_h2_marker":
                data.append(
                    SemanticToken.create(node, lsp_types.SemanticTokenTypes.Struct)
                )
            case "list_item":
                data.append(
                    SemanticToken.create(node, lsp_types.SemanticTokenTypes.Property)
                )
            case _:
                raise NotImplementedError(node)

    traverse(parsed.root_node)

    return data


def to_relative(
    tokens: List[SemanticToken], token_types: List[str]
) -> lsp_types.SemanticTokens:
    data = []
    last: Optional[SemanticToken] = None
    for token in tokens:
        # deltaLine: (lineno - last_line)
        # deltaStart: (start - last_start)
        # length: (end - start)
        # tokenType: 0
        # tokenModifiers: 0
        deltaLine = token.start[0]
        deltaStart = token.start[1]
        if last:
            deltaLine -= last.start[0]
            if deltaLine == 0:
                deltaStart -= last.start[1]

        data += [
            deltaLine,
            deltaStart,
            token.byte_len,
            token_types.index(token.type),
            0,
        ]
        last = token

    return lsp_types.SemanticTokens(data=data)


def semantic_tokens(ls: LanguageServer, params: lsp_types.SemanticTokensParams):
    """See https://microsoft.github.io/language-server-protocol/specification#textDocument_semanticTokens
    for details on how semantic tokens are encoded."""
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    tokens = semantic_tokens_from_utf8bytes(doc.source.encode("utf-8"))
    match ls.lsp.client_capabilities:  # type: ignore
        case lsp_types.ClientCapabilities() as client_capabilities:
            return to_relative(
                tokens, client_capabilities.text_document.semantic_tokens.token_types  # type: ignore
            )
        case _:
            raise Exception()
