from tree_sitter import Language, Parser

JAVA_LANGUAGE = Language("/Users/artemancikov/Desktop/practical work/try1/build/java.so", "java")
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

with open("HelloWorld.java", "rb") as f:
    source_code = f.read()

tree = parser.parse(source_code)

method_query_str = "(method_declaration name: (identifier) @func_name (#eq? @func_name \"approve\")) @method"


#call_query_str = "(method_invocation name: (identifier) @call_name (#eq? @call_name \"approve\")) @call"
#stmt_query_str = '(expression_statement (method_invocation name: (identifier) @call_name (#eq? @call_name \"approve\"))) @stmt'
call_query_str = "(expression_statement (method_invocation name: (identifier) @call_name (#eq? @call_name \"approve\"))) @stmt (local_variable_declaration declarator: (variable_declarator value: (method_invocation name: (identifier) @call_name (#eq? @call_name \"approve\")))) @stmt"

method_query = JAVA_LANGUAGE.query(method_query_str)
call_query = JAVA_LANGUAGE.query(call_query_str)
nodes_to_delete = []


for node, capture_name in method_query.captures(tree.root_node):
    if capture_name == "method":
        nodes_to_delete.append(node)

for node, capture_name in call_query.captures(tree.root_node):
    if capture_name == "stmt":
        nodes_to_delete.append(node)

nodes_to_delete = sorted(set(nodes_to_delete), key=lambda n: n.start_byte, reverse=True)

modified_code = bytearray(source_code)

for node in nodes_to_delete:
    start = node.start_byte
    end = node.end_byte
    del modified_code[start:end]

print(modified_code.decode("utf-8"))
