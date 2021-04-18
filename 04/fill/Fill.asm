// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

@KBD
D=A
@finalScreenAddress
M=D-1 // finalScreenAddress = KBD - 1

(START)
	@KBD
	D=M

	@FILL
	D;JNE
	@UNFILL
	D;JEQ


(FILL)
	// Initialize Loop Vars
	@SCREEN
	D=A
	@nextScreenAddress
	M=D // set nextScreenAddress = 16384

	(FLOOP)
		@nextScreenAddress
		A=M // set address to be nextScreenAddress

		M=-1 // Flip all pixel bits

		D=A+1

		@nextScreenAddress
		M=D // nextScreenAddress += 1
		@CHECKFLOOP
		0;JMP


	@START
	0;JMP


(CHECKFLOOP)
	@nextScreenAddress
	D=M
	@finalScreenAddress
	D=D-M
	@FLOOP
	D;JLE
	@START
	0;JMP


(UNFILL)
	// Initialize Loop Vars
	@SCREEN
	D=A
	@nextScreenAddress
	M=D // set nextScreenAddress = 16384

	(ULOOP)
		@nextScreenAddress
		A=M

		M = 0

		D = A+1

		@nextScreenAddress
		M=D
		@CHECKULOOP
		0;JMP

	@START
	0;JMP


(CHECKULOOP)
	@nextScreenAddress
	D=M
	@finalScreenAddress
	D=D-M
	@ULOOP
	D;JLE
	@START
	0;JMP

