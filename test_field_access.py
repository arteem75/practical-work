from tree_sitter import Language, Parser

# Build the Java language library (only once)
JAVA_LANGUAGE = Language("/Users/artemancikov/Desktop/practical-work-new/reducer/build/java.so", "java")
parser = Parser()
parser.set_language(JAVA_LANGUAGE)




# Load Java test code
with open("./reducer/HelloWorld.java", "r") as f:
    code = f.read().encode()

tree = parser.parse(code)

# Query: match only read-access to field `x`
from tree_sitter import Node, Query










query = JAVA_LANGUAGE.query(r'''
  ;; 0) Initializers: int z = x; or int y = this.x;
  (variable_declarator
     value: (identifier) @use
     (#eq? @use "rails"))
  (variable_declarator
     value: (field_access
               field: (identifier) @field_name
               (#eq? @field_name "rails")) @use)

  ;; 1) RHS of assignments: z = x; or z = this.x;
  (assignment_expression
     right: (identifier) @use
     (#eq? @use "rails"))
  (assignment_expression
     right: (field_access
               field: (identifier) @field_name
               (#eq? @field_name "rails")) @use)

  ;; 2) As an argument: approve(x); or approve(this.x);
  (argument_list
     (identifier) @use
     (#eq? @use "rails"))
  (argument_list
     (field_access
               field: (identifier) @field_name
               (#eq? @field_name "rails")) @use)

  ;; 3) In a return: return x; or return this.x;
  (return_statement
     (identifier) @use
     (#eq? @use "rails"))
  (return_statement
     (field_access
               field: (identifier) @field_name
               (#eq? @field_name "rails")) @use)

  ;; 4) Inside binary expr: x + y, y + x, this.x + ... 
  (binary_expression
     left: (identifier) @use
     (#eq? @use "rails"))
  (binary_expression
     right: (identifier) @use
     (#eq? @use "rails"))
  (binary_expression
     left: (field_access
               field: (identifier) @field_name
               (#eq? @field_name "rails")) @use)
  (binary_expression
     right: (field_access
               field: (identifier) @field_name
               (#eq? @field_name "rails")) @use)
''')



captures = query.captures(tree.root_node)


# ——— Helpers ———
def find_ancestor(node, typ):
    cur = node.parent
    while cur:
        if cur.type == typ:
            return cur
        cur = cur.parent
    return None

def node_in_subtree(target, root):
    if root is None:
        return False
    if target == root:
        return True
    for c in root.children:
        if node_in_subtree(target, c):
            return True
    return False

def is_read_context(node):
    # 1) Exclude field *declaration* `int x = ...;`
    decl = find_ancestor(node, 'variable_declarator')
    if decl and decl.child_by_field_name('name') == node:
        return False

    # 2) Exclude *parameter* declarations `void f(int x)`
    param = find_ancestor(node, 'formal_parameter')
    if param and param.child_by_field_name('name') == node:
        return False

    # 3) Exclude *LHS* of any assignment: `x = ...` or `this.x = ...`
    assign = find_ancestor(node, 'assignment_expression')
    if assign:
        left = assign.child_by_field_name('left') or (assign.children[0] if assign.children else None)
        if left and node_in_subtree(node, left):
            return False

    # Otherwise it's a read
    return True

# ——— Filter & print unique reads ———
seen = set()
print("✅ Field reads of 'x':")
for node, cap_name in captures:
    if not is_read_context(node):
        continue
    key = (node.start_byte, node.end_byte)
    
    seen.add(key)
    line = node.start_point[0] + 1
    text = code[node.start_byte:node.end_byte].decode()
    print(f"  line {line}: {text}")
    print("node = ",node)

name = "rails"

decl_query_str = f'''
            (field_declaration
            type: (_) @field_type
            declarator: (variable_declarator
                name: (identifier) @field_name
                (#eq? @field_name "{name}")
            )
            ) @decl
            '''


query = JAVA_LANGUAGE.query(decl_query_str)
captures = query.captures(tree.root_node)

# ——— Extract and print ———
# captures comes as [(node, capture_name), ...] in document order
field_name = None
field_type = None
print("captures=",captures)
for node, cap in captures:
    print(node,cap)
    text = code[node.start_byte:node.end_byte].decode()
    if cap == "field_name":
        field_name = text
    elif cap == "field_type":
        field_type = text
if field_name and field_type:
    print(f"Field `{field_name}` has type `{field_type}`")
        # reset for next
