#!/usr/bin/python
#  team1_project1.py
#  Chase Phelps and Trenton Hohle
#  this converts some machine code into LEGv8 asm
#  input file is given as a command line argument
#  output file is (infilename) + out_dis.txt

import sys


def gettwoscomplement(binarystring):
    returnval = 0
    for digit in binarystring:
        returnval *= 2
        if digit is '0':
            returnval += 1
    return -(returnval + 1)


class Decompiler:

    def __init__(self):
        pass

    @staticmethod
    def decompile(infilename, outfilename):
        if infilename == "" or outfilename == "":
            return
        fullmachinecode = [line.rstrip() for line in open(infilename, 'rb')]

        binarystring = [None] * len(fullmachinecode)
        opcodes = [None] * len(fullmachinecode)
        instructionformat = [None] * len(fullmachinecode)
        instructions = [None] * len(fullmachinecode)
        rdarray = [None] * len(fullmachinecode)
        rnarray = [None] * len(fullmachinecode)
        rmarray = [None] * len(fullmachinecode)
        shamtarray = [None] * len(fullmachinecode)
        immarray = [None] * len(fullmachinecode)
        addrarray = [None] * len(fullmachinecode)
        offsarray = [None] * len(fullmachinecode)

        datastartindex = None

        for i in range(len(fullmachinecode)):
            opcodes[i] = binarystring[i] = int(fullmachinecode[i], 2)

            if datastartindex is not None:
                continue

            opcodes[i] >>= 21
# BR
            if opcodes[i] == 2038:
                instructionformat[i] = 'BR'
                datastartindex = i
                break
# B
            elif 160 <= opcodes[i] <= 191:
                instructionformat[i] = 'B'
                instructions[i] = 'B'
                addrarray[i] = int(fullmachinecode[i], 2) & 67108863
# R
            elif (opcodes[i] == 1112 or opcodes[i] == 1624 or
                  opcodes[i] == 1691 or opcodes[i] == 1690 or
                  opcodes[i] == 1104 or opcodes[i] == 1360 or opcodes[i] == 1872):
                instructionformat[i] = 'R'
                rdarray[i] = int(fullmachinecode[i], 2) & 31
                rnarray[i] = int(fullmachinecode[i], 2) & 992
                rnarray[i] >>= 5
                if 1690 <= opcodes[i] <= 1691:
                    shamtarray[i] = int(fullmachinecode[i], 2) & 64512
                    shamtarray[i] >>= 10
                    if opcodes[i] == 1690:
                        instructions[i] = 'LSR'
                    else:
                        instructions[i] = 'LSL'
                else:
                    rmarray[i] = int(fullmachinecode[i], 2) & 2031616
                    rmarray[i] >>= 16
                    if opcodes[i] == 1112:
                        instructions[i] = 'ADD'
                    elif opcodes[i] == 1624:
                        instructions[i] = 'SUB'
                    elif opcodes[i] == 1104:
                        instructions[i] = 'AND'
                    elif opcodes[i] == 1360:
                        instructions[i] = 'ORR'
                    elif opcodes[i] == 1872:
                        instructions[i] = 'EOR'
# I
            elif (1160 <= opcodes[i] <= 1161 or
                  1672 <= opcodes[i] <= 1673):
                instructionformat[i] = 'I'
                rdarray[i] = int(fullmachinecode[i], 2) & 31
                rnarray[i] = int(fullmachinecode[i], 2) & 992
                rnarray[i] >>= 5
                immarray[i] = int(fullmachinecode[i], 2) & 4193280
                immarray[i] >>= 10
                if immarray[i] >> 11 > 0:
                    immarray[i] = gettwoscomplement(fullmachinecode[i][10:22])
                if 1160 <= opcodes[i] <= 1161:
                    instructions[i] = 'ADDI'
                elif 1672 <= opcodes[i] <= 1673:
                    instructions[i] = 'SUBI'
# D
            elif opcodes[i] == 1986 or opcodes[i] == 1984:
                instructionformat[i] = 'D'
                rdarray[i] = int(fullmachinecode[i], 2) & 31
                rnarray[i] = int(fullmachinecode[i], 2) & 992
                rnarray[i] >>= 5
                addrarray[i] = int(fullmachinecode[i], 2) & 2093056
                addrarray[i] >>= 12
                if opcodes[i] == 1986:
                    instructions[i] = 'LDUR'
                else:
                    instructions[i] = 'STUR'
#  CB
            elif (1440 <= opcodes[i] <= 1447 or
                  1448 <= opcodes[i] <= 1455):
                rdarray[i] = int(fullmachinecode[i], 2) & 31
                offsarray[i] = int(fullmachinecode[i], 2) & 16777184
                offsarray[i] >>= 5
                instructionformat[i] = 'CB'
                if 1440 <= opcodes[i] <= 1447:
                    instructions[i] = 'CBZ'
                else:
                    instructions[i] = 'CBNZ'
# IM
            elif (1684 <= opcodes[i] <= 1687 or
                  1940 <= opcodes[i] <= 1943):
                instructionformat[i] = 'IM'
                rdarray[i] = int(fullmachinecode[i], 2) & 31
                shamtarray[i] = int(fullmachinecode[i], 2) & 6291456
                shamtarray[i] >>= 21
                immarray[i] = int(fullmachinecode[i], 2) & 2097120
                immarray[i] >>= 5
                if 1684 <= opcodes[i] <= 1687:
                    instructions[i] = 'MOVZ'
                else:
                    instructions[i] = 'MOVK'
# NOP
            elif opcodes[i] == 0:
                instructionformat[i] = 'NOP'

#  now write the output file

        outfile = open(outfilename, 'w')
        memaddr = 92
        for i in range(len(fullmachinecode)):
            memaddr += 4
            outline = ""
            if i > datastartindex:
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\t"
                if int(fullmachinecode[i], 2) >> 31 > 0:
                    outline += str(gettwoscomplement(fullmachinecode[i]))
                else:
                    outline += str(fullmachinecode[i])
            elif instructionformat[i] is None:
                outline += "Instruction not recognized at address: " + str(memaddr)
            elif instructionformat[i] == 'NOP':
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\tNOP"
            elif instructionformat[i] == 'B':
                outline += fullmachinecode[i][0:6] + " " + fullmachinecode[i][6:32] + "\t"
                outline += str(memaddr) + "\tB\t#" + str(addrarray[i])
            elif instructionformat[i] == 'R':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:16] + " " + fullmachinecode[i][16:22]
                outline += " " + fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32] + "\t" + str(memaddr)
                outline += "\t" + str(instructions[i]) + "\tR" + str(rdarray[i]) + ", R" + str(rnarray[i]) + ", "
                if instructions[i] == 'LSL' or instructions[i] == 'LSR':
                    outline += "#" + str(shamtarray[i])
                else:
                    outline += "R" + str(rmarray[i])
            elif instructionformat[i] == 'I':
                outline += fullmachinecode[i][0:10] + " " + fullmachinecode[i][10:22] + " " + fullmachinecode[i][22:27]
                outline += " " + fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t" + instructions[i] + "\tR"
                outline += str(rdarray[i]) + ", R" + str(rnarray[i]) + ", #" + str(immarray[i])
            elif instructionformat[i] == 'D':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:20] + " " + fullmachinecode[i][20:22]
                outline += " " + fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32] + "\t" + str(memaddr)
                outline += "\t" + instructions[i] + "\tR" + str(rdarray[i]) + ", [R" + str(rnarray[i]) + ", #"
                outline += str(addrarray[i]) + "]"
            elif instructionformat[i] == 'CB':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:27] + " " + fullmachinecode[i][27:32]
                outline += "\t" + str(memaddr) + "\t" + instructions[i] + "\tR" + str(rdarray[i]) + ", #"
                outline += str(offsarray[i])
            elif instructionformat[i] == 'IM':
                outline += fullmachinecode[i][0:9] + " " + fullmachinecode[i][9:11] + " " + fullmachinecode[i][11:27]
                outline += " " + fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t" + instructions[i] + "\tR"
                outline += str(rdarray[i]) + ", " + str(immarray[i]) + ", LSL " + str(shamtarray[i] << 4)
            elif instructionformat[i] == 'BR':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:11] + " " + fullmachinecode[i][11:16]
                outline += " " + fullmachinecode[i][16:21] + " " + fullmachinecode[i][21:26] + " "
                outline += fullmachinecode[i][26:32] + "\t" + str(memaddr) + "\tBREAK"
            print >> outfile, outline
        outfile.close()


#  function called when script ran from command line
#  uses first arg, sys.argv[1], as input filepath
#  opens that file and 'decompiles' machine code to asm
if __name__ == "__main__":
    inputFileName = None
    outputFileName = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i' and i < (len(sys.argv) - 1):
            inputFileName = sys.argv[i + 1]
            print inputFileName
        elif sys.argv[i] == '-o' and i < (len(sys.argv) - 1):
            outputFileName = sys.argv[i + 1]
    Decompiler.decompile(inputFileName, outputFileName)
