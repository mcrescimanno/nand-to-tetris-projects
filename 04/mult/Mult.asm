// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

@sum
M=0 // set sum = 0

@i
M=0 // Set i = 0

@R0
D=M
@product
M=D // Set product = R0

@R1
D=M
@n
M=D // Set n = R1

@R2
M=0 // Initialize the product to 0.

// if i >= n , then set sum to r2 and jump to end, else begin loop.
(CHECK)
	@i
	D=M
	@n
	D=D-M
	@RET
	D;JGE
	@LOOP
	D;JLT

(LOOP)
	@sum
	D=M
	@product
	D=D+M
	@sum
	M=D // sum += product

	@i
	M=M+1 // i += 1

	@CHECK
	0;JMP

(END)
	@END
	0;JMP

// r2 = sum, then end program
(RET)
	@sum
	D=M
	@R2
	M=D
	@END
	0;JMP



