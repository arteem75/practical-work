from typing import NamedTuple, List, Any

import networkx as nx
try:
    from reducer import parsers
except ImportError:
    import parsers


class DeclarationNode(NamedTuple):
    name: str
    node_type: str
    parent: Any
    #is_interface: bool = False
    args: List[str] = None #added function arguments

    def __hash__(self):
        return hash((self.name, self.node_type, self.parent, self.args))

    def __str__(self):
        node_name = f"{self.node_type}[{self.name}]"
        if self.parent is not None:
            return f"{str(self.parent)}.{node_name}"
        else:
            return node_name

    __repr__ = __str__


class GraphBuilder(parsers.TreeTraversal):
    LANGUAGE = None

    def __init__(self):
        self.graph = nx.DiGraph()

    def peek_declaration(self):
        if not self.declaration_stack:
            return None
        return self.declaration_stack[-1]

    def push_declaration(self, node):
        self.declaration_stack.append(node)

    def pop_declaration(self):
        if not self.declaration_stack:
            return None
        return self.declaration_stack.pop()

    def build_graph(self, source_file: str) -> nx.DiGraph:
        tree = parsers.parse(source_file, self.LANGUAGE)
        root_node = tree.root_node
        self.traverse_node(root_node)
        return self.graph


class JavaGraphBuilder(GraphBuilder):
    LANGUAGE = "java"

    def __init__(self):
        super().__init__()
        self.function_counter = 0
        self.state_variable_counter = 0
        self.local_variable_counter = 0
        self.declaration_stack: List[DeclarationNode] = []
        self.classes: dict = {}

    def visit_default(self, node):
        pass

    def exit_default(self, node):
        pass

    def visit_class_declaration(self, node):
        class_name = ""
        for n in node.children:
            if n.type == "identifier":
                class_name = n.text.decode("utf-8")
                break
        class_node = DeclarationNode(class_name, "class", None)
        self.graph.add_node(class_node)
        self.push_declaration(class_node)
        self.classes[class_node.name] = class_node

        for child in node.children:
            if child.type == "superclass":
                parent_name = child.text.decode("utf-8").split("extends ")[-1]
                if parent_name != class_name:
                    try:
                        parent_node = self.classes[parent_name]
                        self.graph.add_edge(parent_node, class_node,
                                            label="inherits")
                    except KeyError:
                        continue
                        #print(f"Parent class{parent_name} not found")
    def visit_interface_declaration(self, node):
        class_name = ""
        for n in node.children:
            if n.type == "identifier":
                class_name = n.text.decode("utf-8")
                break
        class_node = DeclarationNode(class_name, "class", None, is_interface=True)
        self.graph.add_node(class_node)
        self.push_declaration(class_node)
        self.classes[class_node.name] = class_node

        for child in node.children:
            if child.type == "superclass":
                parent_name = child.text.decode("utf-8").split("extends ")[-1]
                if parent_name != class_name:
                    try:
                        parent_node = self.classes[parent_name]
                        self.graph.add_edge(parent_node, class_node,
                                            label="inherits")
                    except KeyError:
                        #print(f"Parent class{parent_name} not found")
                        continue

    def exit_contract_declaration(self, ctx):
        self.pop_declaration()

    def visit_function_definition(self, node):
        func_name = None
        for n in node.children:
            if n.type == "identifier":
                func_name = n.text.decode("utf-8")
                break
        
        if func_name is None:
            raise ValueError("Function name not found in node in visit_function_definition")
        function_args = None
        for child in node.children:
            if child.type == "formal_parameters":
                function_args = child.text.decode("utf-8")
                break

        parent_node = self.peek_declaration()
        if node.type == "constructor_declaration":
            func_node = DeclarationNode(func_name, "constructor", parent_node, function_args)
        else:
            func_node = DeclarationNode(func_name, "function", parent_node, function_args)
        self.graph.add_node(func_node)
        self.push_declaration(func_node)
        self.current_function = func_node  # Set the current function context
        if parent_node is not None:
            self.graph.add_edge(parent_node, func_node, label="def")
    
    def visit_field_declaration(self, node):
        for child in node.children:
            if child.type == "variable_declarator":
                var_name_node = child.child_by_field_name("name")
                if var_name_node:
                    field_name = var_name_node.text.decode("utf-8")
                    parent_node = self.peek_declaration()
                    field_node = DeclarationNode(field_name, "field", parent_node)
                    self.graph.add_node(field_node)
                    if parent_node is not None:
                        self.graph.add_edge(parent_node, field_node, label="def")
    def visit_local_variable_declaration(self, node):
       
        parent = self.peek_declaration()

        type_node = node.child_by_field_name("type")
        var_type = type_node.text.decode("utf-8") if type_node else None

        for decl in node.children:
            if decl.type == "variable_declarator":
                name_node = decl.child_by_field_name("name")
                if not name_node:
                    continue
                var_name = name_node.text.decode("utf-8")
                # build and add our node
                local_node = DeclarationNode(var_name, "local_variable", parent)
                self.graph.add_node(local_node)
                if parent is not None:
                    self.graph.add_edge(parent, local_node, label="def")

    def exit_function_definition(self, node):
        self.pop_declaration()

    def visit_modifier_definition(self, node):
        # function_name = node.text.decode("utf-8")
        # parent_node = self.peek_declaration()
        # function_node = DeclarationNode(function_name, "function", parent_node)
        # self.graph.add_node(function_node)
        # self.push_declaration(function_node)
        # if parent_node is not None:
        #     self.graph.add_edge(parent_node, function_node, label="def")
        pass

    def exit_modifier_definition(self, node):
        # self.pop_declaration()
        pass

    def visit_event_definition(self, node):
        event_name = node.text.decode("utf-8")
        parent_node = self.peek_declaration()
        event_node = DeclarationNode(event_name, "event", parent_node)
        self.graph.add_node(event_node)
        if parent_node is not None:
            self.graph.add_edge(parent_node, event_node, label='def')
    

    def get_node_visitor(self, node):
        visitors = {
            "class_declaration": self.visit_class_declaration,
            "interface_declaration": self.visit_class_declaration,
            "method_declaration": self.visit_function_definition,
            "modifier_definition": self.visit_modifier_definition,
            "event_definition": self.visit_event_definition,
            "field_declaration": self.visit_field_declaration,
            "constructor_declaration": self.visit_function_definition,

        }
        return visitors.get(node.type, self.visit_default)

    def get_node_exit(self, node):
        exit_funcs = {
            "contract_declaration": self.exit_contract_declaration,
            "interface_declaration": self.exit_contract_declaration,
            "function_definition": self.exit_function_definition,
            "modifier_definition": self.exit_modifier_definition,
            "local_variable_declaration": self.visit_local_variable_declaration,
        }
        return exit_funcs.get(node.type, self.exit_default)


GRAPH_BUILDERS = {
    "java": JavaGraphBuilder,
}


def get_graph_builder(language: str) -> GraphBuilder:
    builder = GRAPH_BUILDERS.get(language)
    if builder is None:
        raise Exception(
            f"Graph builder for language '{language}' was not found")
    return builder


def build_graph_from_file(file_path: str, language: str) -> nx.DiGraph:
    builder = get_graph_builder(language)
    return builder().build_graph(file_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = 'reducer/HelloWorld.java'
    
    builder = JavaGraphBuilder()
    graph = builder.build_graph(file_path)
    nx.write_gml(graph, "java_graph_HelloWorld.gml")
    print(f"Graph built from {file_path} and saved to java_graph_HelloWorld.gml")
