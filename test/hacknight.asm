; Password = XZgvSYhh7C
start:  jmp char_1
first:  db good_msg
char_1: input first
        subi first, 'X'
        jnz first, end
        jmp char_2

cmp_3:  db 206

; Simple compare with 'curr'
char_2: input curr
        subi curr, 'Z'
        jnz curr, end

; Write location changed
char_3: input curr
        muli curr, 2
        sub curr, cmp_3             ; 'g' = 103, * 2 = 206
        jnz curr, end

; Simple compare, TODO more
char_4: input curr
        subi curr, 118              ; 'v' = 118
        jnz curr, end

; Control flow obfuscated
char_5: jmp ch5_1
ch5_2:  subi curr, 'S'
        jnz curr, end
        jmp char_6
ch5_1:  input curr
        jmp ch5_2

; Simple compare
char_6: input first
        subi first, 'Y'
        jnz curr, end
        jmp ch_7_8

; Compares twice
ctr:    db 9
ch_7_8: input curr                  ; compare for 'h' twice
        subi curr, 'h'
        jnz curr, end
        subi ctr, 8
        jg ctr, ch_7_8

; Simple compare, overwrites code
char_9: input char_6
        subi char_6, '7'
        jnz char_6, end

; Add of negative number, TODO more
char_10: input curr
        addi curr, -67              ; 'C' = 67
        jnz curr, end

; Simple compare for EOF
end_ch: input curr                  ; check for EOF
        jge curr, end

; Print success
success: subleq curr, curr, $+3
mod:    subleq good_msg, Z, $+3
        subleq Z, curr, $+3
        subleq Z, Z, $+3

        jz curr, done
        output curr
        addi mod, 1
        jmp success

done:   nop

end:    jmp -1


curr:   db 0
hash:   db 0
mult:   db 31
good_msg: db 'G'
          db 'o'
          db 'o'
          db 'd'
          db 10
          db 0
