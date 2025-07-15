# profile_modifications.py
from line_profiler import LineProfiler
import sys
import os
import subprocess

# Add the current directory to Python path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the modifications module
from reducer.modifications import JavaDeclarationRemoval

def main():
    # Create profiler
    profiler = LineProfiler()

    # Add all the @profile decorated functions from JavaDeclarationRemoval
    profiler.add_function(JavaDeclarationRemoval.__init__)
    profiler.add_function(JavaDeclarationRemoval.visit_default)
    profiler.add_function(JavaDeclarationRemoval.exit_default)
    profiler.add_function(JavaDeclarationRemoval.delete_nodes)
    profiler.add_function(JavaDeclarationRemoval.get_node_visitor)
    profiler.add_function(JavaDeclarationRemoval.get_node_exit)
    profiler.add_function(JavaDeclarationRemoval.is_contained)
    profiler.add_function(JavaDeclarationRemoval.filter_enclosing_nodes)
    profiler.add_function(JavaDeclarationRemoval.break_inheritance)
    profiler.add_function(JavaDeclarationRemoval.visit_super_calls)
    profiler.add_function(JavaDeclarationRemoval.visit_function_definition)
    profiler.add_function(JavaDeclarationRemoval.visit_call_expression)
    profiler.add_function(JavaDeclarationRemoval.remove_nodes)
    profiler.add_function(JavaDeclarationRemoval.remove_class)
    profiler.add_function(JavaDeclarationRemoval.remove_function)
    profiler.add_function(JavaDeclarationRemoval.remove_constructor)
    profiler.add_function(JavaDeclarationRemoval.remove_field)
    profiler.add_function(JavaDeclarationRemoval.remove_nodes_)
    profiler.add_function(JavaDeclarationRemoval.find_ancestor)
    profiler.add_function(JavaDeclarationRemoval.node_in_subtree)
    profiler.add_function(JavaDeclarationRemoval.is_read_context)
    profiler.add_function(JavaDeclarationRemoval.replace_field)
    profiler.add_function(JavaDeclarationRemoval.replace_function)
    profiler.add_function(JavaDeclarationRemoval.replace_nodes)
    profiler.add_function(JavaDeclarationRemoval.extract_param_types)
    profiler.add_function(JavaDeclarationRemoval.get_literal_type)
    profiler.add_function(JavaDeclarationRemoval.extract_arg_types)

    # Enable profiling
    profiler.enable_by_count()

    # Execute evaluator2000.py as a script
    try:
        print("Starting profiled execution of evaluator2000.py...")
        
        # Execute the evaluator2000.py file directly
        with open('evaluator2000.py', 'r') as f:
            evaluator_code = f.read()
        
        # Execute the code in the current namespace so profiling works
        exec(evaluator_code, {'__name__': '__main__'})
        
    except Exception as e:
        print(f"Error running evaluator2000: {e}")
        import traceback
        traceback.print_exc()

    # Disable profiling and print results
    profiler.disable_by_count()
    
    # Print results to console
    print("\n" + "="*80)
    print("PROFILING RESULTS")
    print("="*80)
    profiler.print_stats()
    
    # Also save results to a file
    with open('profiling_results.txt', 'w') as f:
        import io
        from contextlib import redirect_stdout
        
        with redirect_stdout(f):
            profiler.print_stats()
    
    print(f"\nProfiling results also saved to 'profiling_results.txt'")

if __name__ == "__main__":
    main()