#!/usr/bin/python
#  team1_project1.py
#  Chase Phelps and Trenton Hohle
#  clp186           tah138
#  this converts some machine code into LEGv8 asm

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
    def run(infilename, outfilename):
        if infilename is None or outfilename is None:
            return
        fullmachinecode = [line.rstrip() for line in open(infilename, 'rb')]

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

            opcodes[i] = int(fullmachinecode[i], 2)
            opcodes[i] >>= 21
# NOP - nop
            if opcodes[i] == 0:
                instructionformat[i] = 'NOP'
# R - register
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
                    else:
                        instructions[i] = 'EOR'
# I - immediate
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
                else:
                    instructions[i] = 'SUBI'
# D - data load / store
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
# IM - move immediate / multiple
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
# B - this is the branch instruction
            elif 160 <= opcodes[i] <= 191:
                instructionformat[i] = 'B'
                instructions[i] = 'B'
                addrarray[i] = int(fullmachinecode[i], 2) & 67108863
#  CB - conditional branch
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
# BR - this is the data segment break
            elif opcodes[i] == 2038:
                instructionformat[i] = 'BR'
                datastartindex = i
                break
# for i in fullmachinecode[] end loop

#  now write the output file

        outfile = open(outfilename, 'w')
        memaddr = 92
        for i in range(len(fullmachinecode)):
            memaddr += 4
            outline = ""
# data segment
            if datastartindex is not None and i > datastartindex:
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\t"
                if int(fullmachinecode[i], 2) >> 31 > 0:
                    outline += str(gettwoscomplement(fullmachinecode[i]))
                else:
                    outline += str(fullmachinecode[i])
# instruction format not set
            elif instructionformat[i] is None:
                outline += "Instruction not recognized at address: " + str(memaddr)
# NOP - nop
            elif instructionformat[i] == 'NOP':
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\tNOP"
# R - register
            elif instructionformat[i] == 'R':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:16] + " " + fullmachinecode[i][16:22]
                outline += " " + fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32] + "\t" + str(memaddr)
                outline += "\t" + str(instructions[i]) + "\tR" + str(rdarray[i]) + ", R" + str(rnarray[i]) + ", "
                if instructions[i] == 'LSL' or instructions[i] == 'LSR':
                    outline += "#" + str(shamtarray[i])
                else:
                    outline += "R" + str(rmarray[i])
# I - immediate
            elif instructionformat[i] == 'I':
                outline += fullmachinecode[i][0:10] + " " + fullmachinecode[i][10:22] + " " + fullmachinecode[i][22:27]
                outline += " " + fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t" + instructions[i] + "\tR"
                outline += str(rdarray[i]) + ", R" + str(rnarray[i]) + ", #" + str(immarray[i])
# D - data load / store
            elif instructionformat[i] == 'D':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:20] + " " + fullmachinecode[i][20:22]
                outline += " " + fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32] + "\t" + str(memaddr)
                outline += "\t" + instructions[i] + "\tR" + str(rdarray[i]) + ", [R" + str(rnarray[i]) + ", #"
                outline += str(addrarray[i]) + "]"
# IM - move immediate / multiple
            elif instructionformat[i] == 'IM':
                outline += fullmachinecode[i][0:9] + " " + fullmachinecode[i][9:11] + " " + fullmachinecode[i][11:27]
                outline += " " + fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t" + instructions[i] + "\tR"
                outline += str(rdarray[i]) + ", " + str(immarray[i]) + ", LSL " + str(shamtarray[i] << 4)
# B - this is the branch instruction
            elif instructionformat[i] == 'B':
                outline += fullmachinecode[i][0:6] + " " + fullmachinecode[i][6:32] + "\t"
                outline += str(memaddr) + "\tB\t#" + str(addrarray[i])
# CB - conditional branch
            elif instructionformat[i] == 'CB':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:27] + " " + fullmachinecode[i][27:32]
                outline += "\t" + str(memaddr) + "\t" + instructions[i] + "\tR" + str(rdarray[i]) + ", #"
                outline += str(offsarray[i])
# BR - this is the data segment break
            elif instructionformat[i] == 'BR':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:11] + " " + fullmachinecode[i][11:16]
                outline += " " + fullmachinecode[i][16:21] + " " + fullmachinecode[i][21:26] + " "
                outline += fullmachinecode[i][26:32] + "\t" + str(memaddr) + "\tBREAK"
# write output line and restart loop if more lines to process
            print >> outfile, outline
# for i in fullmachinecode[] end loop

        outfile.close()


#  function called when script ran from command line and acts as a disassembler for machine code
#  ran in the form: $ python team#_project1.py -i test3_bin.txt -o team1_out_dis.txt
#  where test3_bin.txt is the input machine code text file that is read and team1_out_dis.txt is the dis output
if __name__ == "__main__":
    inputFileName = None
    outputFileName = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i' and i < (len(sys.argv) - 1):
            inputFileName = sys.argv[i + 1]
            print inputFileName
        elif sys.argv[i] == '-o' and i < (len(sys.argv) - 1):
            outputFileName = sys.argv[i + 1]
    Decompiler.run(inputFileName, outputFileName)
