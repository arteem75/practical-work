from pathlib import Path

# Base paths for the three versions
src_base = Path("/Users/artemancikov/Desktop/practical-work-new/reducer/generator_source")
function_only_base = Path("/Users/artemancikov/Desktop/practical-work-new/reducer/generator_modified_onepass")
newest_base = Path("/Users/artemancikov/Desktop/practical-work-new/reducer/generator_modified")

num_iters = 10

# Header (note the numeric width specifiers)
print(f"{'Iter':<7} {'Lines (src → one_pass → new)':<50} {'Symbols (src → one_pass → new)':<50}")

for i in range(1, num_iters + 1):
    iter_label = f"iter_{i}"
    src_file    = src_base           / iter_label / "Main.java"
    fn_file     = function_only_base / iter_label / "Main.java"
    new_file    = newest_base        / iter_label / "Main.java"

    try:
        # Read all three
        with open(src_file, "r") as f: lines_src = f.readlines()
        with open(fn_file,  "r") as f: lines_fn  = f.readlines()
        with open(new_file, "r") as f: lines_new = f.readlines()

        # Line counts
        lc_src = len(lines_src)
        lc_fn  = len(lines_fn)
        lc_new = len(lines_new)
        # Char counts
        cc_src = sum(len(l) for l in lines_src)
        cc_fn  = sum(len(l) for l in lines_fn)
        cc_new = sum(len(l) for l in lines_new)

        print(
            f"{iter_label:<15}  "
            f"{lc_src} → {lc_fn} → {lc_new:<30}  "
            f"{cc_src} → {cc_fn} → {cc_new}"
        )

    except FileNotFoundError as e:
        print(f"{iter_label:<7}  ❌ File not found: {e.filename}")
