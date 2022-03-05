from qiskit import *

def get_test_op(qreg,c,circuit,ancilla_reg,conditional):
    '''
        |000> -> 1/sqrt(2)(|100> + |011>)
    '''
    if not conditional:  # for first iteration
        circuit.h(qreg[0])
        circuit.cx(qreg[0],qreg[1])
        circuit.cx(qreg[1],qreg[2])
        circuit.x(qreg[0])
    else:   # for following iterations
        circuit.h(qreg[0]).c_if(c,2)   # 2 <= 010 in binary
        circuit.cx(qreg[0], qreg[1]).c_if(c,2)
        circuit.cx(qreg[1], qreg[2]).c_if(c,2)
        circuit.x(qreg[0]).c_if(c,2)

    circuit.measure(qreg[ancilla_reg], c[ancilla_reg])
    return circuit


def get_test_recovery(qreg,c,circuit,ancilla_reg):
    '''
    |011> -> |000>
    '''
    circuit.x(qreg[1]).c_if(c,2)
    circuit.x(qreg[2]).c_if(c,2)
    return circuit


qr = QuantumRegister(3)
cr = ClassicalRegister(3)

ancilla_reg = 1

circuit = QuantumCircuit(qr,cr)

# apply first iteration
circuit = get_test_op(qr,cr,circuit,ancilla_reg,False)


for i in range(4): # add the recovery+prob circuit multiple times conditionally
    circuit.barrier()
    circuit = get_test_recovery(qr,cr,circuit,ancilla_reg)
    circuit = get_test_op(qr,cr,circuit,ancilla_reg,True)


circuit.draw(output='mpl').show()

simulator = Aer.get_backend('qasm_simulator')
result = execute(circuit, backend=simulator, shots=100).result()
print(result.get_counts())
