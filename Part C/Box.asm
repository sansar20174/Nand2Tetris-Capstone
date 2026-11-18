
 // Box.asm
 // K = 55
 // Starting row = 55
 // Height = 20 rows
 // Width = 64 pixels

(LOOP)
    @KBD
    D=M
    @SET_BLACK
    D;JGT

    @SET_WHITE
    0;JMP

(SET_BLACK)
    @R2
    M=-1
    @DRAW_BOX
    0;JMP

(SET_WHITE)
    @R2
    M=0

(DRAW_BOX)
    @18144
    D=A
    @R0
    M=D

    @20
    D=A
    @R1
    M=D

(ROW_LOOP)
    @R2
    D=M
    @R0
    A=M
    M=D
    @R0
    M=M+1

    @R2
    D=M
    @R0
    A=M
    M=D
    @R0
    M=M+1

    @R2
    D=M
    @R0
    A=M
    M=D
    @R0
    M=M+1

    @R2
    D=M
    @R0
    A=M
    M=D
    @R0
    M=M+1

    // Move to the next screen row
    @28
    D=A
    @R0
    M=D+M

    @R1
    MD=M-1
    @ROW_LOOP
    D;JGT

    @LOOP
    0;JMP
