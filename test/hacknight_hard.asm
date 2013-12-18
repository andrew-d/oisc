; Password = XZgvSYhh7C
start:  jmp char_1
first:  db '4'

; 1. Super simple comparison.
char_1: input first
        subi first, 'X'
        sub valid, first
        jmp char_2

cmp_3:  db 206

; 2. Simple compare at address 'curr'
char_2: input curr
        subi curr, 'Z'
        sub valid, curr

; 3. Multiply before comparing.
char_3: input curr
        muli curr, 2
        sub curr, cmp_3             ; 'g' = 103, * 2 = 206
        add valid, curr

; 4. Simple compare, TODO more
char_4: input curr
        subi curr, 'v'              ; 'v' = 118
        sub valid, curr

; 5. Control flow obfuscated
char_5: jmp ch5_1
        db 'F'

    ; 6. Simple compare (embedded in above)
    char_6: input first
            subi first, 'Y'
            add valid, curr
            jmp ch_7_8

ch5_2:  subi curr, 'S'
        sub valid, curr
        jmp char_6
neg_1:  db -1
        db 'e'
ch5_1:  input curr
        jmp ch5_2

; 7. Compares twice
        db 'M'
ctr:    db 9
ch_7_8: input curr                  ; compare for 'h' twice
        subi curr, 'h'
        add valid, curr
        subi ctr, 8
        jg ctr, ch_7_8

; 8. Simple compare, overwrites old code
char_9: input char_6
        subi char_6, '7'
        add valid, curr

; 9. Add of negative number, TODO more
char_10: input curr
        add curr, neg_1
        addi curr, -66              ; 'C' = 67
        sub valid, curr

; 10. Simple compare for EOF
end_ch: input curr                  ; check for EOF
        jge curr, end

; 11. Validate the final number
        subi valid, 95
        jnz valid, end

; Print success
success: subleq curr, curr, $+3
mod:    subleq good_msg, Z, $+3
        subleq Z, curr, $+3
        subleq Z, Z, $+3

        jz curr, done
        output curr
        addi mod, 1
        jmp success
        db 'B'
done:   nop

end:    jmp -1


curr:   db 0
hash:   db 0
mult:   db 31
valid:  db 95
good_msg: db 'G'
          db 'o'
          db 'o'
          db 'd'
          db 10
          db 0
