import gc
from memory_profiler_master.memory_profiler import profile

@profile
def measure_hash_footprints():
    import os
    input_data = os.urandom(8194 * 8194)

    import hashlib
    from eth_hash.auto import keccak

    sha256 = hashlib.sha256()
    sha256.update(input_data)
    _ = sha256.digest()

    blake2b = hashlib.blake2b()
    blake2b.update(input_data)
    _ = blake2b.digest()

    sha3_256 = hashlib.sha3_256()
    sha3_256.update(input_data)
    _ = sha3_256.digest()

    _ = keccak(input_data)
    _ = keccak(input_data)
    

if __name__ == "__main__":
    gc.disable()
    measure_hash_footprints()
