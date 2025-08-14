import os
import string
import random
# import time

import networkx as nx
import picire

from reducer import utils
from reducer.modifications import AST_REMOVALS
from reducer.checker import BasicPropertyChecker


class Interesting():
    def __init__(self, graph: nx.DiGraph,
                 content,
                 prop_checker: BasicPropertyChecker,
                 language: str):
        self.graph = graph
        self.prop_checker = prop_checker
        self.content = content
        self.language = language
        self.option = "remove"

        res = prop_checker.run_test_script(None)
        if res is None or res != 0:
            raise Exception(
                "The given property does not hold; the test script failed")

        self.reset_state()
        self.mode = None

    def reset_state(self):
        self.cache = {}
        self.removed_nodes = set()

    def __call__(self, nodes, config_id):
        return self.remove_definitions(nodes,mode=self.option)

    def remove_definitions(self, nodes, mode="remove"):
        nodes_to_remove = [
            n for n in self.graph.nodes()
            if n.node_type in self.mode and n not in nodes
        ]
        fr_nodes = frozenset(nodes)
        if fr_nodes in self.cache:
            return self.cache.get(fr_nodes)
        if not nodes_to_remove:
            return picire.Outcome.FAIL
        
        new_content = self.test_removing_definitions(nodes_to_remove, mode)
        if new_content is not None:
            self.content = new_content
            utils.update_file(self.prop_checker.file_path, new_content)
            res = picire.Outcome.FAIL
        else:
            res = picire.Outcome.PASS
        self.cache[fr_nodes] = res
        return res

    def test_removing_definitions(self, nodes_to_remove, mode="remove"):
        nodes_to_remove = set(nodes_to_remove).union(self.removed_nodes)
        ast_removal = AST_REMOVALS[self.language](self.content,
                                                  self.graph)
        if mode == "break":
            nodes_to_remove = set(filter(lambda n: n.node_type == "class", nodes_to_remove))
            modified_content = ast_removal.break_inheritance(nodes_to_remove)
        elif mode == "replace":
            modified_content = ast_removal.remove_nodes(nodes_to_remove, replace=True)
        else:
            modified_content = ast_removal.remove_nodes(nodes_to_remove)
        #modified_content = ast_removal.remove_nodes(nodes_to_remove)
        name = ''.join(random.sample(string.ascii_letters + string.digits, 5))
        if (self.language == 'solidity'):
            temp_file_path = f"{name}.sol"
        else:
            temp_file_path = f"{name}.java" #TODO: change this to java
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(modified_content)
        
        # print(f"Starting timer for test script invocation on file: {temp_file_path}")
        # script_start_time = time.time()
        
        output = self.prop_checker.run_test_script(temp_file_path)
        
        # script_end_time = time.time()
        # script_runtime = script_end_time - script_start_time
        # print(f"Test script invocation completed in {script_runtime:.6f} seconds")
        # print("\n\n")
       
        if output is not None:
            if output == 0:
                # property is satisfied because script returned zero code 0
                os.remove(temp_file_path)
                self.removed_nodes = nodes_to_remove
                return modified_content
            else:
                os.remove(temp_file_path)
                return None
        else:
            os.remove(temp_file_path)
            return None

    def get_contract_by_name(self, contract_name):
        nodes = [n for n in self.graph.nodes()
                 if n.node_type == "contract" and n.name == contract_name]
        assert len(nodes) == 1
        return nodes[0]

    def update_parse_tree(self):
        self.tree = AST_REMOVALS[self.language].setup_parse_tree(self.content)
        self.content_ = self.content

    def update_inheritance_tree(self, node):
        parents = list(self.graph.predecessors(node))
        children = set()
        for child, data in self.graph[node].items():
            if data["label"] == "inherits":
                children.add(child)
        for child in children:
            self.graph.remove_edge(node, child)
            for parent in parents:
                self.graph.add_edge(parent, child, label="inherits")

    def update_graph(self, nodes_to_remove, remove_contracts=False):
        nodes = set()
        excluded_nodes = set()
        for node in nodes_to_remove:
            if remove_contracts:
                self.update_inheritance_tree(node)
            if node not in self.graph:
                continue
            for k, v, label in nx.dfs_labeled_edges(self.graph, source=node):
                if label == "inherits":
                    excluded_nodes.add(v)
                    continue

                if k in excluded_nodes:
                    excluded_nodes.add(v)
                    continue

                nodes.add(k)
                nodes.add(v)
        self.graph.remove_nodes_from(nodes)


def perform_dd(interesting, node_filter, parallel: bool = True):
    #TODO for debugging disable parallel
    parallel = False
    dd_cls = picire.ParallelDD if parallel else picire.DD
    nodes = [n for n in interesting.graph.nodes() if node_filter(n)]
    cache = picire.parallel_dd.SharedCache(
        picire.cache.ConfigCache(cache_fail=True))
    dd_obj = dd_cls(
        interesting,
        cache=cache,
        split=picire.splitter.BalancedSplit(n=2),
        dd_star=True,
        config_iterator=picire.iterator.CombinedIterator(
            False, picire.iterator.skip,
            picire.iterator.random
        )
    )
    output_nodes = [x for x in dd_obj(nodes)]
    """
    interesting.update_graph(
        [f for f in nodes if f not in output_nodes],
        remove_contracts=False
    )
    """
    
    

    interesting.reset_state()

