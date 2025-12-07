import gc
import hashlib
import os

from eth_hash.auto import keccak
from memory_profiler import profile

input_data = os.urandom(8192 * 8192)

@profile
def measure_hash_footprints():
    sha256 = hashlib.sha256()
    sha256.update(input_data)
    _ = sha256.digest()
    
    blake2b = hashlib.blake2b()
    blake2b.update(input_data)
    _ = blake2b.digest()

    _ = keccak(input_data)


if __name__ == "__main__":
    gc.disable()
    measure_hash_footprints()
