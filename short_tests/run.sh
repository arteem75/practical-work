#!/bin/bash


start_time=$(date +%s)

source_file=$1
expected_error="error: incompatible types: possible lossy conversion from double to int"
expected_count=1

if [ -z "$source_file" ]; then
    echo "Error: No source file provided."
    exit 1
fi

# Create directory to store all reduction files
mkdir -p reduction_files
cp "$source_file" "short_tests1/original_$(basename "$source_file")"

# Compile and capture error output
javac "$source_file" 2> compile_err.txt

# Check for pattern occurrence
count=$(grep -o "$expected_error" compile_err.txt | wc -l | xargs)

# Report findings
if [ "$count" -eq "$expected_count" ]; then
    echo "\"$expected_error\" found exactly $expected_count times."
    all_patterns_match=1
else
    echo "\"$expected_error\" expected $expected_count times, but found $count times."
    all_patterns_match=0
fi

# Token counter (very basic)
count_tokens() {
    local file_path=$1
    local token_count=$(grep -o -E '\w+|[{}();]' "$file_path" | wc -l)
    echo "$token_count"
}

token_count=$(count_tokens "$source_file")
echo "Token count: $token_count"

# Save info to reduction_results
total_time=$(($(date +%s) - start_time))

{
    echo "======== REDUCTION RESULT ========"
    echo "File: $source_file"
    echo "Execution time: $total_time seconds"
    echo "Token count: $token_count"
    echo "Error matched: $count time(s)"
    echo ""
} >> reduction_results.log

# Save current analyzed version
cp "$source_file" "reduction_files/reduced_$(basename "$source_file")"

# Final exit status
if [ "$all_patterns_match" -eq 1 ]; then
    echo "Pattern matched successfully."
    exit 0
else
    echo "Pattern mismatch."
    exit 1
fi

