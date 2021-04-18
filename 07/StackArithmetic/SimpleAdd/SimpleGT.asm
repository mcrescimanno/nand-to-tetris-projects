// push constant 8
@8
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 7
@7
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@__GT_TRUE_0
D;JGT
D=0
@__GT_CONT_0
0;JMP

(__GT_TRUE_0)
	D=-1
	@__GT_CONT_0
	0;JMP

(__GT_CONT_0)
	@SP
	A=M
	M=D
	@SP
	M=M+1
