#!/bin/bash
start_time=$(date +%s)

source_file=$(find . -maxdepth 1 -name "*.java" | head -n 1)

if [ ! -f "$source_file" ]; then
    echo "Error: Could not find Java file in working directory."
    exit 1
fi

# Run using JDK 8u25, capture stderr
/Library/Java/JavaVirtualMachines/jdk1.8.0_25.jdk/Contents/Home/bin/javac "$source_file" 2> compile_err.txt

# Check for crash pattern
if grep -q "An exception has occurred in the compiler" compile_err.txt; then
    exit 0
else
    echo "Property does not hold: expected compiler crash not observed."
    cat compile_err.txt
    exit 1
fi
