from tree_sitter import Language, Parser

# Load the previously built language library
JAVA_LANGUAGE = Language('build/java.so', 'java')

# Initialize the parser and set its language to Java
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

# A simple Java source code snippet
java_code = b"""
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
    }
}
"""

# Parse the Java code
tree = parser.parse(java_code)
root_node = tree.root_node

# Print the S-expression representation of the syntax tree
print(root_node.sexp())
