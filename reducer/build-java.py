from tree_sitter import Language

# This will compile the Java parser into a shared library.
Language.build_library(
    # The path to the output shared library.
    'build/java.so',
    # A list of paths to the language repositories.
    [
        'tree-sitter-java'
    ]
)
