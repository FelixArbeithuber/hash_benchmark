import hashlib
import os
import timeit
from enum import Enum
from typing import Tuple
import math

from eth_hash.auto import keccak  # Canonical Ethereum hash library

# --- CONFIGURATION ---

BLOCKS: int = 1024
BLOCK_SIZE: int = 32768 * 2 * 2 * 2 * 2 * 2
ITERATIONS: int = 50

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
    """Measure Throughput (MB/s) and Latency (ms)"""

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

    avg_latency_ms = (total_time / ITERATIONS) * 1000.0

    mb_processed = len(input_data) / 2**20
    throughput_mb_s = mb_processed / (total_time / ITERATIONS)

    return throughput_mb_s, avg_latency_ms


# --- MAIN EXECUTION ---


def main():
    print("Blockchain Hash Function Benchmark Results:\n")

    print()
    print("*" * 87)
    print("BLOCK_SIZE scaling")
    print("*" * 87)
    print()

    for block_size in range(4, int(math.log2(BLOCK_SIZE))):
        input_data: list[bytes] = [os.urandom(2**block_size) for i in range(0, BLOCKS)]

        print(
            f"Blocks: {BLOCKS} | Block Size: {2**block_size} | Data Size: {((2**block_size) * BLOCKS) / 1024 / 1024:.2f}MB | Iterations per Test: {ITERATIONS}\n"
        )
        print(
            f"{'ALGORITHM':<25} | {'THROUGHPUT (MB/s)':<20} | {'LATENCY (ms)':<20} | {'AVALANCHE (%)':<15}"
        )
        print("-" * 87)

        for algo in [HashAlgorithm.SHA256, HashAlgorithm.BLAKE2b, HashAlgorithm.SHA3, HashAlgorithm.Keccak256]:
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

            print(
                f"{algo.value:<25} | {mb_per_sec:>18.2f} | {latency_ms:>18.4f} | {avalanche_score:>13.2f}%"
            )

        print("-" * 87)


if __name__ == "__main__":
    main()
