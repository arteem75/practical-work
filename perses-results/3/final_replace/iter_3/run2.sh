#!/bin/bash
start_time=$(date +%s)

source_file=$(find . -maxdepth 1 -name "*.java" | head -n 1)
expected_error="error: incompatible types: int cannot be converted to Smuttier"
expected_count=1

if [ ! -f "$source_file" ]; then
    echo "Error: Could not find Java file in working directory."
    exit 1
fi

javac "$source_file" 2> compile_err.txt
count=$(grep -o "$expected_error" compile_err.txt | wc -l | xargs)
total_errors=$(grep -c "error:" compile_err.txt)

if [ "$count" -eq "$expected_count" ] && [ "$total_errors" -eq "$expected_count" ]; then
    exit 0
else
    exit 1
fi
