// HACK bootstrap
@256
D=A
@SP
M=D
@Sys.init$ret.0
D=A
@SP
A=M
M=D
@LCL
D=M
@SP
M=M+1
A=M
M=D
@ARG
D=M
@SP
M=M+1
A=M
M=D
@THIS
D=M
@SP
M=M+1
A=M
M=D
@THAT
D=M
@SP
M=M+1
A=M
M=D
@SP
M=M+1
@5
D=A
@0
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(Sys.init$ret.0)
// push argument 1
@ARG
D=M
@SP
A=M
M=D
@1
D=A
@SP
A=M
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// pop pointer 1
@1
D=A
@__COND_THIS_1
D;JEQ
@__COND_THAT_1
0;JMP
(__COND_THIS_1)
	@SP
	M=M-1
	A=M
	D=M
	@THIS
	M=D
	@__PTR_CONT_1
	0;JMP
(__COND_THAT_1)
	@SP
	M=M-1
	A=M
	D=M
	@THAT
	M=D
	@__PTR_CONT_1
	0;JMP
(__PTR_CONT_1)
0
// push constant 0
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 0
@THAT
D=M
@SP
A=M
M=D
@0
D=A
@SP
A=M
M=M+D
@SP
M=M-1
A=M
D=M
@SP
M=M+1
A=M
A=M
M=D
@SP
M=M-1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 1
@THAT
D=M
@SP
A=M
M=D
@1
D=A
@SP
A=M
M=M+D
@SP
M=M-1
A=M
D=M
@SP
M=M+1
A=M
A=M
M=D
@SP
M=M-1
// push argument 0
@ARG
D=M
@SP
A=M
M=D
@0
D=A
@SP
A=M
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 2
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
// pop argument 0
@ARG
D=M
@SP
A=M
M=D
@0
D=A
@SP
A=M
M=M+D
@SP
M=M-1
A=M
D=M
@SP
M=M+1
A=M
A=M
M=D
@SP
M=M-1
// label MAIN_LOOP_START
(MAIN_LOOP_START)
// push argument 0
@ARG
D=M
@SP
A=M
M=D
@0
D=A
@SP
A=M
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// if-goto COMPUTE_ELEMENT
@SP
M=M-1
A=M
D=M
@__BRANCH_TRUE_2
D;JNE
@__BRANCH_FALSE_2
0;JMP
(__BRANCH_TRUE_2)
	@COMPUTE_ELEMENT
	0;JMP
(__BRANCH_FALSE_2)
0
// goto END_PROGRAM
@END_PROGRAM
0;JMP
// label COMPUTE_ELEMENT
(COMPUTE_ELEMENT)
// push that 0
@THAT
D=M
@SP
A=M
M=D
@0
D=A
@SP
A=M
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push that 1
@THAT
D=M
@SP
A=M
M=D
@1
D=A
@SP
A=M
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
// pop that 2
@THAT
D=M
@SP
A=M
M=D
@2
D=A
@SP
A=M
M=M+D
@SP
M=M-1
A=M
D=M
@SP
M=M+1
A=M
A=M
M=D
@SP
M=M-1
// push pointer 1
@1
D=A
@__COND_THIS_3
D;JEQ
@__COND_THAT_3
0;JMP
(__COND_THIS_3)
	@THIS
	D=M
	@__PTR_CONT_3
	0;JMP
(__COND_THAT_3)
	@THAT
	D=M
	@__PTR_CONT_3
	0;JMP
(__PTR_CONT_3)
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
// pop pointer 1
@1
D=A
@__COND_THIS_4
D;JEQ
@__COND_THAT_4
0;JMP
(__COND_THIS_4)
	@SP
	M=M-1
	A=M
	D=M
	@THIS
	M=D
	@__PTR_CONT_4
	0;JMP
(__COND_THAT_4)
	@SP
	M=M-1
	A=M
	D=M
	@THAT
	M=D
	@__PTR_CONT_4
	0;JMP
(__PTR_CONT_4)
0
// push argument 0
@ARG
D=M
@SP
A=M
M=D
@0
D=A
@SP
A=M
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// push constant 1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
// pop argument 0
@ARG
D=M
@SP
A=M
M=D
@0
D=A
@SP
A=M
M=M+D
@SP
M=M-1
A=M
D=M
@SP
M=M+1
A=M
A=M
M=D
@SP
M=M-1
// goto MAIN_LOOP_START
@MAIN_LOOP_START
0;JMP
// label END_PROGRAM
(END_PROGRAM)
