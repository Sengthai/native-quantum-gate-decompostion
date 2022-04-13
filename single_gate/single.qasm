OPENQASM 2.0;
include "qelib1.inc";
qreg q0[7];
x q0[0];
y q0[1];
z q0[2];
h q0[3];
t q0[4];
cx q0[5], q0[6];