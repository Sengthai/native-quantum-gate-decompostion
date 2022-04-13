import os
import csv
from math import pi, ceil
from re import M
from sympy import EvaluationFailed
from tqdm import tqdm
import numpy as np
from multiprocessing import Pool, cpu_count
import time

from qiskit import QuantumCircuit, transpile
os.system('cls' if os.name == 'nt' else 'clear')

DEBUG =1

# dir_name = "benchmarks"
dir_name = "single_gate"
dir_name = "multi_qubit_gate"

ref_dir_path = "./" + dir_name

def writeEval(rows):
    with open(dir_name+'_eval.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        header = ['cir','qubit', 'origin_gate', 'ibm_gate', 
                    'ionq_gate','riggit_gate','google_gate',
                    'ori_depth','ibm_depth', 'ionq_depth',
                     'riggit_depth','google_depth'] 
        writer.writerow(header)
        for row in tqdm(rows):
            writer.writerow(row)



# for qasm in tqdm(os.listdir(ref_dir_path)):

def evaluate_file(qasm):
    # # preven .DS_store or files that auto generated by OS
    # if qasm.startswith('.'):
    #     continue
    
    qasm_path = os.path.join(ref_dir_path, qasm)
    name = qasm.replace(".qasm", "")

    qc = QuantumCircuit.from_qasm_file(qasm_path)

    num_of_machine = 4

    ibm_basis       = ['sx', 'rz', 'rzx'] # rzx is cross-resonance gate
    rigetti_basis   = ['sx', 'rz', 'cz']
    ion_basis       = ['r',  'rz', 'rxx'] # rxx is xx(x) gates
    google_basis    = ['r',  'rz', 'cz', 'iswap']

    machines = {"ibm": ibm_basis, 
                "ion": ion_basis,
                "rigetti": rigetti_basis, 
                "google": google_basis}

    iter = 1

    m_size = np.zeros(num_of_machine)
    m_depth = np.zeros(num_of_machine)

    if DEBUG == 1:
        print("Original circuit")
        print(qc)

    for i in range(iter):
        depths, sizes = [], []
        for m,basis in machines.items():
            
            temp_qc = transpile(qc, basis_gates=basis, optimization_level=0)
            # if m == 'rigetti' or m == 'google':
            #     continue
            #     print("Machine: " , m)
            #     print(temp_qc)
            if DEBUG == 1:
                print("Machine: " , m , " -- Gate: " , temp_qc.size())
                print(temp_qc)
            depths.append(temp_qc.depth())
            sizes.append(temp_qc.size())
        m_size += np.array(sizes)
        m_depth += np.array(depths)
        
    
    # get average from  iteration
    m_size /= iter
    m_depth /= iter

    print("-- ", name , ": ", qc.size(), " gates")

    # Append name, number of qubits, original size, [each of machines native gate], 
    # original circuit depth, [each of machines circuit depth]
    return [name, qc.num_qubits, qc.size()]+ m_size.tolist() + [qc.depth()] + m_depth.tolist()

if __name__ == "__main__":
    start_time = time.time()

    rows = []
    paths_list = [ p for p in os.listdir(ref_dir_path) if not p.startswith('.')]

    if DEBUG==1:
        for i in paths_list:
            evaluate_file(i)
            break;
    else:
        print("CPUs work with : ", cpu_count() - 1)
        pool = Pool(processes=cpu_count() - 1)
        rows = pool.map(evaluate_file, paths_list, chunksize=1)
        pool.close()
        writeEval(rows)
    print("DONE with --- %s seconds ---" % (time.time() - start_time))



