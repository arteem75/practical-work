from tree_sitter import Language, Parser

def extract_param_types(params_text):

    params_text = params_text.strip()
    if params_text.startswith("(") and params_text.endswith(")"):
        inner = params_text[1:-1].strip()
    else:
        inner = params_text
    if not inner:
        return tuple()
    params = [p.strip() for p in inner.split(",")]
    types = []
    for p in params:
        tokens = p.split()
        if tokens:
            types.append(tokens[0])
    return tuple(types)

def get_literal_type(node):

    typemap = {
        "decimal_integer_literal": "int",
        "boolean_literal": "boolean",
        "character_literal": "char"
    }
    return typemap.get(node.type, None)

def extract_arg_types(arg_list_node, source_code):

    arg_types = []
    for child in arg_list_node.children:
        t = get_literal_type(child)
        if t is not None:
            arg_types.append(t)
    return tuple(arg_types)

JAVA_LANGUAGE = Language("/Users/artemancikov/Desktop/practical work/try1/build/java.so", "java")
parser = Parser()
parser.set_language(JAVA_LANGUAGE)

with open("HelloWorld.java", "rb") as f:
    source_code = f.read()

tree = parser.parse(source_code)


decl_query_str = r'''
(method_declaration
  type: (_) @return_type
  name: (identifier) @func_name
  parameters: (formal_parameters) @params
  (#eq? @func_name "approve")
)
'''
decl_query = JAVA_LANGUAGE.query(decl_query_str)

overload_mapping = {}
return_mapping = {
    "int": "42",
    "boolean": "true",
    "char": "'a'",
    "void": ""
}


for node, capture_name in decl_query.captures(tree.root_node):
    if capture_name == "return_type":
        rt = source_code[node.start_byte:node.end_byte].decode("utf-8").strip()
    elif capture_name == "params":
        params_text = source_code[node.start_byte:node.end_byte].decode("utf-8").strip()
        param_types = extract_param_types(params_text)
        constant = return_mapping.get(rt)
        if constant != None:
            overload_mapping[param_types] = constant


call_query_str = r'''
(method_invocation
  name: (identifier) @call_name
  arguments: (argument_list) @args
  (#eq? @call_name "approve")
) @call
'''
call_query = JAVA_LANGUAGE.query(call_query_str)

nodes_to_replace = []
call_arg_types = {}

for node, capture_name in call_query.captures(tree.root_node):
    if capture_name == "call":
        nodes_to_replace.append(node)
        arg_list_node = None
        for child in node.children:
            if child.type == "argument_list":
                arg_list_node = child
                break
        if arg_list_node:
            arg_types = extract_arg_types(arg_list_node, source_code)
        else:
            arg_types = tuple()
        call_arg_types[node] = arg_types

nodes_to_replace = sorted(set(nodes_to_replace), key=lambda n: n.start_byte, reverse=True)

modified_code = bytearray(source_code)

for node in nodes_to_replace:
    arg_types = call_arg_types[node]
    constant_value = overload_mapping.get(arg_types)
    if constant_value is None:
        continue
    replacement_text = constant_value.encode("utf-8")
    start = node.start_byte
    end = node.end_byte
    modified_code[start:end] = replacement_text

print("Modified source code:")
print(modified_code.decode("utf-8"))
