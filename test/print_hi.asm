; Manually emit mov so it's clearer what's being modified.
start:  subleq curr, curr, $+3
mod:    subleq printme, Z, $+3
        subleq Z, curr, $+3
        subleq Z, Z, $+3

        ; If we just 'read' a 0 (i.e. null), we're done
        jz curr, done

        ; Print output
        output curr

        ; Increment the print address by 1
        addi mod, 1

        ; Next character
        jmp start

        ; Jumping to a negative address will halt the VM
done:   jmp -1


addr:           db 0
curr:           db 0
printme:        db 'H'
                db 'e'
                db 'l'
                db 'l'
                db 'o'
                db 10
                db 0
