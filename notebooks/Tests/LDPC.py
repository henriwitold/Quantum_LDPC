import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer

# H_X matrix from the paper
Hx = np.array([
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 1, 1, 0, 0, 1],
    [0, 0, 1, 1, 0, 0, 0, 1, 0, 1]
])

# H_Z matrix
Hz = np.array([
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0, 0, 0, 0, 1, 1],
    [0, 0, 1, 0, 1, 0, 1, 0, 0, 1]
])

def make_stabilizer_circ(Hx, Hz):
    n_data_qubits = Hx.shape[1]
    n_x_stabilizers = Hx.shape[0]
    n_z_stabilizers = Hz.shape[0]
    n_ancilla_qubits = n_x_stabilizers + n_z_stabilizers

    total_qubits = n_data_qubits + n_ancilla_qubits
    qc = QuantumCircuit(total_qubits, n_ancilla_qubits)

    x_ancilla_start = n_data_qubits
    z_ancilla_start = n_data_qubits + n_x_stabilizers

    # Initialize data qubits in |+⟩ state for testing X stabilizers
    qc.h(range(n_data_qubits))

    # X stabilizer measurements
    for i in range(n_x_stabilizers):
        ancilla = x_ancilla_start + i
        qc.h(ancilla)  # Prepare ancilla in |+⟩
        for j in range(n_data_qubits):
            if Hx[i, j]:
                qc.cx(ancilla, j)
        qc.h(ancilla)  # Measure ancilla in X basis
        qc.measure(ancilla, i)

    # Z stabilizer measurements
    for i in range(n_z_stabilizers):
        ancilla = z_ancilla_start + i
        # Ancilla qubits are initialized in |0⟩ by default
        for j in range(n_data_qubits):
            if Hz[i, j]:
                qc.cx(j, ancilla)
        qc.measure(ancilla, n_x_stabilizers + i)

    return qc

# Build the circuit
qc = make_stabilizer_circ(Hx, Hz)

# Use Aer simulator
backend = Aer.get_backend('qasm_simulator')

# Transpile the circuit for the simulator
transpiled_circuit = transpile(qc, backend)

# Run the circuit on the backend
job = backend.run(transpiled_circuit, shots=1024)
result = job.result()

# Get the counts (measurement results)
counts = result.get_counts()

# Print the counts
print("Measurement Results:")
for outcome, count in counts.items():
    print(f"{outcome}: {count}")

# Plot the histogram
plot_histogram(counts)
qc.draw('mpl')
