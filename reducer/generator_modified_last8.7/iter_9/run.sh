#!/bin/bash


start_time=$(date +%s)

source_file=$1
expected_error="error: incompatible types: possible lossy conversion from double to int"
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
    echo "\"$expected_error\" found exactly $expected_count times and no other errors present."
    all_patterns_match=1
else
    echo "\"$expected_error\" expected $expected_count times, but found $count times."
    echo "Total compiler errors found: $total_errors"
    all_patterns_match=0
fi




# Final exit status
if [ "$all_patterns_match" -eq 1 ]; then
    echo "Pattern matched successfully."
    exit 0
else
    echo "Pattern mismatch."
    exit 1
fi


