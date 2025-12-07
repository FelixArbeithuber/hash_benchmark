import gc
import hashlib

from eth_hash.auto import keccak
from memory_profiler import profile


@profile
def measure_hash_footprints():
    sha256_hash = hashlib.sha256(b"").digest()
    blake2b_hash = hashlib.blake2b(b"").digest()
    keccak_hash = keccak(b"")


if __name__ == "__main__":
    gc.disable()
    measure_hash_footprints()
    gc.enable()
