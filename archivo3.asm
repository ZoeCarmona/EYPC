
     ld a, (1000h)
     ld b, a
     ld c, 1
eti3: ld a, c
     cp d
     jp z, eti1
     ld c, 0
     ld d, 0 
     ld ix, 1001h
eti5: dec b
     ld a, d
     cp b
     jp m, eti2
     jp eti3
eti2: inc b
     ld a, (ix+0)
     cp (ix+1)
     jp eti4
eti6: inc d
     inc ix
     jp eti5
eti4: ld e, (ix+1)
     ld (ix+0), e
     ld (ix+1), a 
     ld c, 1
     jp eti6
eti1: halt
