import subprocess
from pathlib import Path
from tqdm import tqdm

# Base directory
base_dir = Path("/Users/artemancikov/Desktop/practical-work-new/reducer/generator_modified")

# Number of iterations
num_iters = 10

# Run setup.sh
setup_script = "setup.sh"
print(f"🔧 Running setup: {setup_script}")
try:
    subprocess.run(["bash", str(setup_script)], check=True)
except subprocess.CalledProcessError as e:
    print(f"❌ Setup script failed: {e}")
    exit(1)

# Loop with progress bar
for i in tqdm(range(1, num_iters + 1), desc="Running commands"):
    iter_dir = base_dir / f"iter_{i}"
    main_java = iter_dir / "Main.java"
    run_sh = iter_dir / "run.sh"

    command = [
        "python3", "-m", "main",
        "--source-file", str(main_java),
        "--script", str(run_sh)
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error occurred in iter_{i}: {e}")
    # Run cleanup.sh
    cleanup_script = "cleanup.sh"
    print(f"🧹 Running cleanup: {cleanup_script}")
    try:
        subprocess.run(["bash", str(cleanup_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Cleanup script failed: {e}")
cleanup_script = "cleanup.sh"
print(f"🧹 Running cleanup: {cleanup_script}")
try:
    subprocess.run(["bash", str(cleanup_script)], check=True)
except subprocess.CalledProcessError as e:
        print(f"❌ Cleanup script failed: {e}")



