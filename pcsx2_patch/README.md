# NOTES

## Restoring Debug Print

Restoring debug print functionality can be done in a minimum of 4 instructions, 2 if ignoring the return.
Rough code looks like the following.

```
24030075 addiu v1,zero,0x75
0000000C syscall --- 
03E00008 jr ra
00000000 nop 
```

Debug printing on PS2 works in 3 steps
1. Set `a0` register to a null terminated string pointer
2. Set `v1` to the ID of the syscall you want to execute, for the print syscall this is `0x75` or `117`
3. Run the `syscall` instruction to call the print function.

The snippet of code above can be placed in a stubbed out print function that has already set up `a0`. Simply
setting `v1` and executing `syscall` will print, after that we can `jr` or jump return back to the original function. 
We add a `nop` because the PS2 CPU reads 64 bits of instructions at a time before it executes.

## Custom Debug Print to Print Filenames

The games will dynamically hash a string before locating the file in the PackInfo file. We can intercept the hash function
to print the pre hashed string to give us the original filenames.

Lucky for us the hash function already has the string to be hashed as the first argument in register `a0`. We can skip step 1
and move right onto 2 and 3.

We need a place to store our new code, we can't just insert new instructions before the code as that would affect all the jumps
that happen across the codebase. Instead we need to leverage a `code cave`, a region of memory that we can safely inject code that won't
overwrite functionality of the game.

The easiest solution would be to take the original assembly and just prepend a print syscall. We can simply rewrite the original hash function
to immedately jump to our code cave, execute the hash, then when that finishes and calls `jr` we do another `jr` in the original function.

An important detail to note, the print syscall will not add newlines automatically, multiple print statements will not appear until a newline is enountered
flushing that line to the logging output then moving onto the next.

## Pumped & Primed

```
001008c0 - printf
00100890 - printf
003727b8 - CalculateHash
```

```
// Hash Function
// Jump into code
patch=1,EE,203727b8,extended,08192040
// Write our return address into $t3
patch=1,EE,203727bc,extended,03E0582D
// Newline
patch=1,EE,106480fc,extended,0000000A
// Newline
patch=1,EE,20648100,extended,24030075
// Syscall
patch=1,EE,20648104,extended,0000000C
patch=1,EE,20648108,extended,0080482D
// Set $t7 to $a0
patch=1,EE,2064810C,extended,3C040064
// Set $a0 to the newline
patch=1,EE,20648110,extended,348480fc
patch=1,EE,20648114,extended,00802021
patch=1,EE,20648118,extended,24030075
// Syscall
patch=1,EE,2064811C,extended,0000000C
patch=1,EE,20648120,extended,0120202D
// Set $a0 to $t7
patch=1,EE,20648124,extended,908C0000
// Original Function
patch=1,EE,20648128,extended,318F00FF
patch=1,EE,2064812C,extended,11E0000B
patch=1,EE,20648130,extended,0000102D
patch=1,EE,20648134,extended,000278F8
patch=1,EE,20648138,extended,318D00FF
patch=1,EE,2064813C,extended,01E2782D
patch=1,EE,20648140,extended,24840001
patch=1,EE,20648144,extended,000F78B8
patch=1,EE,20648148,extended,908C0000
patch=1,EE,2064814C,extended,01E2782D
patch=1,EE,20648150,extended,318E00FF
patch=1,EE,20648154,extended,15C0FFF7
patch=1,EE,20648158,extended,01ED102D
patch=1,EE,2064815C,extended,0002103C
patch=1,EE,20648160,extended,01600008
// Jump return $t3
patch=1,EE,20648164,extended,0002103F
patch=1,EE,20648168,extended,00000000
```

## Million Monkeys

```
00100a18 - printf
00100a48 - printf
00485e60 - CalculateHash
```

```
// Hash Function
// Jump into code
patch=1,EE,20485e60,extended,08196040
// Write our return address into $t3
patch=1,EE,20485e64,extended,03E0582D
// Newline
patch=1,EE,106580fc,extended,0000000A
// Syscall
patch=1,EE,20658100,extended,24030075
patch=1,EE,20658104,extended,0000000C
// Set $t7 to $a0
patch=1,EE,20658108,extended,0080482D
// Set $a0 to the newline
patch=1,EE,2065810C,extended,3C040065
patch=1,EE,20658110,extended,348480fc
patch=1,EE,20658114,extended,00802021
// Set Syscall
patch=1,EE,20658118,extended,24030075
patch=1,EE,2065811C,extended,0000000C
// Set $a0 to $t7
patch=1,EE,20658120,extended,0120202D
// Original Function
patch=1,EE,20658124,extended,908C0000
patch=1,EE,20658128,extended,318F00FF
patch=1,EE,2065812C,extended,11E0000B
patch=1,EE,20658130,extended,0000102D
patch=1,EE,20658134,extended,000278F8
patch=1,EE,20658138,extended,318D00FF
patch=1,EE,2065813C,extended,01E2782D
patch=1,EE,20658140,extended,24840001
patch=1,EE,20658144,extended,000F78B8
patch=1,EE,20658148,extended,908C0000
patch=1,EE,2065814C,extended,01E2782D
patch=1,EE,20658150,extended,318E00FF
patch=1,EE,20658154,extended,15C0FFF7
patch=1,EE,20658158,extended,01ED102D
patch=1,EE,2065815C,extended,0002103C
patch=1,EE,20658160,extended,01600008
// Jump return $t3
patch=1,EE,20658164,extended,0002103F
patch=1,EE,20658168,extended,00000000
```