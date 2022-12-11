from tree_sitter import Language, Parser

Language.build_library(
    # Store the library in the `build` directory
    "build/my-languages.dll",
    # Include one or more languages
    [
        # https://github.com/MDeiml/tree-sitter-markdown
        "vendor/tree-sitter-markdown/tree-sitter-markdown",
    ],
)
