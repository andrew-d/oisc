start:  addi expected, 9 ; 3*3*19*4001*4423
        muli expected, 19
        jmp inp
ten:    db 10
inp:    input curr
        jle curr, next
        mul hash, mult
        add hash, curr
        jmp inp

exp_temp: db 40
expected: db 0     ; 'foobar', value 3026088333
next:   mul exp_temp, ten
        mul exp_temp, ten
        addi exp_temp, 1        ; exp_temp = 4001

        mul expected, exp_temp

        zero exp_temp
        addi exp_temp, 44
        mul exp_temp, ten       ; exp_temp = 440
        mul exp_temp, ten       ; exp_temp = 4400
        addi exp_temp, 23       ; exp_temp = 4423

        mul expected, exp_temp  ; should be equal to final val

        sub hash, expected
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
          db 10
          db 0
