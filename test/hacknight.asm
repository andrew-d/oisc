start:  input curr
        jle curr, next
        mul hash, mult
        add hash, curr
        jmp start

expected: db 3026088333     ; 'foobar'
next:   sub hash, expected
        jnz hash, end

print:  subleq curr, curr, $+3
mod:    subleq good_msg, Z, $+3
        subleq Z, curr, $+3
        subleq Z, Z, $+3

        jz curr, done
        output curr
        addi mod, 1
        jmp print

done:   nop

end:    jmp -1


curr:   db 0
hash:   db 0
mult:   db 31
good_msg: db 'G'
          db 'o'
          db 'o'
          db 'd'
          db 0
