import argparse

parser = argparse.ArgumentParser(description="Quantum Test Case Generator")

parser.add_argument("-n", type=int, default=5, help="number of qubits")
parser.add_argument("-g", type=str, default='random', help='quantum test case generator')

args = parser.parse_args()

print(args)