#!/usr/bin/python

import sys

#  converts an unsigned binary text string into decimal
def binarytexttodecimal(binarytext):
    numba = 0
    for c in binarytext:
        numba = numba*2 + int(c)
    return numba

#  converts a signed 2's complement binary text string to decimal
def twoscbinarytexttodecimal(binarytext):
    numba = 0
    for c in binarytext:
        numba = numba*2 + (0 if int(c) == 1 else 1)
    numba = (numba + 1) * -1
    return numba

def main():
    fullmachinecode = [line.rstrip() for line in open(sys.argv[1], 'rb')]

    opcodes = []
    textend = 0
    instructionformat = []
    for i in range(len(fullmachinecode)):
        opcodes.append(fullmachinecode[i][0:11])
        opcodes[i] = binarytexttodecimal(opcodes[i])
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
# I - format
        elif (opcodes[i] == 1160 or opcodes[i] == 1161 or
              opcodes[i] == 1672 or opcodes[i] == 1673):
            instructionformat.append('I')
# D - format
        elif opcodes[i] == 1986 or opcodes[i] == 1984:
            instructionformat.append('D')
#  CB - format
        elif opcodes[i] == 1440 or opcodes[i] == 1448:
            instructionformat.append('CB')
# IM - format
        elif (opcodes[i] == 1684 or opcodes[i] == 1687 or
              opcodes[i] == 1940 or opcodes[i] == 1943):
            instructionformat.append('IM')
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
            print fullmachinecode[i][0:6] + " " + fullmachinecode[i][6:32] + "\t",
        elif instructionformat[i] == 'R':
            print fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:16] + " ",
            print fullmachinecode[i][16:22] + " " + fullmachinecode[i][22:27] + " ",
            print fullmachinecode[i][27:32] + "\t",
        elif instructionformat[i] == 'I':
            print fullmachinecode[i][0:10] + " " + fullmachinecode[i][10:22] + " ",
            print fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32] + "\t",
        elif instructionformat[i] == 'D':
            print fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:20] + " ",
            print fullmachinecode[i][20:22] + " " + fullmachinecode[i][22:27] + " ",
            print fullmachinecode[i][27:32] + "\t",
        elif instructionformat[i] == 'CB':
            print fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:27] + " ",
            print fullmachinecode[i][27:32] + "\t",
        elif instructionformat[i] == 'IM':
            print fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:27] + " ",
            print fullmachinecode[i][27:32] + "\t",
        elif instructionformat[i] == 'BR':
            print fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:11] + " ",
            print fullmachinecode[i][11:16] + " " + fullmachinecode[i][16:21] + " ",
            print fullmachinecode[i][21:26] + " " + fullmachinecode[i][26:32] + "\t",
        elif instructionformat[i] == 'NOP':
            print fullmachinecode[i] + "\t" + str(i * 4 + 96) + "\tNOP\n",
            continue
        else:
            print "something bad\t,"
        print str(i*4+96) + "\t",
        print "\n",


#  function called when script ran from command line
#  uses first arg, sys.argv[1], as input filepath
#  opens that file and 'decompiles' machine code to asm
if __name__ == "__main__":
    main()