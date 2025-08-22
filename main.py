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
    description=('Modify Java files based on node removal and '
                 "AST analysis, considering specified properties.")
)

parser.add_argument(
    "--language",
    default="java",
    choices=['solidity', 'c', 'java'],
    help="Select specific language (options: 'solidity', 'c', 'java')"
)

parser.add_argument(
    "--source-file",
    type=str,
    required=True,
    help="Source file to minimize",
)
parser.add_argument(
    '--script',
    type=str,
    required=True,
    help='Test script to run'
)
parser.add_argument(
    "--mode",
    choices=["remove", "replace", "removereplace"],
    default="remove",
    help="Choose 'remove' to only delete nodes, 'replace' to replace then remove, or 'removereplace' for combined approach.")
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
        # print(f"Starting timer for pass {pass_} in mode 'break'")
        # pass_start_time = time.time()
        
        graph = build_graph_from_file(file_path, args.language)
            
        interesting.graph = graph
        interesting.mode = pass_
        perform_dd(interesting, lambda n: n.node_type in pass_,
                   parallel=True)
        
        # pass_end_time = time.time()
        # pass_runtime = pass_end_time - pass_start_time
        # print(f"Pass {pass_} in mode 'break' completed in {pass_runtime:.6f} seconds")
        # print("\n\n")
        
    graph = build_graph_from_file(file_path, args.language)
            
    interesting.graph = graph
    
  
    # if replace mode, do the replace-loop next
    fixed_point_reached = False
    if args.mode == "removereplace":
        passes = [["function"], ["field"], ["local_variable"]]
        interesting.option = "replace"
        
        counter = 0

        while not fixed_point_reached:
            # print(f"Starting timer for replace iteration {counter + 1}")
            # iteration_start_time = time.time()
            
            old = utils.read_file(file_path)
            for pass_ in passes:
                # print(f"Starting timer for pass {pass_} in mode 'replace' (iteration {counter + 1})")
                # pass_start_time = time.time()
                
                graph = build_graph_from_file(file_path, args.language)
            
                interesting.graph = graph
                interesting.mode = pass_
                perform_dd(interesting, lambda n: n.node_type in pass_, parallel=True)
                
                # pass_end_time = time.time()
                # pass_runtime = pass_end_time - pass_start_time
                # print(f"Pass {pass_} in mode 'replace' (iteration {counter + 1}) completed in {pass_runtime:.6f} seconds")
                # print("\n\n")
                
            new = utils.read_file(file_path)
            fixed_point_reached = (old == new)
            counter += 1
            
            # iteration_end_time = time.time()
            # iteration_runtime = iteration_end_time - iteration_start_time
            # print(f"Replace iteration {counter} completed in {iteration_runtime:.6f} seconds")
            # print("\n\n")
            
        print("Number of replace iterations:", counter)

    
        passes = [
        ["local_variable"],
        ["function"],
        ["constructor"],
        ["field"],
        ["class"],
        ["local_variable", "function","field"]

        ]
        fixed_point_reached = False
        graph = build_graph_from_file(file_path, args.language)
        prop_checker = BasicPropertyChecker(file_path, args.script)
        content = utils.read_file(file_path)
        interesting = Interesting(graph, content,
                                prop_checker, args.language)
        interesting.option = "remove"
        
        remove_iteration_counter = 0
        
        while not fixed_point_reached:
            remove_iteration_counter += 1
            # print(f"Starting timer for remove iteration {remove_iteration_counter}")
            # iteration_start_time = time.time()
            
            old_content = utils.read_file(file_path)
            
            for pass_ in passes:
                # print(f"Starting timer for pass {pass_} in mode 'remove' (iteration {remove_iteration_counter})")
                # pass_start_time = time.time()
                
                graph = build_graph_from_file(file_path, args.language)
                prop_checker = BasicPropertyChecker(file_path, args.script)
                content = utils.read_file(file_path)
                interesting = Interesting(graph, content,
                                        prop_checker, args.language)
                interesting.mode = pass_
                perform_dd(interesting, lambda n: n.node_type in pass_,
                        parallel=False)
                
                # pass_end_time = time.time()
                # pass_runtime = pass_end_time - pass_start_time
                # print(f"Pass {pass_} in mode 'remove' (iteration {remove_iteration_counter}) completed in {pass_runtime:.6f} seconds")
                # print("\n\n")
                
            new_content = utils.read_file(file_path)
            if old_content == new_content:
                fixed_point_reached = True
                
            # iteration_end_time = time.time()
            # iteration_runtime = iteration_end_time - iteration_start_time
            # print(f"Remove iteration {remove_iteration_counter} completed in {iteration_runtime:.6f} seconds")
            # print("\n\n")
    elif args.mode == "remove":
        passes = [
        ["local_variable"],
        ["function"],
        ["constructor"],
        ["field"],
        ["class"],

        ]
        fixed_point_reached = False
        graph = build_graph_from_file(file_path, args.language)
        prop_checker = BasicPropertyChecker(file_path, args.script)
        content = utils.read_file(file_path)
        interesting = Interesting(graph, content,
                                prop_checker, args.language)
        interesting.option = "remove"
        
        remove_iteration_counter = 0
        
        while not fixed_point_reached:
            remove_iteration_counter += 1
            # print(f"Starting timer for remove iteration {remove_iteration_counter}")
            # iteration_start_time = time.time()
            
            old_content = utils.read_file(file_path)
            
            for pass_ in passes:
                # print(f"Starting timer for pass {pass_} in mode 'remove' (iteration {remove_iteration_counter})")
                # pass_start_time = time.time()
                
                graph = build_graph_from_file(file_path, args.language)
                prop_checker = BasicPropertyChecker(file_path, args.script)
                content = utils.read_file(file_path)
                interesting = Interesting(graph, content,
                                        prop_checker, args.language)
                interesting.mode = pass_
                perform_dd(interesting, lambda n: n.node_type in pass_,
                        parallel=False)
                
                # pass_end_time = time.time()
                # pass_runtime = pass_end_time - pass_start_time
                # print(f"Pass {pass_} in mode 'remove' (iteration {remove_iteration_counter}) completed in {pass_runtime:.6f} seconds")
                # print("\n\n")
                
            new_content = utils.read_file(file_path)
            if old_content == new_content:
                fixed_point_reached = True
                
            # iteration_end_time = time.time()
            # iteration_runtime = iteration_end_time - iteration_start_time
            # print(f"Remove iteration {remove_iteration_counter} completed in {iteration_runtime:.6f} seconds")
            # print("\n\n")

    elif args.mode == "replace":
        passes = [["function"], ["field"], ["local_variable"]]
        interesting.option = "replace"
        
        counter = 0

        while not fixed_point_reached:
            # print(f"Starting timer for replace iteration {counter + 1}")
            # iteration_start_time = time.time()
            
            old = utils.read_file(file_path)
            for pass_ in passes:
                # print(f"Starting timer for pass {pass_} in mode 'replace' (iteration {counter + 1})")
                # pass_start_time = time.time()
                
                graph = build_graph_from_file(file_path, args.language)
            
                interesting.graph = graph
                interesting.mode = pass_
                perform_dd(interesting, lambda n: n.node_type in pass_, parallel=True)
                
                # pass_end_time = time.time()
                # pass_runtime = pass_end_time - pass_start_time
                # print(f"Pass {pass_} in mode 'replace' (iteration {counter + 1}) completed in {pass_runtime:.6f} seconds")
                # print("\n\n")
                
            new = utils.read_file(file_path)
            fixed_point_reached = (old == new)
            counter += 1
            
            # iteration_end_time = time.time()
            # iteration_runtime = iteration_end_time - iteration_start_time
            # print(f"Replace iteration {counter} completed in {iteration_runtime:.6f} seconds")
            # print("\n\n")
            
        print("Number of replace iterations:", counter)

   
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time} seconds")
    #print("Number of all iterations:",counter)


if __name__ == "__main__":
    main()
