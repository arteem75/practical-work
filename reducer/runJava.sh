#!/bin/bash

start_time=$(date +%s)

source_file=$1
expected_error="error: incompatible types: int cannot be converted to String"

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
if [ "$count" -ge 1 ]; then
    echo "\"$expected_error\" found $count time(s) (other errors allowed)."
    pattern_match=1
else
    echo "\"$expected_error\" not found."
    echo "Total compiler errors found: $total_errors"
    pattern_match=0
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
    echo "Total errors: $total_errors"
    echo ""
} >> reduction_results.log

# Final exit status
if [ "$pattern_match" -eq 1 ]; then
    echo "Pattern matched successfully."
    exit 0
else
    echo "Pattern not found."
    exit 1
fi
