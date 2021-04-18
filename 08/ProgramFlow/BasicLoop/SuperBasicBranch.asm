// label LABEL
(LABEL)
// push constant 34
@34
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@__EQ_TRUE_0
D;JEQ
D=0
@__EQ_CONT_0
0;JMP

(__EQ_TRUE_0)
	D=-1
	@__EQ_CONT_0
	0;JMP

(__EQ_CONT_0)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// if-goto LABEL
@SP
M=M-1
A=M
D=M
@__BRANCH_TRUE_1
D;JLT
@__BRANCH_FALSE_1
0;JMP
(__BRANCH_TRUE_1)
	@LABEL
	0;JMP
(__BRANCH_FALSE_1)
0
(__END)
@__END
0;JMP
