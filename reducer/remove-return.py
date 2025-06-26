from tree_sitter import Language, Parser
import os
grammar = Language('build/java.so', 'java')
parser = Parser()
parser.set_language(grammar)

def find_nodes(node):
    nodes = []
    if node.type == "return_statement":
        nodes.append(node)
    for child in node.children:
        nodes.extend(find_nodes(child))
    return nodes

def remove_return(code):
    tree = parser.parse(code)
    root_node = tree.root_node



    return_nodes = find_nodes(root_node)


    modified_code = bytearray(code)

    for node in sorted(return_nodes, key=lambda n: n.start_byte, reverse=True):
        del modified_code[node.start_byte:node.end_byte]

    output = modified_code.decode("utf-8")
    return output


def print_function_names(node, source_code):
    # Check if this node is a method_declaration.
    if node.type == "method_declaration":
        # Get the child node that represents the function name.
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            # Slice the source code using the byte offsets.
            function_name = source_code[name_node.start_byte:name_node.end_byte].decode("utf-8")
            print("Found function:", function_name)
    # Recurse into children.
    for child in node.children:
        print_function_names(child, source_code)

with open('HelloWorld.java', "rb") as f:
            content = f.read()
tree = parser.parse(content)

print_function_names(tree.root_node, content)


"""
path = './generator/'
for root, dirs, files in os.walk(path):
    if "Main.java" in files:
        main_path = os.path.join(root, "Main.java")
        removed_path = os.path.join(root, "Removed.java")
        
        # Read the content of Main.java
        with open(main_path, "rb") as f:
            content = f.read()
        
        output = remove_return(content)
        
        with open(removed_path, "w", encoding="utf-8") as f:
            f.write(output)
        
        print(f"Processed '{main_path}' -> '{removed_path}'")

#https://til.simonwillison.net/python/tree-sitter
"""