// push constant 10
@10
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop local 0
@LCL
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
// push constant 21
@21
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 22
@22
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop argument 2
@ARG
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
// pop argument 1
@ARG
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
// push constant 36
@36
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop this 6
@THIS
D=M
@SP
A=M
M=D
@6
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
// push constant 42
@42
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 45
@45
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop that 5
@THAT
D=M
@SP
A=M
M=D
@5
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
// push constant 510
@510
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop temp 6
@5
D=A
@SP
A=M
M=D
@6
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
// push local 0
@LCL
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
// push that 5
@THAT
D=M
@SP
A=M
M=D
@5
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
// push this 6
@THIS
D=M
@SP
A=M
M=D
@6
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
// push this 6
@THIS
D=M
@SP
A=M
M=D
@6
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
// push temp 6
@5
D=A
@SP
A=M
M=D
@6
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
(__END)
@__END
0;JMP