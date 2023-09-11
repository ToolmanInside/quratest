import shutil
import os

mutator = [
    "RandomMutator",
    "QFTMutator",
    "UCNOTMutator"
]

for q in range(4,8):
    qubits = str(q).zfill(2)
    if not os.path.exists("inputs_" + qubits):
        os.mkdir("inputs_" + qubits)
    first_folder = "inputs_" + qubits
    for idx in range(10):
        idxx = str(idx).zfill(2)
        sec_folder = "run_" + idxx
        for m in mutator:
            path = os.path.join("exp-01-" + qubits, sec_folder, m, "circuit")
            shutil.copy(path, os.path.join(first_folder, m + "_" + idxx))