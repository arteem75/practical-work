from abc import ABC, abstractmethod
from tree_sitter import Language, Parser

try:
    from reducer import utils
except ImportError:
    import utils


JAVA_LANGUAGE = Language("/Users/artemancikov/Desktop/practical-work-new/reducer/build/java.so", "java")
JAVA_PARSER = Parser()
JAVA_PARSER.set_language(JAVA_LANGUAGE)


PARSERS = {
    "java": JAVA_PARSER,
}


class TreeTraversal(ABC):
    @abstractmethod
    def get_node_visitor(self, node):
        pass

    @abstractmethod
    def get_node_exit(self, node):
        pass

    def traverse_node(self, node):
        # Perform action for the node type if defined
        visitor = self.get_node_visitor(node)
        visitor(node)
        # if node_type in actions:
        #     # Pass the node to the action
        #     actions[node_type](node)

        # Recurse into children
        for child in node.children:
            self.traverse_node(child)
        exit_node = self.get_node_exit(node)
        exit_node(node)


def get_parser(language: str):
    parser = PARSERS.get(language)
    if parser is None:
        raise Exception(f"Parser for language '{language}' was not found")
    return parser


def parse(file_name: str, language: str):
    parser = get_parser(language)
    file_content = utils.read_file(file_name).encode("utf-8")
    tree = parser.parse(file_content)
    return tree
