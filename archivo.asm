
      ld b,1;
      ld c,1;
      ld a,(1001h);
      cp 0;
      
jp z,eti1;
eti3: cp b;
      jp m,eti1;
      sub b;
      ld d,a;
      ld a,b;
      inc a;
      inc a;
      ld b,a;
      ld a,c;
      inc a;
      ld c,a;
      ld a,d;
      jp eti3;
eti1: ld a,c;
      dec a;
      ld (1000h),a;
      halt
