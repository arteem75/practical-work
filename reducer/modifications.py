from abc import abstractmethod
from tree_sitter import Language, Parser

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

    def visit_default(self, node):
        pass

    def exit_default(self, node):
        pass
    def delete_nodes(self, tree):
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
       
        #print(modified_code.decode("utf-8"))
        return modified_code.decode("utf-8")

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
        return self.delete_nodes(tree)


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
                print("No class declaration found for super call")
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
        if replace:
            return self.replace_nodes(nodes_to_remove)
        else:
            return self.remove_nodes_(nodes_to_remove)
    def remove_class(self, node_to_remove, tree):
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

    def remove_function(self, node_to_remove,tree):
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


    def remove_constructor(self, node_to_remove, tree):
        name = node_to_remove.name
        constructor_query_str = f'''(constructor_declaration name: (identifier) @ctor_name (#eq? @ctor_name "{name}")) @ctor'''
        constructor_query = JAVA_LANGUAGE.query(constructor_query_str)
        for node, capture_name in constructor_query.captures(tree.root_node):
            if capture_name == "ctor":
                self.removed_nodes.append(node)

    def remove_field(self, node_to_remove, tree):
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

            
        
    def remove_nodes_(self, nodes_to_remove: set):
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
            
        return self.delete_nodes(tree)
    
    def replace_nodes(self, nodes_to_remove: set):

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
        
        self.nodes_to_remove = nodes_to_remove
        
        for node in self.nodes_to_remove:
            name = node.name
            overload_mapping = {}

            decl_str1 = "(method_declaration type: (_) @return_type name: (identifier) @func_name parameters: (formal_parameters) @params (#eq? @func_name \""
            decl_str2 = "\"))"
            decl_query_str = decl_str1 + name + decl_str2
            decl_query = JAVA_LANGUAGE.query(decl_query_str)
            for node, capture_name in decl_query.captures(tree.root_node):
                if capture_name == "return_type":
                    rt = source_code[node.start_byte:node.end_byte].decode("utf-8").strip()
                elif capture_name == "params":
                    params_text = source_code[node.start_byte:node.end_byte].decode("utf-8").strip()
                    param_types = self.extract_param_types(params_text)
                    constant = return_mapping.get(rt)
                    if constant != None:
                        overload_mapping[param_types] = constant
            call_query_str1 ="(method_invocation name: (identifier) @call_name arguments: (argument_list) @args (#eq? @call_name \""
            call_query_str2 = "\")) @call"
            call_query_str = call_query_str1 + name + call_query_str2
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
                        arg_types = self.extract_arg_types(arg_list_node)
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
            modified_code = modified_code.decode("utf-8")
            tree = parser.parse(modified_code.encode("utf-8"))
            source_code = tree.text
        self.content = modified_code
        modified_code = self.remove_nodes_(nodes_to_remove)
        return modified_code


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
    file_name = "/Users/artemancikov/Desktop/practical work/try1/reducer/HelloWorld.java"
    #'/Users/artemancikov/Desktop/practical work/try1/generator/iter_1/Main.java'
    import utils
    content = utils.read_file(file_name)
    modifier = JavaDeclarationRemoval(content, nx.DiGraph())
    
    remove = True
    if remove:
        updated_tree = modifier.break_inheritance(
        {DeclarationNode("A", "class", None),
         DeclarationNode("B", "class", None),
         
            #DeclarationNode("approve", "function", None, args='(int a)'),
            #DeclarationNode("HelloWorld", "constructor", None),
         #DeclarationNode("foo", "function", None),
         })
        updated_tree = modifier.remove_nodes({DeclarationNode("A", "class", None),
         DeclarationNode("B", "class", None)})
    else:
        updated_tree = modifier.replace_nodes(
            {DeclarationNode("approve", "function", None),
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