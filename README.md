# JREDUCE

Semantic Aware Program Reducer for Java

## Overview

This project implements a program reduction tool that can:
- **Remove** declarations (classes, methods, fields, variables)
- **Replace** code elements with constants/null values
- **Break inheritance** relationships

## Usage

### Basic Command
```bash
python3 -m main --source-file <file.java> --script <test_script.sh> --mode <remove|replace>
```

### Modes
- `remove`: Only removes code elements
- `replace`: Replaces elements with constants, then removes
- `removereplace`: Combined replace-then-remove approach

### Example
```bash
python3 -m main --source-file iter_1/Main.java --script iter_1/run.sh --mode remove
```

## Project Structure

### Core Scripts
- **`setup.sh`**: Initializes fresh test environment, copies source files
- **`cleanup.sh`**: Removes temporary files and resets workspace
- **`evaluator.py`**: Runs batch evaluation across multiple test cases
- **`comparator.py`**: Compares reduction results between different modes

## Reproducing Evaluation Results

### 1. Setup Test Cases
```bash
# Ensure test cases are in generator_modified/ or similar directory
# Each iter_X/ folder should contain Main.java and run.sh
```

### 2. Run Full Evaluation
```bash
python3 evaluator.py
```

### 3. Analyze Results
```bash
# Parse timing data
python3 extract_times.py <path_to_log_file>

# Compare modes
python3 comparator.py
```

### Output Structure
```
evaluation_results_YYYYMMDD_HHMMSS/
├── remove_mode_evaluation.log
├── replace_mode_evaluation.log  
├── removereplace_mode_evaluation.log
├── remove_mode_results/
├── replace_mode_results/
└── removereplace_mode_results/
```

## Evaluation Against Perses

The tool has been evaluated using 3 different test suites, with all 3 modes tested per suite:

- **JDK23 errors**: Compilation error test cases from JDK 23
- **JDK11 errors**: Compilation error test cases from JDK 11  
- **JDK8 crashes**: Compiler crash test cases from JDK 8

Comparative evaluation results against the Perses reducer can be found in the `perses-results/` folder.

## Results

[Tables and detailed results will be inserted here]
