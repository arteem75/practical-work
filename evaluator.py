import subprocess
import shutil
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

base_dir = Path("/Users/artemancikov/Desktop/practical-work-new/reducer/jdk-bugs-modified")

num_iters = 20

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_dir = Path(f"jdk_evaluation_results_{timestamp}")
results_dir.mkdir(exist_ok=True)

print("Starting REMOVE MODE section")

setup_script = "setup.sh"
print(f"Running setup for remove mode: {setup_script}")
try:
    subprocess.run(["bash", str(setup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Setup script failed: {e}")
    exit(1)

remove_log_file = results_dir / "remove_mode_evaluation.log"

with open(remove_log_file, 'w') as remove_log:
    remove_log.write("=== REMOVE MODE EVALUATION LOG ===\n\n")
    
    for i in tqdm(range(1, num_iters + 1), desc="Running REMOVE mode commands"):
        iter_dir = base_dir / f"iter_{i}"
        main_java = iter_dir / "Main.java"
        run_sh = iter_dir / "run.sh"

        command = [
            "python3", "-m", "main",
            "--source-file", str(main_java),
            "--script", str(run_sh),
            "--mode", "remove"
        ]

        remove_log.write(f"\n{'='*50}\n")
        remove_log.write(f"ITERATION {i} - REMOVE MODE\n")
        remove_log.write(f"Source: {main_java}\n")
        remove_log.write(f"Script: {run_sh}\n")
        remove_log.write(f"{'='*50}\n\n")
        remove_log.flush()

        try:
            subprocess.run(command, check=True, stdout=remove_log, stderr=subprocess.STDOUT)
            print(f"iter_{i} (remove) completed")
        except subprocess.CalledProcessError as e:
            print(f"\nError occurred in iter_{i} (remove): {e}")
            remove_log.write(f"\nERROR: {e}\n")
            remove_log.flush()

print("Saving REMOVE mode results...")
remove_results_dir = results_dir / "remove_mode_results"
shutil.copytree(base_dir, remove_results_dir)
print(f"Remove mode results saved to: {remove_results_dir}")

cleanup_script = "cleanup.sh"
print(f"Running cleanup after remove mode: {cleanup_script}")
try:
    subprocess.run(["bash", str(cleanup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Cleanup script failed: {e}")

print("REMOVE MODE section completed\n")

# ===== REPLACE MODE SECTION =====
print("Starting REPLACE MODE section")

setup_script = "setup.sh"
print(f"Running setup for replace mode: {setup_script}")
try:
    subprocess.run(["bash", str(setup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Setup script failed: {e}")
    exit(1)

replace_log_file = results_dir / "replace_mode_evaluation.log"

with open(replace_log_file, 'w') as replace_log:
    replace_log.write("=== REPLACE MODE EVALUATION LOG ===\n\n")
    
    for i in tqdm(range(1, num_iters + 1), desc="Running REPLACE mode commands"):
        iter_dir = base_dir / f"iter_{i}"
        main_java = iter_dir / "Main.java"
        run_sh = iter_dir / "run.sh"

        command = [
            "python3", "-m", "main",
            "--source-file", str(main_java),
            "--script", str(run_sh),
            "--mode", "replace"
        ]

        replace_log.write(f"\n{'='*50}\n")
        replace_log.write(f"ITERATION {i} - REPLACE MODE\n")
        replace_log.write(f"Source: {main_java}\n")
        replace_log.write(f"Script: {run_sh}\n")
        replace_log.write(f"{'='*50}\n\n")
        replace_log.flush()

        try:
            subprocess.run(command, check=True, stdout=replace_log, stderr=subprocess.STDOUT)
            print(f"iter_{i} (replace) completed")
        except subprocess.CalledProcessError as e:
            print(f"\nError occurred in iter_{i} (replace): {e}")
            replace_log.write(f"\nERROR: {e}\n")
            replace_log.flush()

print("Saving REPLACE mode results...")
replace_results_dir = results_dir / "replace_mode_results"
shutil.copytree(base_dir, replace_results_dir)
print(f"Replace mode results saved to: {replace_results_dir}")

cleanup_script = "cleanup.sh"
print(f"Running cleanup after replace mode: {cleanup_script}")
try:
    subprocess.run(["bash", str(cleanup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Cleanup script failed: {e}")

print("REPLACE MODE section completed\n")

# ===== REMOVEREPLACE MODE SECTION =====
print("Starting REMOVEREPLACE MODE section")

setup_script = "setup.sh"
print(f"Running setup for removereplace mode: {setup_script}")
try:
    subprocess.run(["bash", str(setup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Setup script failed: {e}")
    exit(1)

removereplace_log_file = results_dir / "removereplace_mode_evaluation.log"

with open(removereplace_log_file, 'w') as removereplace_log:
    removereplace_log.write("=== REMOVEREPLACE MODE EVALUATION LOG ===\n\n")
    
    for i in tqdm(range(1, num_iters + 1), desc="Running REMOVEREPLACE mode commands"):
        iter_dir = base_dir / f"iter_{i}"
        main_java = iter_dir / "Main.java"
        run_sh = iter_dir / "run.sh"

        command = [
            "python3", "-m", "main",
            "--source-file", str(main_java),
            "--script", str(run_sh),
            "--mode", "removereplace"
        ]

        removereplace_log.write(f"\n{'='*50}\n")
        removereplace_log.write(f"ITERATION {i} - REMOVEREPLACE MODE\n")
        removereplace_log.write(f"Source: {main_java}\n")
        removereplace_log.write(f"Script: {run_sh}\n")
        removereplace_log.write(f"{'='*50}\n\n")
        removereplace_log.flush()

        try:
            subprocess.run(command, check=True, stdout=removereplace_log, stderr=subprocess.STDOUT)
            print(f"iter_{i} (removereplace) completed")
        except subprocess.CalledProcessError as e:
            print(f"\nError occurred in iter_{i} (removereplace): {e}")
            removereplace_log.write(f"\nERROR: {e}\n")
            removereplace_log.flush()

print("Saving REMOVEREPLACE mode results...")
removereplace_results_dir = results_dir / "removereplace_mode_results"
shutil.copytree(base_dir, removereplace_results_dir)
print(f"Removereplace mode results saved to: {removereplace_results_dir}")

cleanup_script = "cleanup.sh"
print(f"Running cleanup after removereplace mode: {cleanup_script}")
try:
    subprocess.run(["bash", str(cleanup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Cleanup script failed: {e}")

print("REMOVEREPLACE MODE section completed\n")

# Final cleanup
cleanup_script = "cleanup.sh"
print(f"Running final cleanup: {cleanup_script}")
try:
    subprocess.run(["bash", str(cleanup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"Final cleanup script failed: {e}")

print("All evaluations finished!")
print(f"All results saved in: {results_dir}")
print(f"Remove mode log: {remove_log_file}")
print(f"Replace mode log: {replace_log_file}")
print(f"Removereplace mode log: {removereplace_log_file}")
print(f"Remove mode results: {remove_results_dir}")
print(f"Replace mode results: {replace_results_dir}")
print(f"Removereplace mode results: {removereplace_results_dir}")



