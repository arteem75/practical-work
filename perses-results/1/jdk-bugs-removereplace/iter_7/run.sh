#!/bin/bash


start_time=$(date +%s)

source_file=$1
expected_error="error: incompatible types: bad type in conditional expression"
expected_count=1

if [ -z "$source_file" ]; then
    echo "Error: No source file provided."
    exit 1
fi



# Compile and capture error output
javac "$source_file" 2> compile_err.txt

# Check for pattern occurrence
count=$(grep -o "$expected_error" compile_err.txt | wc -l | xargs)

total_errors=$(grep -c "error:" compile_err.txt)

# Report findings
if [ "$count" -eq "$expected_count" ] && [ "$total_errors" -eq "$expected_count" ]; then
    all_patterns_match=1
else
    all_patterns_match=0
fi




# Final exit status
if [ "$all_patterns_match" -eq 1 ]; then
    exit 0
else
    exit 1
fi


