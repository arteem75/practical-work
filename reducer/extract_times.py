import re
import sys

if len(sys.argv) > 1:
    log_path = sys.argv[1]
else:
    print("Usage: python extract_times.py <log_file_path>")
    print("Example: python extract_times.py evaluation_results_20250821_102634/replace_mode_evaluation.log")
    sys.exit(1)

iteration_pattern = re.compile(r"ITERATION\s+(\d+)\s+-")
time_pattern = re.compile(r"Execution time:\s+([\d.]+)\s+seconds")

iterations = []
times = []

try:
    with open(log_path, "r") as f:
        for line in f:
            iter_match = iteration_pattern.search(line)
            time_match = time_pattern.search(line)

            if iter_match:
                iterations.append(int(iter_match.group(1)))
            elif time_match:
                times.append(float(time_match.group(1)))
except FileNotFoundError:
    print(f"Error: Log file not found: {log_path}")
    sys.exit(1)

print(f"{'Iteration':>10} | {'Execution Time (s)':>18}")
print("-" * 32)

for i, t in zip(iterations, times):
    print(f"{i:10} | {t:18.6f}")
