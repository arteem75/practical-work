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




#example Solidity:greduce --script solidity2.sh
#example C: jreduce --source-file ./example.c --script ./cproperty.sh --language c

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
parser.add_argument(
    "--mode",
    choices=["remove", "replace"],
    default="remove",
    help="Choose 'remove' to only delete nodes, or 'replace' to first replace then remove.")
args = parser.parse_args()


def main():
    start_time = time.time()
    file_path = args.source_file
    print(f"Using source file: {file_path}")

    graph = build_graph_from_file(file_path, args.language)
  
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
    # if replace mode, do the replace-loop next
    fixed_point_reached = False
    if args.mode == "replace":
        passes = [["function"], ["field"]]
        interesting.option = "replace"
        
        counter = 0

        while not fixed_point_reached:
            old = utils.read_file(file_path)
            for pass_ in passes:
                interesting.mode = pass_
                perform_dd(interesting, lambda n: n.node_type in pass_, parallel=True)
            new = utils.read_file(file_path)
            fixed_point_reached = (old == new)
            counter += 1
        print("Number of replace iterations:", counter)
    passes = [
    ["function"],
    ["constructor"],
    ["field"],
    ["class"]
    ]
    fixed_point_reached = False
    interesting.option = "remove"
    graph = build_graph_from_file(file_path, args.language)
    interesting.graph = graph
    while not fixed_point_reached:
        old_content = utils.read_file(file_path)
        
        for pass_ in passes:
            
            graph = build_graph_from_file(file_path, args.language)
            
            interesting.graph = graph
            
            interesting.mode = pass_
            perform_dd(interesting, lambda n: n.node_type in pass_,
                    parallel=True)
        new_content = utils.read_file(file_path)
        if old_content == new_content:
            fixed_point_reached = True
    


   
    #one last pass
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time} seconds")
    #print("Number of all iterations:",counter)


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

