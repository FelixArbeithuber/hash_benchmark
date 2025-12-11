import gc
import tracemalloc
import os

input_data = os.urandom(8194 * 8194)


tracemalloc.start()

# --- START ---
snapshot1 = tracemalloc.take_snapshot()

import hashlib
from eth_hash.auto import keccak
from memory_profiler import profile

snapshot2 = tracemalloc.take_snapshot()

sha256 = hashlib.sha256()
sha256.update(input_data)
_ = sha256.digest()

snapshot3 = tracemalloc.take_snapshot()

blake2b = hashlib.blake2b()
blake2b.update(input_data)
_ = blake2b.digest()

snapshot4 = tracemalloc.take_snapshot()

sha3_256 = hashlib.sha3_256()
sha3_256.update(input_data)
_ = sha3_256.digest()

snapshot5 = tracemalloc.take_snapshot()
_ = keccak(input_data)
snapshot6 = tracemalloc.take_snapshot()

_ = keccak(input_data)

# --- END ---
tracemalloc.stop()

def compare(snap1, snap2):
    for stat in snap2.compare_to(snap1, 'lineno'):
        if stat.size_diff > 0:
            print(stat)
    
compare(snapshot5, snapshot6)
