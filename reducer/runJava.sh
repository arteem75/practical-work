#!/bin/bash


start_time=$(date +%s)

source_file=$1
expected_error="error: incompatible types: Object cannot be converted to String"
expected_count=1

if [ -z "$source_file" ]; then
    echo "Error: No source file provided."
    exit 1
fi

# Create directory to store all reduction files
mkdir -p reduction_files
cp "$source_file" "original_$(basename "$source_file")"

# Compile and capture error output
javac "$source_file" 2> compile_err.txt

# Check for pattern occurrence
count=$(grep -o "$expected_error" compile_err.txt | wc -l | xargs)
total_errors=$(grep -c "error:" compile_err.txt)

# Report findings
if [ "$count" -eq "$expected_count" ] && [ "$total_errors" -eq "$expected_count" ]; then
    echo "\"$expected_error\" found exactly $expected_count times and no other errors present."
    all_patterns_match=1
else
    echo "\"$expected_error\" expected $expected_count times, but found $count times."
    echo "Total compiler errors found: $total_errors"
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


# Final exit status
if [ "$all_patterns_match" -eq 1 ]; then
    echo "Pattern matched successfully."
    exit 0
else
    echo "Pattern mismatch."
    exit 1
fi


