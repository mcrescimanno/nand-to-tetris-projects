// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push temp 6
@TMP
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
(__END)
@__END
0;JMP
