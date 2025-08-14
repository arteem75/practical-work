# Java Program Reducer

A tool for automatically reducing Java programs while preserving specific compilation errors or properties. Uses delta debugging and AST manipulation to find minimal failing test cases.

## Overview

This project implements a program reduction tool that can:
- **Remove** declarations (classes, methods, fields, variables)
- **Replace** code elements with constants/null values
- **Break inheritance** relationships
- Preserve compilation errors for debugging

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

### Key Components
- `main.py`: Entry point and orchestration
- `reducer/modifications.py`: AST manipulation and code transformation
- `reducer/dd.py`: Delta debugging implementation
- `reducer/graph.py`: Dependency graph construction

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

This will:
- Execute all three modes (remove, replace, removereplace)
- Save results to timestamped directories
- Generate comprehensive logs
- Preserve intermediate states

### 3. Analyze Results
```bash
# Parse timing data
python3 extract_times.py

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

## Requirements
- Python 3.7+
- Java compiler (javac)
- tree-sitter library
- Dependencies: `pip install -r requirements.txt`