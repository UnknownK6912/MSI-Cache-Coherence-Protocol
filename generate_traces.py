import random

# System config (default values, will be prompted to change if desired later)
num_cores   = 4   # N: number of processor cores
cache_lines = 8   # C: cache lines per cache
mem_size    = 64  # M: total memory addresses

# Ask user which type of trace he/she wants
print("Which trace do you want to generate?")
print("  A - Read-Dominated Private Access")
print("  B - Producer-Consumer")
print("  C - Migratory Sharing")

try:
    trace_choice = input("Enter trace (A / B / C): ").strip().upper()
    assert trace_choice in ["A", "B", "C"], "Choice must be A, B, or C"
except AssertionError as e:
    print(f"Error: {e}")
    exit(1)

try:
    num_rounds = int(input("How many rounds do you want to generate?: "))
    assert num_rounds > 0, "Number of rounds must be positive"
except ValueError:
    print("Error: Input must be a valid number")
    exit(1)
except AssertionError as e:
    print(f"Error: {e}")
    exit(1)

try:
    num_cores = int(input(f"Number of cores (N) [default {num_cores}]: ").strip() or num_cores)
    assert num_cores > 0, "Number of cores must be positive"
except ValueError:
    print("Error: Input must be a valid number")
    exit(1)
except AssertionError as e:
    print(f"Error: {e}")
    exit(1)

try:
    cache_lines = int(input(f"Cache lines per cache (C) [default {cache_lines}]: ").strip() or cache_lines)
    assert cache_lines > 0, "Cache lines must be positive"
except ValueError:
    print("Error: Input must be a valid number")
    exit(1)
except AssertionError as e:
    print(f"Error: {e}")
    exit(1)

try:
    mem_size = int(input(f"Memory size in addresses (M) [default {mem_size}]: ").strip() or mem_size)
    assert mem_size > 0, "Memory size must be positive"
except ValueError:
    print("Error: Input must be a valid number")
    exit(1)
except AssertionError as e:
    print(f"Error: {e}")
    exit(1)

output_file = open(f"trace_{trace_choice.lower()}.txt", "w")  # one file per trace


# Trace A
def gen_trace_a():
    stride     = mem_size // num_cores
    slice_size = min(cache_lines // 2, stride)  # stay well inside cache capacity

    for _ in range(num_rounds):
        for core in range(num_cores):
            base = core * stride
            for offset in range(slice_size):
                addr = base + offset
                output_file.write(f"{core},R,{addr}\n")


# Trace B
def gen_trace_b():
    num_shared = cache_lines // 2  # small enough to fit in every cache at once

    for _ in range(num_rounds):
        for addr in range(num_shared):           # producer writes
            output_file.write(f"0,W,{addr}\n")
        for core in range(1, num_cores):         # consumers read
            for addr in range(num_shared):
                output_file.write(f"{core},R,{addr}\n")


# Trace C
def gen_trace_c():
    for _ in range(num_rounds):
        for core in range(num_cores):
            output_file.write(f"{core},W,0\n")


if trace_choice == "A":
    gen_trace_a()
elif trace_choice == "B":
    gen_trace_b()
elif trace_choice == "C":
    gen_trace_c()

output_file.close()
print(f"Trace {trace_choice} written to trace_{trace_choice.lower()}.txt")