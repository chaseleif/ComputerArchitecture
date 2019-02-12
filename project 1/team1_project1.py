#!/usr/bin/python
#  team1_project1.py
#  Chase Phelps and Trenton Hohle
#  this converts some machine code into LEGv8 asm
#  input file is given as a command line argument
#  output file is (infilename) + out_dis.txt

import sys


#  converts an unsigned binary text string into decimal
def binarytexttodecimal(binarytext):
    numba = 0
    for c in binarytext:
        numba = numba*2 + int(c)
    return numba


#  converts a _signed_ and _negative_ 2's complement binary text string to decimal
#  only call if the most significant digit is a ONE, this is only for negative 2C nums
def twoscbinarytexttodecimal(binarytext):
    numba = 0
    for c in binarytext:
        numba = numba*2 + (0 if int(c) == 1 else 1)
    numba = (numba + 1) * -1
    return numba


class Decompiler:

    def __init__(self):
        pass

    @staticmethod
    def decompile(infile):
        fullmachinecode = [line.rstrip() for line in open(infile, 'rb')]
#  opened input file, now get our output filename
        textend = infile.find('.')
        outfilename = infile[:textend] + "out_dis.txt"
        outfile = open(outfilename, 'w')

        opcodes = []
        textend = 0
        instructionformat = []
        theinstruction = []
        for i in range(len(fullmachinecode)):
            opcodes.append(binarytexttodecimal(fullmachinecode[i][0:11]))
            theinstruction.append('')
    #  text/data break
            if opcodes[i] == 2038:
                instructionformat.append('BR')
                textend = i
                break
    # B - format
            if 160 <= opcodes[i] <= 191:
                instructionformat.append('B')
    # R - format
            elif (opcodes[i] == 1112 or opcodes[i] == 1624 or
                  opcodes[i] == 1691 or opcodes[i] == 1690 or
                  opcodes[i] == 1104 or opcodes[i] == 1360 or opcodes[i] == 1872):
                instructionformat.append('R')
                if opcodes[i] == 1112:
                    theinstruction[i] = 'ADD'
                elif opcodes[i] == 1624:
                    theinstruction[i] = 'SUB'
                elif opcodes[i] == 1691:
                    theinstruction[i] = 'LSL'
                elif opcodes[i] == 1690:
                    theinstruction[i] = 'LSR'
                elif opcodes[i] == 1104:
                    theinstruction[i] = 'AND'
                elif opcodes[i] == 1360:
                    theinstruction[i] = 'ORR'
                elif opcodes[i] == 1872:
                    theinstruction[i] = 'EOR'
    # I - format
            elif (1160 <= opcodes[i] <= 1161 or
                  1672 <= opcodes[i] <= 1673):
                instructionformat.append('I')
                if 1160 <= opcodes[i] <= 1161:
                    theinstruction[i] = 'ADDI'
                elif 1672 <= opcodes[i] <= 1673:
                    theinstruction[i] = 'SUBI'
    # D - format
            elif opcodes[i] == 1986 or opcodes[i] == 1984:
                instructionformat.append('D')
                if opcodes[i] == 1986:
                    theinstruction[i] = 'LDUR'
                else:
                    theinstruction[i] = 'STUR'
    #  CB - format
            elif (1440 <= opcodes[i] <= 1447 or
                  1448 <= opcodes[i] <= 1455):
                instructionformat.append('CB')
                if 1440 <= opcodes[i] <= 1447:
                    theinstruction[i] = 'CBZ'
                else:
                    theinstruction[i] = 'CBNZ'
    # IM - format
            elif (1684 <= opcodes[i] <= 1687 or
                  1940 <= opcodes[i] <= 1943):
                instructionformat.append('IM')
                if 1684 <= opcodes[i] <= 1687:
                    theinstruction[i] = 'MOVZ'
                else:
                    theinstruction[i] = 'MOVK'
    # NOP
            elif opcodes[i] == 0:
                instructionformat.append('NOP')
            else:
                instructionformat.append('OTHER')

        for i in range(len(fullmachinecode)):
            if i > textend:
                print >> outfile, fullmachinecode[i] + "\t" + str(i * 4 + 96) + "\t",
                print >> outfile, (str(twoscbinarytexttodecimal(fullmachinecode[i])) if fullmachinecode[i][0] == '1'
                       else binarytexttodecimal(fullmachinecode[i])),
                print >> outfile, "\n",
                continue
            if instructionformat[i] == 'B':
                print >> outfile, fullmachinecode[i][0:6] + " " + fullmachinecode[i][6:32] + "   ",
            elif instructionformat[i] == 'R':
                print >> outfile, fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:16],
                print >> outfile, fullmachinecode[i][16:22] + " " + fullmachinecode[i][22:27],
                print >> outfile, fullmachinecode[i][27:32],
            elif instructionformat[i] == 'I':
                print >> outfile, fullmachinecode[i][0:10] + " " + fullmachinecode[i][10:22],
                print >> outfile, fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32],
            elif instructionformat[i] == 'D':
                print >> outfile, fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:20],
                print >> outfile, fullmachinecode[i][20:22] + " " + fullmachinecode[i][22:27],
                print >> outfile, fullmachinecode[i][27:32],
            elif instructionformat[i] == 'CB':
                print >> outfile, fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:27],
                print >> outfile, fullmachinecode[i][27:32] + " ",
            elif instructionformat[i] == 'IM':
                print >> outfile, fullmachinecode[i][0:9] + " " + fullmachinecode[i][9:11],
                print >> outfile, fullmachinecode[i][11:27] + " " + fullmachinecode[i][27:32],
            elif instructionformat[i] == 'BR':
                print >> outfile, fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:11],
                print >> outfile, fullmachinecode[i][11:16] + " " + fullmachinecode[i][16:21],
                print >> outfile, fullmachinecode[i][21:26] + " " + fullmachinecode[i][26:32],
            elif instructionformat[i] == 'NOP':
                print >> outfile, fullmachinecode[i] + "\t" + str(i * 4 + 96) + "\tNOP"
                continue
            else:
                print >> outfile, "something bad\t,"
            print >> outfile, "\t" + str(i*4+96) + "\t",

            if instructionformat[i] == 'B':
                print >> outfile, "B\t#" + str(binarytexttodecimal(fullmachinecode[i][6:32]))
            elif instructionformat[i] == 'R':
                print >> outfile, theinstruction[i] + "\tR" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
                print >> outfile, "R" + str(binarytexttodecimal(fullmachinecode[i][22:27])) + ",",
                if theinstruction[i] == 'LSL' or theinstruction[i] == 'LSR':
                    if fullmachinecode[i][16] == '0':
                        print >> outfile, "#" + str(binarytexttodecimal(fullmachinecode[i][16:22]))
                    else:
                        print >> outfile, "#" + str(twoscbinarytexttodecimal(fullmachinecode[i][16:22]))
                else:
                    print >> outfile, "R" + str(binarytexttodecimal(fullmachinecode[i][11:16]))
            elif instructionformat[i] == 'I':
                print >> outfile, (theinstruction[i] + "\tR" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ", R" +
                       str(binarytexttodecimal(fullmachinecode[i][22:27])) + ","),
                print >> outfile, ("#" + str(twoscbinarytexttodecimal(fullmachinecode[i][10:22])) if fullmachinecode[i][10] == '1'
                       else "#" + str(binarytexttodecimal(fullmachinecode[i][10:22])))
            elif instructionformat[i] == 'D':
                print >> outfile, theinstruction[i] + "\tR" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
                print >> outfile, "[R" + str(binarytexttodecimal(fullmachinecode[i][22:27])) + ",",
                print >> outfile, "#" + str(binarytexttodecimal(fullmachinecode[i][11:20])) + "]"
            elif instructionformat[i] == 'CB':
                print >> outfile, theinstruction[i] + " \tR" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
                print >> outfile, "#" + str(binarytexttodecimal(fullmachinecode[i][8:27]))
            elif instructionformat[i] == 'IM':
                print >> outfile, theinstruction[i] + "\tR" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
                print >> outfile, str(binarytexttodecimal(fullmachinecode[i][11:27])) + ",",
                print >> outfile, "LSL " + str(16*binarytexttodecimal(fullmachinecode[i][9:11]))
            elif instructionformat[i] == 'BR':
                print >> outfile, "BREAK"
            elif instructionformat[i] == 'NOP':
                print >> outfile, "NOP"
            else:
                print >> outfile, "something bad\t"
        outfile.close()


#  function called when script ran from command line
#  uses first arg, sys.argv[1], as input filepath
#  opens that file and 'decompiles' machine code to asm
if __name__ == "__main__":
    Decompiler.decompile(sys.argv[1])
