; Manually emit mov
start:  subleq curr, curr, $+3
mod:    subleq printme, Z, $+3
        subleq Z, curr, $+3
        subleq Z, Z, $+3

        jz curr, done

        output curr
        addi 1, mod

        jmp start

done:   jmp -1



addr:           db 0
curr:           db 0
printme:        db 'H'
                db 'e'
                db 'l'
                db 'l'
                db 'o'
                db 0
