// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
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
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 16
@16
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
@__EQ_TRUE_1
D;JEQ
D=0
@__EQ_CONT_1
0;JMP

(__EQ_TRUE_1)
	D=-1
	@__EQ_CONT_1
	0;JMP

(__EQ_CONT_1)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
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
@__EQ_TRUE_2
D;JEQ
D=0
@__EQ_CONT_2
0;JMP

(__EQ_TRUE_2)
	D=-1
	@__EQ_CONT_2
	0;JMP

(__EQ_CONT_2)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@__LT_TRUE_3
D;JLT
D=0
@__LT_CONT_3
0;JMP

(__LT_TRUE_3)
	D=-1
	@__LT_CONT_3
	0;JMP

(__LT_CONT_3)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@__LT_TRUE_4
D;JLT
D=0
@__LT_CONT_4
0;JMP

(__LT_TRUE_4)
	D=-1
	@__LT_CONT_4
	0;JMP

(__LT_CONT_4)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@__LT_TRUE_5
D;JLT
D=0
@__LT_CONT_5
0;JMP

(__LT_TRUE_5)
	D=-1
	@__LT_CONT_5
	0;JMP

(__LT_CONT_5)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
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
@__GT_TRUE_6
D;JGT
D=0
@__GT_CONT_6
0;JMP

(__GT_TRUE_6)
	D=-1
	@__GT_CONT_6
	0;JMP

(__GT_CONT_6)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32767
@32767
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
@__GT_TRUE_7
D;JGT
D=0
@__GT_CONT_7
0;JMP

(__GT_TRUE_7)
	D=-1
	@__GT_CONT_7
	0;JMP

(__GT_CONT_7)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
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
@__GT_TRUE_8
D;JGT
D=0
@__GT_CONT_8
0;JMP

(__GT_TRUE_8)
	D=-1
	@__GT_CONT_8
	0;JMP

(__GT_CONT_8)
	@SP
	A=M
	M=D
	@SP
	M=M+1
// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 53
@53
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
// push constant 112
@112
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
// neg
@SP
M=M-1
A=M
M=-M
@SP
M=M+1
// and
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D&M
@SP
M=M+1
// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=D|M
@SP
M=M+1
// not
@SP
M=M-1
A=M
M=!M
@SP
M=M+1
(__END)
@__END
0;JMP
