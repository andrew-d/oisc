start:  mov ctr, printme_len
loop:   jz ctr, done
        mov -1, printme
done:   jmp -1



num_1:          db 1
ctr:            db 0
printme:        db 'H'
                db 'i'
printme_len:    db 2
