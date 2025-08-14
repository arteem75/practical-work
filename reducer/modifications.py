from abc import abstractmethod
from tree_sitter import Language, Parser
# import time

import networkx as nx
try:
    from reducer import parsers
    from reducer.graph import DeclarationNode
except ImportError:
    import parsers
    from graph import DeclarationNode


JAVA_LANGUAGE = Language("/Users/artemancikov/Desktop/practical work/try1/reducer/build/java.so", "java")

class ASTRemoval(parsers.TreeTraversal):
    
    def __init__(self, content, graph: nx.DiGraph):
        self.content = content
        self.graph = graph
        self.removals = []
        self.replacements = []

    
    @abstractmethod
    def remove_nodes(self, nodes_to_remove: set) -> str:
        pass


class JavaDeclarationRemoval(ASTRemoval):
    LANGUAGE = "java"
    count = 0

    
    def __init__(self, content, graph):
        super().__init__(content, graph)
        self.removed_nodes = []
        self.parser = parsers.get_parser(self.LANGUAGE)
        self.tree = self.parser.parse(content.encode("utf-8"))

    
    def visit_default(self, node):
        pass

    
    def exit_default(self, node):
        pass

    def update_tree_incrementally(self, new_content):
        old_tree = self.tree
        self.content = new_content
        self.tree = self.parser.parse(
            new_content.encode("utf-8"),
            old_tree=old_tree  
        )
    
    def delete_nodes(self, tree=None):
        if tree is None:
            tree = self.tree
        self.removed_nodes = self.filter_enclosing_nodes(self.removed_nodes) #remove duplicates and nested nodes
        self.removed_nodes.sort(key=lambda node: node.start_byte, reverse=True)
        source_code = tree.text
        modified_code = bytearray(source_code)
        #self.removed_nodes = list(set(self.removed_nodes))

        for node in self.removed_nodes:
            
            #print('deleting',node.text)
            start = node.start_byte
            end = node.end_byte
            del modified_code[start:end]

        modified_content = modified_code.decode("utf-8")
        #self.update_tree_incrementally(modified_content)

        return modified_content

    
    def get_node_visitor(self, node):
        visitors = {
            "method_declaration": self.visit_function_definition,
            "call_expression": self.visit_call_expression,
        }
        return visitors.get(node.type, self.visit_default)

    
    def get_node_exit(self, node):
        exit_funcs = {
        }
        return exit_funcs.get(node.type, self.exit_default)
    
    def is_contained(self,inner, outer):
        return (outer.start_byte <= inner.start_byte and outer.end_byte >= inner.end_byte)

    
    def filter_enclosing_nodes(self,nodes):
        result = []
        for node in nodes:
            if not any(self.is_contained(node, other) and node != other for other in nodes):
                result.append(node)
        return result
    
    def break_inheritance(self, nodes_to_remove: set):
        # print(f"Starting timer in method break_inheritance")
        # start_time = time.time()
    
        parser = parsers.get_parser(self.LANGUAGE)
        tree = parser.parse(self.content.encode("utf-8"))
        #self.visit_super_calls(tree)
        for node in nodes_to_remove:

            class_name = node.name

            query = JAVA_LANGUAGE.query(f"""
            (class_declaration
            name: (identifier) @class_name
            (#eq? @class_name "{class_name}")) @class
            """)

            captures = query.captures(tree.root_node)
            class_node = None
            for node, capture_name in captures:
                if capture_name == "class":
                    class_node = node
                    break

            if class_node is None:
                continue

            for child in class_node.children:
                if child.type == "superclass" or child.type == "super_interfaces":
                    self.removed_nodes.append(child)

            for child in class_node.children:
                if child.type != "class_body":
                    continue
                for member in child.children:
                    if member.type != "constructor_declaration":
                        continue
                    for ctor_child in member.children:
                        if ctor_child.type != "constructor_body":
                            continue
                        for statement in ctor_child.children:
                            if statement.type == "explicit_constructor_invocation":
                                ctor_field = statement.child_by_field_name("constructor")
                                if ctor_field and ctor_field.type == "super":
                                    self.removed_nodes.append(statement)
    
        result = self.delete_nodes(tree)
    
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method break_inheritance completed in {runtime:.6f} seconds")
        # print("\n\n")
    
        return result

    
    def visit_super_calls(self, tree):
        query = JAVA_LANGUAGE.query("""
        (
        (explicit_constructor_invocation
            constructor: (super)
            arguments: (argument_list) @args) @super_ctor
        )
        """)
        capt = query.captures(tree.root_node)

        for node, _ in capt:
            current = node
            while current is not None and current.type != "class_declaration":
                current = current.parent
            if current is None:
                #print("No class declaration found for super call")
                continue
            for child in current.children:
                if child.type == "superclass" or child.type == "super_interfaces":
                    self.removed_nodes.append(child)
                    break
 
            self.removed_nodes.append(node)


    
    def visit_function_definition(self, node):
        
        
        #function_name = node.children[1].text.decode("utf-8")
        function_name = None
        for n in node.children:
            if n.type == "identifier":
                function_name = n.text.decode("utf-8")
                break
        if any((node.name == function_name and node.node_type == "function")
               for node in self.nodes_to_remove):
            self.removed_nodes.append(node)
        

    
    def visit_call_expression(self, node):
        child = node.children[0]
        assert child.type == "expression"
        match child.children[0].type:
            case "member_expression":
                call_name = child.children[0].children[-1].text.decode("utf-8")
            case "identifier":
                call_name = child.children[0].text.decode("utf-8")
            case _:
                raise Exception("Unknown node")
        if any(node.name == call_name for node in self.nodes_to_remove):
            self.removed_nodes.append(node)
            current_node = node
            while True:
                match current_node.type:
                    case "assignment_expression":
                        self.removed_nodes.remove(node)
                        self.removed_nodes.append(current_node)
                        break
                    case "function_body":
                        break
                    case None:
                        break
                    case _:
                        current_node = current_node.parent
    
    def remove_nodes(self, nodes_to_remove: set, replace=False):
        # print(f"Starting timer in method remove_nodes")
        # start_time = time.time()
        
        if replace:
            result = self.replace_nodes(nodes_to_remove)
        else:
            result = self.remove_nodes_(nodes_to_remove)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method remove_nodes completed in {runtime:.6f} seconds")
        # print("\n\n")
        
        return result

    def remove_local_variable(self, node_to_remove, tree):
        # print(f"Starting timer in method remove_local_variable")
        # start_time = time.time()
        
        name = node_to_remove.name
        decl_q = JAVA_LANGUAGE.query(f"""
        (local_variable_declaration
          declarator: (variable_declarator
            name: (identifier) @var_name 
            (#eq? @var_name "{name}")
          )
        ) @decl
        """)
        for n, cap in decl_q.captures(tree.root_node):
            if cap == "decl":
                self.removed_nodes.append(n)

        id_q = JAVA_LANGUAGE.query(f"""
        (identifier) @id (#eq? @id "{name}")
        """)
        for n, cap in id_q.captures(tree.root_node):
            if cap == "id":
                stmt = self.find_ancestor(n, 'statement')
                if stmt:
                    self.removed_nodes.append(stmt)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method remove_local_variable completed in {runtime:.6f} seconds")
        # print("\n\n")

    def remove_class(self, node_to_remove, tree):
        # print(f"Starting timer in method remove_class")
        # start_time = time.time()
        
        name = node_to_remove.name

        query = JAVA_LANGUAGE.query(f"""
        (class_declaration
            name: (identifier) @class_name
            (#eq? @class_name "{name}")) @class_node
       
        """)
        query2 =  JAVA_LANGUAGE.query(f"""
                                      (interface_declaration
        name: (identifier) @interface_name
        (#eq? @interface_name "{name}")) @interface_node
         """)
        class_node = None
        for node, capture in query.captures(tree.root_node):
            if capture == "class_node":
                class_node = node
                break

        if class_node is None:
            for node, capture in query2.captures(tree.root_node):
                if capture == "interface_node":
                    class_node = node
                    break
        if class_node is None:
            # end_time = time.time()
            # runtime = end_time - start_time
            # print(f"Method remove_class completed in {runtime:.6f} seconds")
            # print("\n\n")
            return

       

        self.removed_nodes.append(class_node)

        usage_query = JAVA_LANGUAGE.query(f"""
        (object_creation_expression type: (type_identifier) @used_type
        (#eq? @used_type "{name}")) @expr

        (cast_expression type: (type_identifier) @used_type
        (#eq? @used_type "{name}")) @expr

        (local_variable_declaration
            type: (type_identifier) @used_type
            (#eq? @used_type "{name}")) @stmt

        (field_declaration
            type: (type_identifier) @used_type
            (#eq? @used_type "{name}")) @stmt
        """)
        for node, cap in usage_query.captures(tree.root_node):
            if cap in {"expr", "stmt"}:
                self.removed_nodes.append(node)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method remove_class completed in {runtime:.6f} seconds")
        # print("\n\n")

    
    def remove_function(self, node_to_remove,tree):
        # print(f"Starting timer in method remove_function")
        # start_time = time.time()
        
        name = node_to_remove.name
        method_query_str = f'''(method_declaration name: (identifier) @func_name (#eq? @func_name "{name}")) @method'''
        
        call_query_str = f'''(method_invocation name:(identifier) @call_name (#eq? @call_name "{name}")) @call'''

        method_query = JAVA_LANGUAGE.query(method_query_str)
        call_query = JAVA_LANGUAGE.query(call_query_str)
    
        for node, capture_name in method_query.captures(tree.root_node):
            if capture_name == "method":
                function_args = ""
                for child in node.children:
                    if child.type == "formal_parameters":
                        function_args = child.text.decode("utf-8")
                        break
                if function_args == node_to_remove.args:
                    self.removed_nodes.append(node)
        for node, capture_name in call_query.captures(tree.root_node):
            if capture_name == "call":
                current_node = node
                while current_node.parent is not None:
                    if current_node.type in {
                        "local_variable_declaration",
                        "assignment_expression",
                        "expression_statement",
                        "return_statement",
                        "field_declaration",
                        
                    }:
                        self.removed_nodes.append(current_node)
                        break
                    current_node = current_node.parent
        for node, capture_name in call_query.captures(tree.root_node):
            if capture_name == "call":
                self.removed_nodes.append(node)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method remove_function completed in {runtime:.6f} seconds")
        # print("\n\n")


    
    def remove_constructor(self, node_to_remove, tree):
        # print(f"Starting timer in method remove_constructor")
        # start_time = time.time()
        
        name = node_to_remove.name
        constructor_query_str = f'''(constructor_declaration name: (identifier) @ctor_name (#eq? @ctor_name "{name}")) @ctor'''
        constructor_query = JAVA_LANGUAGE.query(constructor_query_str)
        for node, capture_name in constructor_query.captures(tree.root_node):
            if capture_name == "ctor":
                self.removed_nodes.append(node)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method remove_constructor completed in {runtime:.6f} seconds")
        # print("\n\n")

    
    def remove_field(self, node_to_remove, tree):
        # print(f"Starting timer in method remove_field")
        # start_time = time.time()
        
        name = node_to_remove.name
        field_decl_query_str = f'''( (field_declaration declarator: (variable_declarator name: (identifier) @field_name value: (_) @field_value ) ) (#eq? @field_name "{name}") )'''
        field_query = JAVA_LANGUAGE.query(field_decl_query_str)

        field_access_query_str = f'''
        (expression_statement
            (assignment_expression
            left: (field_access
                    field: (identifier) @field_name
                    (#eq? @field_name "{name}")))) @stmt

        (expression_statement
            (field_access
            field: (identifier) @field_name
            (#eq? @field_name "{name}"))) @stmt

        (return_statement
            (field_access
            field: (identifier) @field_name
            (#eq? @field_name "{name}"))) @stmt'''


        access_query = JAVA_LANGUAGE.query(field_access_query_str)

        field_query = JAVA_LANGUAGE.query(field_decl_query_str)

        for node, capture_name in field_query.captures(tree.root_node):
            if capture_name == "field_value":
                self.removed_nodes.append(node)
                if node.prev_sibling is not None:
                    if node.prev_sibling.type == "=":
                        self.removed_nodes.append(node.prev_sibling)

        for node, capture_name in access_query.captures(tree.root_node):
            if capture_name == "stmt":
                self.removed_nodes.append(node)
        decl_query_str = f'''
            (field_declaration
            declarator: (variable_declarator
                name: (identifier) @field_name
                (#eq? @field_name "{name}")
            )
            ) @decl
            '''
        access_captures = access_query.captures(tree.root_node)
        decl_query = JAVA_LANGUAGE.query(decl_query_str)
        decl_captures = decl_query.captures(tree.root_node)

        if decl_captures and not access_captures:
            for node, capture_name in decl_captures:
                if capture_name == "decl":
                    self.removed_nodes.append(node)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method remove_field completed in {runtime:.6f} seconds")
        # print("\n\n")

            
        
    
    def remove_nodes_(self, nodes_to_remove: set):
        # print(f"Starting timer in method remove_nodes_")
        # start_time = time.time()
        
        self.removed_nodes = []
        self.count += 1
        parser = parsers.get_parser(self.LANGUAGE)
        tree = parser.parse(self.content.encode("utf-8"))
        self.nodes_to_remove = nodes_to_remove
       
        
        for node_to_remove in self.nodes_to_remove:
            node_type = node_to_remove.node_type
            match node_type:
                case "function":
                    self.remove_function(node_to_remove,tree)
                case "constructor":
                    self.remove_constructor(node_to_remove,tree)
                case "field":
                    self.remove_field(node_to_remove,tree)
                case "class":
                    self.remove_class(node_to_remove,tree)
                case "local_variable":
                    self.remove_local_variable(node_to_remove, tree)
        
        result = self.delete_nodes(tree)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method remove_nodes_ completed in {runtime:.6f} seconds")
        # print("\n\n")
        
        return result
    
    def find_ancestor(self,node, typ):
        cur = node.parent
        while cur:
            if cur.type == typ:
                return cur
            cur = cur.parent
        return None

    
    def node_in_subtree(self,target, root):
        if root is None:
            return False
        if target == root:
            return True
        for c in root.children:
            if self.node_in_subtree(target, c):
                return True
        return False

    
    def is_read_context(self,node):
        decl = self.find_ancestor(node, 'variable_declarator')
        if decl and decl.child_by_field_name('name') == node:
            return False

        param = self.find_ancestor(node, 'formal_parameter')
        if param and param.child_by_field_name('name') == node:
            return False

        assign = self.find_ancestor(node, 'assignment_expression')
        if assign:
            left = assign.child_by_field_name('left') or (assign.children[0] if assign.children else None)
            if left and self.node_in_subtree(node, left):
                return False

        return True
    
    def replace_field(self,node_to_replace,tree):
        # print(f"Starting timer in method replace_field")
        # start_time = time.time()
        
        name = node_to_replace.name
        access_query= JAVA_LANGUAGE.query(f'''
        ;; Initializers: int z = x; int y = this.x;
        (variable_declarator
            value: (identifier) @use
            (#eq? @use {name}))
        (variable_declarator
            value: (field_access
                    field: (identifier) @field_name
                    (#eq? @field_name {name})) @use)

        ;; RHS of assignments: z = x; z = this.x;
        (assignment_expression
            right: (identifier) @use
            (#eq? @use {name}))
        (assignment_expression
            right: (field_access
                    field: (identifier) @field_name
                    (#eq? @field_name {name})) @use)

        ;; Argument: approve(x); approve(this.x);
        (argument_list
            (identifier) @use
            (#eq? @use {name}))
        (argument_list
            (field_access
                    field: (identifier) @field_name
                    (#eq? @field_name {name})) @use)

        ;; Return: return x; return this.x;
        (return_statement
            (identifier) @use
            (#eq? @use {name}))
        (return_statement
            (field_access
                    field: (identifier) @field_name
                    (#eq? @field_name {name})) @use)

        ;; Binary expression: x + y, y + x, this.x + ... 
        (binary_expression
            left: (identifier) @use
            (#eq? @use {name}))
        (binary_expression
            right: (identifier) @use
            (#eq? @use {name}))
        (binary_expression
            left: (field_access
                    field: (identifier) @field_name
                    (#eq? @field_name {name})) @use)
        (binary_expression
            right: (field_access
                    field: (identifier) @field_name
                    (#eq? @field_name {name})) @use)
        ''')


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

     
        field_name = None #used for debugging
        field_type = None
        source_code = tree.text
        code = bytearray(source_code)
        
        for node, cap in captures:
            text = code[node.start_byte:node.end_byte].decode()
            if cap == "field_name":
                field_name = text
            elif cap == "field_type":
                field_type = text
        

        query = access_query
        captures = query.captures(tree.root_node) #capture access
        nodes_to_replace = []
        for node, cap_name in captures:
            if not self.is_read_context(node): #make sure it's not LHS
                continue
            nodes_to_replace.append(node)

        result = (nodes_to_replace,field_type)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method replace_field completed in {runtime:.6f} seconds")
        # print("\n\n")
        
        return result
       
            
    
    def replace_function(self, node_to_replace, tree):
        # print(f"Starting timer in method replace_function")
        # start_time = time.time()

        name = node_to_replace.name
        source_code = tree.text
        
        decl_query_str = f'''
            (method_declaration type: (_) @return_type 
            name: (identifier) @func_name 
            parameters: (formal_parameters) @params 
            (#eq? @func_name {name} ))'''
        
        decl_query = JAVA_LANGUAGE.query(decl_query_str)
        rt = None
        for node, capture_name in decl_query.captures(tree.root_node):
            if capture_name == "return_type":
                rt = source_code[node.start_byte:node.end_byte].decode("utf-8").strip()
            
        
        call_query_str = f'''
        (
        (method_invocation
            name: (identifier) @call_name (#eq? @call_name "{name}")
            arguments: (argument_list) @args
        ) @call
        )
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
                    arg_types = self.extract_arg_types(arg_list_node) #tried handling overloading here, if failed, just boils down to return type
                    arg_types = arg_types if arg_types else rt
                else:
                    arg_types = rt
                call_arg_types[node] = arg_types
        
        result = (nodes_to_replace,rt)
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method replace_function completed in {runtime:.6f} seconds")
        # print("\n\n")
        
        return result

    def replace_local_variable(self, node_to_replace, tree):
        # print(f"Starting timer in method replace_local_variable")
        # start_time = time.time()
        
        """
        Find *read* uses of a single local variable and return
        ([list_of_nodes], var_type).
        """
        name = node_to_replace.name
        decl_query = JAVA_LANGUAGE.query(f'''
        (local_variable_declaration
            type: (_) @var_type
            declarator: (variable_declarator
                name: (identifier) @var_name (#eq? @var_name "{name}")
            )
        )
        ''')
        var_type = None
        for n, cap in decl_query.captures(tree.root_node):
            if cap == "var_type":
                var_type = tree.text[n.start_byte:n.end_byte].decode("utf-8").strip()

        # 2) now only grab *reads* in these contexts:
        use_query = JAVA_LANGUAGE.query(f'''
        ;; initializer RHS: int x = a;
        (variable_declarator
            name: (_)
            value: (identifier) @use1 (#eq? @use1 "{name}")
        )
        ;; assignment RHS: x = a;
        (assignment_expression right: (identifier) @use2 (#eq? @use2 "{name}"))
        ;; return x;
        (return_statement (identifier) @use3 (#eq? @use3 "{name}"))
        ;; argument: foo(x)
        (argument_list (identifier) @use4 (#eq? @use4 "{name}"))
        ;; binary ops: x  y, y  x
        (binary_expression left: (identifier) @use5 (#eq? @use5 "{name}"))
        (binary_expression right: (identifier) @use6 (#eq? @use6 "{name}"))
        ''')

        to_replace = []
        for n, cap in use_query.captures(tree.root_node):
            # only the captures named use1…use6
            if cap.startswith("use") and self.is_read_context(n):
                to_replace.append(n)

        result = to_replace, var_type
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method replace_local_variable completed in {runtime:.6f} seconds")
        # print("\n\n")
        
        return result
    
    def replace_nodes(self, nodes_to_remove: set):
        # print(f"Starting timer in method replace_nodes")
        # start_time = time.time()
        
        return_mapping = {
            "int": "42",
            "boolean": "true",
            "char": "'a'",
            "void": "",
            "Boolean": "true",
            "Integer": "42",
            "String": "\"\"",
            "Object": "null",
            "double": "0.0",
            "float": "0.0f",
            "Double": "0.0",
            "Float": "0.0f",
            "byte": "0",
            "Byte": "0",
            "short": "0",
            "Short": "0",
            "long": "0L",
            "Long": "0L",
            
        }

        parser = parsers.get_parser(self.LANGUAGE)
        tree = parser.parse(self.content.encode("utf-8"))
        source_code = tree.text
        modified_code = bytearray(source_code)
        self.nodes_to_remove = nodes_to_remove
        nodes_to_replace = []
        mapping = dict()
        for node in self.nodes_to_remove:
            if node.node_type == 'field':
                fields_to_replace = self.replace_field(node,tree)
                nodes_to_replace.append(fields_to_replace)

            elif node.node_type =='function':
                functions_to_replace = self.replace_function(node,tree)
                nodes_to_replace.append(functions_to_replace)
            elif node.node_type == 'local_variable':
                locals_to_replace = self.replace_local_variable(node, tree)
                nodes_to_replace.append(locals_to_replace)
        for arr,typ in nodes_to_replace:
            for n in arr:
                mapping[n] = typ
        nodes_to_replace = [n for n, _ in nodes_to_replace]
        nodes_to_replace = [item for sub in nodes_to_replace for item in sub]


        

        nodes_to_replace = sorted(set(nodes_to_replace), key=lambda n: n.start_byte, reverse=True)
        nodes_to_replace = self.filter_enclosing_nodes(nodes_to_replace)
        modified_code = bytearray(source_code)

        for node in nodes_to_replace:
            
            constant_value = return_mapping.get(mapping.get(node, None), None)
            if constant_value is None:
                typ = mapping.get(node, None)
                if typ:
                    constant_value = f"({typ}) null"
            replacement_text = constant_value.encode("utf-8")
            start = node.start_byte
            end = node.end_byte
            modified_code[start:end] = replacement_text
        modified_code = modified_code.decode("utf-8")
        tree = parser.parse(modified_code.encode("utf-8"))
        source_code = tree.text
        self.content = modified_code
        
        result = modified_code
        
        # end_time = time.time()
        # runtime = end_time - start_time
        # print(f"Method replace_nodes completed in {runtime:.6f} seconds")
        # print("\n\n")
        
        return result

    
    def extract_param_types(self,params_text):
        #avoid string operations, replace with nodes from the parse tree
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

    
    def get_literal_type(self,node):

        typemap = {
            "decimal_integer_literal": "int",
            "boolean_literal": "boolean",
            "character_literal": "char"
        }
        return typemap.get(node.type, None)

    
    def extract_arg_types(self,arg_list_node):

        arg_types = []
        for child in arg_list_node.children:
            t = self.get_literal_type(child)
            if t is not None:
                arg_types.append(t)
        return tuple(arg_types)



AST_REMOVALS = {
    "java": JavaDeclarationRemoval,
}

if __name__ == "__main__":
    file_name = "/Users/artemancikov/Desktop/practical-work-new/reducer/HelloWorld.java"
    #'/Users/artemancikov/Desktop/practical work/try1/generator/iter_1/Main.java'
    import utils
    content = utils.read_file(file_name)
    modifier = JavaDeclarationRemoval(content, nx.DiGraph())
    
    remove = False
    if remove:
        """
        updated_tree = modifier.break_inheritance(
        {DeclarationNode("A", "class", None),
         DeclarationNode("B", "class", None),
         
            #DeclarationNode("approve", "function", None, args='(int a)'),
            #DeclarationNode("HelloWorld", "constructor", None),
         #DeclarationNode("foo", "function", None),
         })
         """
        updated_tree = modifier.remove_nodes({DeclarationNode("hw", "field", None),
         DeclarationNode("B", "class", None)})
    else:
        updated_tree = modifier.replace_nodes(
            {DeclarationNode("hw", "field", None),
            #DeclarationNode("foo", "function", None),
            })
   #print(updated_tree)
    with open("updated_tree.java", "w") as f:
        f.write(updated_tree)



"""
try to integrate with jreduce 

try to run jreduce on the given programs
try to find a minimised version of the program with jreduce
try on the generated programs to keep the introduced transformation persistand after removing as much as possible


heads up: 
need to behave well with overloading/overriding; same name/diff class
"""

"""
class A{
    int a;
    int x;
    A(int a){
        this.a = a;
    }
}
class B extends A {
    B(int a){
       
    }
    int foo(){
    print(x)
    }
}
next -> remove classes, remove all usages of all members
"""