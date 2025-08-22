import re

log_path = "/Users/artemancikov/Desktop/practical-work-new/final-jdk_evaluation_results_20250821_102634/replace_mode_evaluation.log" 

iteration_pattern = re.compile(r"ITERATION\s+(\d+)\s+-")
time_pattern = re.compile(r"Execution time:\s+([\d.]+)\s+seconds")

iterations = []
times = []

with open(log_path, "r") as f:
    for line in f:
        iter_match = iteration_pattern.search(line)
        time_match = time_pattern.search(line)

        if iter_match:
            iterations.append(int(iter_match.group(1)))
        elif time_match:
            times.append(float(time_match.group(1)))

# Print header
print(f"{'Iteration':>10} | {'Execution Time (s)':>18}")
print("-" * 32)

# Print matched data
for i, t in zip(iterations, times):
    print(f"{i:10} | {t:18.6f}")
