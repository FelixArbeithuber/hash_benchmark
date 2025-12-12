import hashlib
import os
import timeit
from enum import Enum
from typing import Literal, Tuple, Dict, List
import math

import matplotlib.pyplot as plt
from eth_hash.auto import keccak

# --- CONFIGURATION ---

BLOCKS: int = 32
BLOCK_SIZE: int = 2**22
ITERATIONS: int = 32

# --- HELPER FUNCTIONS ---


class HashAlgorithm(Enum):
    SHA256 = "SHA-256"
    BLAKE2b = "BLAKE2b"
    SHA3 = "SHA3-256"
    Keccak256 = "Keccak-256"


def bit_diff(a: bytes, b: bytes) -> int:
    """number of differing bits between two arrays of bytes"""

    diff = 0
    for x, y in zip(a, b):
        diff += bin(x ^ y).count("1")

    return diff


def measure_avalanche_effect(algo_name: HashAlgorithm, input_data: bytes) -> float:
    """Measures the % change in the hash output when a single bit is flipped in the input"""

    # flip the least significant bit of the last byte
    modified_data = bytearray(input_data)
    modified_data[-1] ^= 1
    modified_data = bytes(modified_data)

    if algo_name == HashAlgorithm.SHA256:
        h1 = hashlib.sha256(input_data).digest()
        h2 = hashlib.sha256(modified_data).digest()
    elif algo_name == HashAlgorithm.BLAKE2b:
        h1 = hashlib.blake2b(input_data).digest()
        h2 = hashlib.blake2b(modified_data).digest()
    elif algo_name == HashAlgorithm.SHA3:
        h1 = hashlib.sha3_256(input_data).digest()
        h2 = hashlib.sha3_256(modified_data).digest()
    elif algo_name == HashAlgorithm.Keccak256:
        h1 = keccak(input_data)
        h2 = keccak(modified_data)

    total_bits = len(h1) * 8
    return (bit_diff(h1, h2) / total_bits) * 100.0


def measure_latency_and_throughput(
    algo_name: HashAlgorithm, input_data: bytes
) -> Tuple[float, float]:
    """Measure Throughput (MiB/s) and Latency (ms)"""

    # Define task for timeit
    def run_sha256():
        hashlib.sha256(input_data).digest()

    def run_blake2b():
        hashlib.blake2b(input_data).digest()

    def run_sha3():
        hashlib.sha3_256(input_data).digest()

    def run_keccak():
        keccak(input_data)

    if algo_name == HashAlgorithm.SHA256:
        total_time = timeit.timeit(run_sha256, number=ITERATIONS)
    elif algo_name == HashAlgorithm.BLAKE2b:
        total_time = timeit.timeit(run_blake2b, number=ITERATIONS)
    if algo_name == HashAlgorithm.SHA3:
        total_time = timeit.timeit(run_sha3, number=ITERATIONS)
    elif algo_name == HashAlgorithm.Keccak256:
        total_time = timeit.timeit(run_keccak, number=ITERATIONS)

    # total time is in seconds
    # -> divide by ITERATIONS and 1000 to get avg time in milliseconds
    avg_latency_ms = (total_time / ITERATIONS) * 1000.0

    mb_processed = len(input_data) / 2**20
    throughput_mb_s = mb_processed / (total_time / ITERATIONS)

    return throughput_mb_s, avg_latency_ms

def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size >= power:
        size /= power
        n += 1
    return str(size) + (power_labels[n] + 'B')

# --- MAIN EXECUTION ---

def main():
    print("Blockchain Hash Function Benchmark Results:\n")

    print("*" * 70)
    print("BLOCK_SIZE scaling")
    print("*" * 70)

    results: Dict[HashAlgorithm, Dict[Literal['sizes', 'throughput', 'latency'], List[float]]] = {
        algo: {'sizes': [], 'throughput': [], 'latency': []} 
        for algo in HashAlgorithm
    }
    for block_size in range(4, int(math.log2(BLOCK_SIZE))):
        input_data: list[bytes] = [os.urandom(2**block_size) for i in range(0, BLOCKS)]

        print(
            f"\nBlocks: {BLOCKS} | Block Size: {format_bytes(2**block_size)} | Iterations per Test: {ITERATIONS}"
        )
        print(
            f"{'ALGORITHM':<16} | {'THROUGHPUT (MiB/s)':>18} | {'LATENCY (ms)':>12} | {'AVALANCHE (%)':>13}"
        )
        print("-" * 70)

        for algo in HashAlgorithm:
            mb_per_sec = 0
            latency_ms = 0
            avalanche_score = 0
            for block in input_data:
                throughput, latency = measure_latency_and_throughput(algo, block)
                mb_per_sec += throughput
                latency_ms += latency
                avalanche_score += measure_avalanche_effect(algo, block)
            mb_per_sec /= len(input_data)
            latency_ms /= len(input_data)
            avalanche_score /= len(input_data)

            results[algo]['sizes'].append(2**block_size / 1024)
            results[algo]['throughput'].append(mb_per_sec)
            results[algo]['latency'].append(latency_ms)

            print(
                f"{algo.value:<16} | {mb_per_sec:>18.2f} | {latency_ms:>12.5f} | {avalanche_score:>13.2f}%"
            )

        print("-" * 70)

    # --- PLOTTING ---
        
    # Setup the subplots (2 rows, 1 column)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    # 1. Throughput vs Block Size
    for algo in HashAlgorithm:
        ax1.plot(
            results[algo]['sizes'], 
            results[algo]['throughput'], 
            marker='o', 
            label=algo.name
        )
    
    ax1.set_title('Hashing Throughput vs Block Size')
    ax1.set_xlabel('Block Size (Kibibytes)')
    ax1.set_ylabel('Throughput (MiB/s)')
    ax1.set_xscale('log', base=2)
    ax1.grid(True, which="both", ls="-", alpha=0.5)
    ax1.legend()

    # 2. Latency vs Block Size
    for algo in HashAlgorithm:
        ax2.plot(
            results[algo]['sizes'], 
            results[algo]['latency'], 
            marker='x', 
            label=algo.value
        )
    
    ax2.set_title('Hashing Latency vs Block Size')
    ax2.set_xlabel('Block Size (Kibibytes)')
    ax2.set_ylabel('Latency (ms)')
    ax2.set_xscale('log', base=2)
    ax2.set_yscale('log', base=2)
    ax2.grid(True, which="both", ls="-", alpha=0.5)
    ax2.legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
