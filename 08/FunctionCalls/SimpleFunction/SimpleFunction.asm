// function SimpleFunction.test 2
(SimpleFunction.test)
@2
D=A
(__FUNCTION_LOOP_0)
@__FUNCTION_PUSH_LOCAL_0
D;JNE
@__FUNCTION_CONT_0
0;JMP
(__FUNCTION_PUSH_LOCAL_0)
@SP
A=M
M=0
@SP
M=M+1
D=D-1
@__FUNCTION_LOOP_0
0;JMP
(__FUNCTION_CONT_0)
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
// push local 1
@LCL
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
// not
@SP
M=M-1
A=M
M=!M
@SP
M=M+1
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
// return
@LCL
D=M
@5
M=D
@5
D=D-A
A=D
D=M
@6
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@5
D=M
@1
D=D-A
A=D
D=M
@THAT
M=D
@5
D=M
@2
D=D-A
A=D
D=M
@THIS
M=D
@5
D=M
@3
D=D-A
A=D
D=M
@ARG
M=D
@5
D=M
@4
D=D-A
A=D
D=M
@LCL
M=D
@6
A=M
0;JMP
(__END)
@__END
0;JMP