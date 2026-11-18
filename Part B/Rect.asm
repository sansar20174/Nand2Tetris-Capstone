// Draw rectangle

@55
D=A
@16
M=D

(LOOP)
@16
D=M
@16384
M=D

@16
M=M-1
@LOOP
D;JGT

(END)
@END
0;JMP