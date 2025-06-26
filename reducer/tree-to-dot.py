from tree_sitter import Language, Parser

JAVA_LANGUAGE = Language("/Users/artemancikov/Desktop/practical work/try1/reducer/build/java.so", "java")


# Initialize the parser
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

# Example Java code
java_code = b"""
public class Person {
    private String name;
    private int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public void greet() {
        int x = 5;
        System.out.println("Hello, " + name);
    }
}
"""

# Parse the code
tree = parser.parse(java_code)
root_node = tree.root_node

# Convert to DOT format
def node_id(node):
    return f"n{node.id}"

def write_dot(node, code, lines, parent_id=None):
    current_id = node_id(node)
    label = node.type.replace('"', '')  # Node type only
    lines.append(f'{current_id} [label="{label}"];')
    if parent_id:
        lines.append(f'{parent_id} -> {current_id};')
    for child in node.children:
        write_dot(child, code, lines, current_id)

lines = ['digraph G {']
write_dot(root_node, java_code, lines)
lines.append('}')

# Save the graph
with open("tree.dot", "w") as f:
    f.write('\n'.join(lines))

print("DOT file saved as tree.dot")
