import argparse
import time
import resource
import sys
import networkx as nx
from reducer import utils, parsers
from reducer.dd import Interesting, perform_dd
from reducer.checker import BasicPropertyChecker
from reducer.graph import build_graph_from_file
from reducer.modifications import AST_REMOVALS


soft, hard = resource.getrlimit(resource.RLIMIT_STACK)
#resource.setrlimit(resource.RLIMIT_STACK, (2**29, -1))
#resource.setrlimit(resource.RLIMIT_STACK, (min(2**29, hard), soft))

sys.setrecursionlimit(10**6)


#example Solidity:greduce --script solidity2.sh
#example C: greduce --source-file ./example.c --script ./cproperty.sh --language c

# Argument parsing
parser = argparse.ArgumentParser(
    description=('Modify Solidity files based on node removal and '
                 "Slither analysis, considering specified findings.")
)

parser.add_argument(
    "--language",
    default="java",  #"solidity",
    choices=['solidity', 'c', 'java'],
    help="Select specific language (options: 'solidity', 'c')"
)

parser.add_argument(
    "--source-file",
    type=str,
    #default="/Users/artemancikov/Desktop/practical work/try1/reducer/HelloWorld.java",
    default='/Users/artemancikov/Desktop/practical work/try1/short_tests/FunctionCalls.java',
    help="Source file to minimize",
)
parser.add_argument(
    '--script',
    type=str,
    help='script to run"',
    #default="/Users/artemancikov/Desktop/practical work/try1/reducer/runJava.sh"
    default='/Users/artemancikov/Desktop/practical work/try1/short_tests/run.sh'
)
args = parser.parse_args()


def main():
    start_time = time.time()
    file_path = args.source_file
    print(f"Using source file: {file_path}")

    graph = build_graph_from_file(file_path, args.language)
    
    print(graph)
    nx.write_gml(graph, "loljava_graph.gml")
    print(args.script)
    print(file_path)
    prop_checker = BasicPropertyChecker(file_path, args.script)
    content = utils.read_file(file_path)
    
    interesting = Interesting(graph, content,
                              prop_checker, args.language)
    



   
    passes_class = [
        ["class"]
    ]
    interesting.option = "break"
    for pass_ in passes_class:
        interesting.mode = pass_
        perform_dd(interesting, lambda n: n.node_type in pass_,
                   parallel=True)
    passes = [
    ["function"],
    ["constructor"],
    ["field"],
    ["class"]
    ]
    interesting.option = "remove"
    for i in range(10):
        for pass_ in passes:
            graph = build_graph_from_file(file_path, args.language)
            
            interesting.graph = graph
            interesting.mode = pass_
            perform_dd(interesting, lambda n: n.node_type in pass_,
                    parallel=True)
    
        
        
    interesting.option = "remove"
    passes2 = [['class'],['constructor']]
    for i in range(10):
        for pass_ in passes2:
            graph = build_graph_from_file(file_path, args.language)
            
            interesting.graph = graph
            interesting.mode = pass_
            perform_dd(interesting, lambda n: n.node_type in pass_,
                    parallel=True)
    

    for i in range(10):
        for pass_ in passes:
            graph = build_graph_from_file(file_path, args.language)
            
            interesting.graph = graph
            interesting.mode = pass_
            perform_dd(interesting, lambda n: n.node_type in pass_,
                    parallel=True)
    #one last pass
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time} seconds")


if __name__ == "__main__":
    main()

"""
refactor it to iterate until fixed point is reached 
maybe try heuristics on class removal, but keep it lightweight

improve the tool by for example using constants by calling replace_nodes


experiments:
1) run perses on these test programs (track number of tokens + test reduction time)
2) run jreduce and measure time, give the outcome of jreduce to perses; measure number of tokens + overall time (jreduce + perses)
3) compare the numbers of jreduce+perses to vanilla perses
"""

