from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import execute
from qiskit import BasicAer

import operator


def get_test_op(qreg,c,ancilla_reg):
    '''
        |000> -> 1/sqrt(2)(|100> + |011>)
    '''
    circuit = QuantumCircuit(qreg,c)
    circuit.h(qreg[0])
    circuit.cx(qreg[0],qreg[1])
    circuit.cx(qreg[1],qreg[2])
    circuit.x(qreg[0])
    circuit.measure(qreg[ancilla_reg],c[ancilla_reg])

    return circuit


def get_test_recovery(qreg,c):
    '''
    |011> -> |000>
    '''
    circuit = QuantumCircuit(qreg,c)
    circuit.x(qreg[1])
    circuit.x(qreg[2])
    circuit.barrier()
    return circuit

def exec_iteration(backend, circuit, ancilla_index):
    '''
    executes one iteration of the RUS circuit
    '''
    #circuit.draw(output='mpl').show()

    job = execute(circuit, backend)
    result = job.result()
    counts = result.get_counts(circuit)

    # determine ancilla measurement result
    ancilla_measurement = 0
    for (key,value) in counts.items():
        ancilla_measurement = int(key[ancilla_index])

    # get statevector from Backend to initialize next round in case of bad measurement
    statevector = result.get_statevector(circuit)

    return ancilla_measurement,statevector


def RUS_test():

    #initialize backend
    backend_sv = BasicAer.get_backend('statevector_simulator')

    #initialize registers
    q = QuantumRegister(3, 'q')
    c = ClassicalRegister(3, 'c')

    #index of the ancilla qubit
    ancilla_index = 1

    circuit = QuantumCircuit(q, c)

    #initialize first iteration
    circuit = circuit.compose(get_test_op(q,c,ancilla_index))

    ancilla_measurement, statevector = exec_iteration(backend_sv,circuit,ancilla_index)

    cnt = 1  # count how many iterations were needed

    while (ancilla_measurement == 1):

        cnt+=1

        circuit = QuantumCircuit(q,c)

        # use statevector to artificially continue the circuit after measurement
        circuit.initialize(statevector,q)

        circuit = circuit.compose(get_test_recovery(q,c)) # apply recovery circuit
        circuit = circuit.compose(get_test_op(q,c,ancilla_index)) # apply probabilistiy circuit again

        ancilla_measurement,statevector = exec_iteration(backend_sv,circuit,ancilla_index)

    return cnt

if __name__ == "__main__":
    q = QuantumRegister(3, 'q')
    c = ClassicalRegister(3, 'c')

    ancilla_index = 1

    get_test_op(q,c,ancilla_index).draw(output='mpl').show()
    get_test_recovery(q,c).draw(output='mpl').show()

    cnt_hist = {}
    repititions = 100
    print(f"Repititions: {repititions}")
    for i in range(repititions):
        cnt = RUS_test()

        if cnt not in cnt_hist:
            cnt_hist[cnt] = 1
        else:
            cnt_hist[cnt]+=1

    for key,val in sorted(cnt_hist.items()):
        print(f"Number of Iterations: {key}, \t#: {val}")