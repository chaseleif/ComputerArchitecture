#!/usr/bin/python

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


def regnumba(binarytext):
    numba = 0
    for c in binarytext:
        numba = numba*2 + int(c)
    if numba < 32:
        return numba
    return -1


def main():
    fullmachinecode = [line.rstrip() for line in open(sys.argv[1], 'rb')]

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
              opcodes[i] == 1104 or opcodes[i] == 1360 or opcodes[i] == 1616):
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
            elif opcodes[i] == 1616:
                theinstruction[i] = 'EOR'
# I - format
        elif (opcodes[i] == 1160 or opcodes[i] == 1161 or
              opcodes[i] == 1672 or opcodes[i] == 1673):
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
        elif opcodes[i] == 1440 or opcodes[i] == 1448:
            instructionformat.append('CB')
            if opcodes[i] == 1440:
                theinstruction[i] = 'CBZ'
            else:
                theinstruction[i] = 'CBNZ'
# IM - format
        elif (opcodes[i] == 1684 or opcodes[i] == 1687 or
              opcodes[i] == 1940 or opcodes[i] == 1943):
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
            print fullmachinecode[i],
            print str(i * 4 + 96) + "\t",
            print (str(twoscbinarytexttodecimal(fullmachinecode[i])) if fullmachinecode[i][0] == '1'
                   else binarytexttodecimal(fullmachinecode[i])),
            print "\n",
            continue
        if instructionformat[i] == 'B':
            print fullmachinecode[i][0:6] + " " + fullmachinecode[i][6:32],
        elif instructionformat[i] == 'R':
            print fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:16],
            print fullmachinecode[i][16:22] + " " + fullmachinecode[i][22:27],
            print fullmachinecode[i][27:32],
        elif instructionformat[i] == 'I':
            print fullmachinecode[i][0:10] + " " + fullmachinecode[i][10:22],
            print fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32],
        elif instructionformat[i] == 'D':
            print fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:20],
            print fullmachinecode[i][20:22] + " " + fullmachinecode[i][22:27],
            print fullmachinecode[i][27:32],
        elif instructionformat[i] == 'CB':
            print fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:27],
            print fullmachinecode[i][27:32],
        elif instructionformat[i] == 'IM':
            print fullmachinecode[i][0:9] + " " + fullmachinecode[i][9:11],
            print fullmachinecode[i][11:27] + " " + fullmachinecode[i][27:32],
        elif instructionformat[i] == 'BR':
            print fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:11],
            print fullmachinecode[i][11:16] + " " + fullmachinecode[i][16:21],
            print fullmachinecode[i][21:26] + " " + fullmachinecode[i][26:32],
        elif instructionformat[i] == 'NOP':
            print fullmachinecode[i],
            continue
        else:
            print "something bad\t,"
        print str(i*4+96) + "\t",

        if instructionformat[i] == 'B':
            print "B #" + str(binarytexttodecimal(fullmachinecode[i][6:32]))
        elif instructionformat[i] == 'R':
            print theinstruction[i] + " R" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
            print "R" + str(binarytexttodecimal(fullmachinecode[i][22:27])) + ",",
            if theinstruction[i] == 'LSL' or theinstruction[i] == 'LSR':
                if fullmachinecode[i][16] == '0':
                    print "#" + str(binarytexttodecimal(fullmachinecode[i][16:22]))
                else:
                    print "#" + str(twoscbinarytexttodecimal(fullmachinecode[i][16:22]))
            else:
                print "R" + str(binarytexttodecimal(fullmachinecode[i][11:16]))
        elif instructionformat[i] == 'I':
            print (theinstruction[i] + " R" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ", R" +
                   str(binarytexttodecimal(fullmachinecode[i][22:27])) + ", #" +
                   str(binarytexttodecimal(fullmachinecode[i][10:22])))
        elif instructionformat[i] == 'D':
            print theinstruction[i] + " R" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
            print "[R" + str(binarytexttodecimal(fullmachinecode[i][22:27])) + ",",
            print "#" + str(binarytexttodecimal(fullmachinecode[i][11:20])) + "]"
        elif instructionformat[i] == 'CB':
            print theinstruction[i] + " R" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
            print "#" + str(binarytexttodecimal(fullmachinecode[i][8:27]))
#  need to find out IM opcode / MOVZ/MOVK details!!! #
        elif instructionformat[i] == 'IM':
            print theinstruction[i] + " R" + str(binarytexttodecimal(fullmachinecode[i][27:32])) + ",",
            print str(binarytexttodecimal(fullmachinecode[i][11:27]))
        elif instructionformat[i] == 'BR':
            print "BREAK"
        elif instructionformat[i] == 'NOP':
            print "NOP"
        else:
            print "something bad\t"


#  function called when script ran from command line
#  uses first arg, sys.argv[1], as input filepath
#  opens that file and 'decompiles' machine code to asm
if __name__ == "__main__":
    main()
