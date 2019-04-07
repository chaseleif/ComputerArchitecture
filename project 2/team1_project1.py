#!/usr/bin/python
#  team1_project1.py
#  Chase Phelps and Trenton Hohle
#  clp186           tah138
#  part one: this converts some machine code into LEGv8 asm
#  part two: this then emulates step-through execution, printing info

import sys


class Decompiler:

    def __init__(self):
        self.opcodes = [None]
        self.instructionformat = [None]
        self.instructions = [None]
        self.instrdisplaystring = [None]
        self.rdarray = [None]
        self.rnarray = [None]
        self.rmarray = [None]
        self.shamtarray = [None]
        self.immarray = [None]
        self.addrarray = [None]
        self.offsarray = [None]
        self.datastartindex = None
        self.dataendindex = None
        self.datasegment = {}

    def run(self, infilename, outfilename):
        if infilename is None or outfilename is None:
            return
        outfilename += "_dis.txt"
        fullmachinecode = [line.rstrip() for line in open(infilename, 'rb')]

        self.datastartindex = None
        self.dataendindex = None
        self.opcodes = [None] * len(fullmachinecode)
        self.instructionformat = [None] * len(fullmachinecode)
        self.instructions = [None] * len(fullmachinecode)
        self.instrdisplaystring = [None] * len(fullmachinecode)
        self.rdarray = [None] * len(fullmachinecode)
        self.rnarray = [None] * len(fullmachinecode)
        self.rmarray = [None] * len(fullmachinecode)
        self.shamtarray = [None] * len(fullmachinecode)
        self.immarray = [None] * len(fullmachinecode)
        self.addrarray = [None] * len(fullmachinecode)
        self.offsarray = [None] * len(fullmachinecode)
        self.datasegment = {}

        for i in range(len(fullmachinecode)):
# data
            if self.datastartindex is not None:
                # dictionary, keyed by "actual" memory address
                self.datasegment[(i * 4) + 96] = fullmachinecode[i]
                self.dataendindex = i
                continue
# text
            self.opcodes[i] = int(fullmachinecode[i], 2)
            self.opcodes[i] >>= 21
# NOP - nop
            if self.opcodes[i] == 0:
                self.instructionformat[i] = 'NOP'
# R - register
            elif (self.opcodes[i] == 1112 or self.opcodes[i] == 1624 or
                  self.opcodes[i] == 1691 or self.opcodes[i] == 1690 or
                  self.opcodes[i] == 1692 or self.opcodes[i] == 1104 or
                  self.opcodes[i] == 1360 or self.opcodes[i] == 1872):
                self.instructionformat[i] = 'R'
                self.rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                self.rnarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x1F
                if 1690 <= self.opcodes[i] <= 1691:
                    self.shamtarray[i] = (int(fullmachinecode[i], 2) >> 10) & 0x3F
                    if self.opcodes[i] == 1690:
                        self.instructions[i] = 'LSR'
                    elif self.opcodes[i] == 1692:
                        self.instructions[i] = 'ASR'
                    else:
                        self.instructions[i] = 'LSL'
                else:
                    self.rmarray[i] = (int(fullmachinecode[i], 2) >> 16) & 0x1F
                    if self.opcodes[i] == 1112:
                        self.instructions[i] = 'ADD'
                    elif self.opcodes[i] == 1624:
                        self.instructions[i] = 'SUB'
                    elif self.opcodes[i] == 1104:
                        self.instructions[i] = 'AND'
                    elif self.opcodes[i] == 1360:
                        self.instructions[i] = 'ORR'
                    else:
                        self.instructions[i] = 'EOR'
# I - immediates
            elif (1160 <= self.opcodes[i] <= 1161 or
                  1672 <= self.opcodes[i] <= 1673):
                self.instructionformat[i] = 'I'
                self.rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                self.rnarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x1F
                self.immarray[i] = (int(fullmachinecode[i], 2) >> 10) & 0xFFF
                if self.immarray[i] >> 11 > 0:
                    self.immarray[i] ^= 0xFFF
                    self.immarray[i] += 1
                    self.immarray[i] *= -1
                if 1160 <= self.opcodes[i] <= 1161:
                    self.instructions[i] = 'ADDI'
                else:
                    self.instructions[i] = 'SUBI'
# D - data load and store
            elif self.opcodes[i] == 1986 or self.opcodes[i] == 1984:
                self.instructionformat[i] = 'D'
                self.rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                self.rnarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x1F
                self.addrarray[i] = (int(fullmachinecode[i], 2) >> 12) & 0x1FF
                if self.addrarray[i] >> 8 > 0:
                    self.addrarray[i] ^= 0x1FF
                    self.addrarray[i] += 1
                    self.addrarray[i] *= -1
                if self.opcodes[i] == 1986:
                    self.instructions[i] = 'LDUR'
                else:
                    self.instructions[i] = 'STUR'
# IM - move immediate and movezk
            elif (1684 <= self.opcodes[i] <= 1687 or
                  1940 <= self.opcodes[i] <= 1943):
                self.instructionformat[i] = 'IM'
                self.rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                self.shamtarray[i] = ((int(fullmachinecode[i], 2) >> 21) & 0x3) << 4
                self.immarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0xFFFF
                if 1684 <= self.opcodes[i] <= 1687:
                    self.instructions[i] = 'MOVZ'
                else:
                    self.instructions[i] = 'MOVK'
# B - branch
            elif 160 <= self.opcodes[i] <= 191:
                self.instructionformat[i] = 'B'
                self.instructions[i] = 'B'
                self.addrarray[i] = int(fullmachinecode[i], 2) & 0x3FFFFFF
                if self.addrarray[i] >> 25 > 0:
                    self.addrarray[i] ^= 0x3FFFFFF
                    self.addrarray[i] += 1
                    self.addrarray[i] *= -1
#  CB - conditional branch
            elif (1440 <= self.opcodes[i] <= 1447 or
                  1448 <= self.opcodes[i] <= 1455):
                self.rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                self.offsarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x7FFFF
                if self.offsarray[i] >> 18 > 0:
                    self.offsarray[i] ^= 0x7FFFF
                    self.offsarray[i] += 1
                    self.offsarray[i] *= -1
                self.instructionformat[i] = 'CB'
                if 1440 <= self.opcodes[i] <= 1447:
                    self.instructions[i] = 'CBZ'
                else:
                    self.instructions[i] = 'CBNZ'
# BR - data segment break
            elif self.opcodes[i] == 2038:
                self.instructionformat[i] = 'BR'
                self.datastartindex = i + 1
# for i in fullmachinecode[] end loop

# write the disassembled output file
# after return, self._[] retains info
        outfile = open(outfilename, 'w')
        memaddr = 92
        for i in range(len(fullmachinecode)):
            memaddr += 4
            outline = ""
# data segment
            if self.dataendindex is not None and i >= self.datastartindex:
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\t"
                if int(fullmachinecode[i], 2) >> 31 > 0:
                    fullmachinecode[i] = int(fullmachinecode[i], 2) ^ 0xFFFFFFFF
                    fullmachinecode[i] += 1
                    fullmachinecode[i] *= -1
                    outline += str(fullmachinecode[i])
                else:
                    outline += str(fullmachinecode[i])
# instruction format wasn't found
            elif self.instructionformat[i] is None:
                outline += "Instruction not recognized at address: " + str(memaddr) + "\t"
                self.instrdisplaystring[i] = "Could not determine opcode"
# nop
            elif self.instructionformat[i] == 'NOP':
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\t"
                self.instrdisplaystring[i] = "NOP"
# R - register (add/sub/ ... )
            elif self.instructionformat[i] == 'R':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:16] + " "
                outline += fullmachinecode[i][16:22] + " " + fullmachinecode[i][22:27] + " "
                outline += fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t"
                self.instrdisplaystring[i] = str(self.instructions[i]) + "\tR" + str(self.rdarray[i]) + ", R"
                self.instrdisplaystring[i] += str(self.rnarray[i]) + ", "
                if self.instructions[i] == 'LSL' or self.instructions[i] == 'LSR' or self.instructions[i] == 'ASR':
                    self.instrdisplaystring[i] += "#" + str(self.shamtarray[i])
                else:
                    self.instrdisplaystring[i] += "R" + str(self.rmarray[i])
# I - immediate
            elif self.instructionformat[i] == 'I':
                outline += fullmachinecode[i][0:10] + " " + fullmachinecode[i][10:22] + " "
                outline += fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32]
                outline += "\t" + str(memaddr) + "\t"
                self.instrdisplaystring[i] = self.instructions[i] + "\tR" + str(self.rdarray[i]) + ", R"
                self.instrdisplaystring[i] += str(self.rnarray[i]) + ", #" + str(self.immarray[i])
# D - data load or store
            elif self.instructionformat[i] == 'D':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:20] + " "
                outline += fullmachinecode[i][20:22] + " " + fullmachinecode[i][22:27] + " "
                outline += fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t"
                self.instrdisplaystring[i] = self.instructions[i] + "\tR" + str(self.rdarray[i]) + ", [R"
                self.instrdisplaystring[i] += str(self.rnarray[i]) + ", #" + str(self.addrarray[i]) + "]"
# IM - move immediate and movezk
            elif self.instructionformat[i] == 'IM':
                outline += fullmachinecode[i][0:9] + " " + fullmachinecode[i][9:11] + " "
                outline += fullmachinecode[i][11:27] + " " + fullmachinecode[i][27:32]
                outline += "\t" + str(memaddr) + "\t"
                self.instrdisplaystring[i] = self.instructions[i] + "\tR" + str(self.rdarray[i]) + ", "
                self.instrdisplaystring[i] += str(self.immarray[i]) + ", LSL " + str(self.shamtarray[i])
# B - branch
            elif self.instructionformat[i] == 'B':
                outline += fullmachinecode[i][0:6] + " " + fullmachinecode[i][6:32] + "\t"
                outline += str(memaddr) + "\t"
                self.instrdisplaystring[i] = "B\t#" + str(self.addrarray[i])
# CB - conditional branch
            elif self.instructionformat[i] == 'CB':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:27] + " "
                outline += fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t"
                self.instrdisplaystring[i] = self.instructions[i] + "\tR"
                self.instrdisplaystring[i] += str(self.rdarray[i]) + ", #" + str(self.offsarray[i])
# BR - data segment break
            elif self.instructionformat[i] == 'BR':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:11] + " "
                outline += fullmachinecode[i][11:16] + " " + fullmachinecode[i][16:21] + " "
                outline += fullmachinecode[i][21:26] + " " + fullmachinecode[i][26:32] + "\t" + str(memaddr)
                outline += "\t"
                self.instrdisplaystring[i] = "BREAK"
# write output line and restart loop until eof
            if self.datastartindex is None or i <= self.datastartindex:
                outline += self.instrdisplaystring[i]
            print >> outfile, outline

        self.datastartindex += 1
        outfile.close()
        return self

    def emulator(self):

        # set counters and empty registers
        cyclecounter = 0
        pccounter = 0
        registers = [0] * 32
        while self.instructionformat[pccounter] != 'BR':
            cyclecounter += 1
            outline = "====================\n"
            outline += "cycle: " + str(cyclecounter) + "\t" + str((pccounter * 4) + 96) + "\t"
            outline += self.instrdisplaystring[pccounter]
# flag for whether to update pc counter +1 or if branch is changing it
            takebranch = 0
# R -> rdarray[], rnarray[], (rmarray[] or shamtarray[])
            # TODO: Fix for the pos/neg mismatch for: or, eor, and
            #                if registers[self.rdarray[pccounter]] < 0 and registers[self.rnarray[pccounter]] < 0:
            #                    print "eor - they are both negative\n"
            #               elif registers[self.rdarray[pccounter]] < 0 or registers[self.rnarray[pccounter]] < 0:
            #                    print "eor - one is negative\n"
            #                else:
            #                    print "eor - both positive\n"
            if self.instructions[pccounter] == 'ADD':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]]\
                                                     + registers[self.rmarray[pccounter]]
            elif self.instructions[pccounter] == 'SUB':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]]\
                                                     - registers[self.rmarray[pccounter]]
            elif self.instructions[pccounter] == 'AND':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]]\
                                                     & registers[self.rmarray[pccounter]]
            elif self.instructions[pccounter] == 'ORR':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]]\
                                                     | registers[self.rmarray[pccounter]]
            elif self.instructions[pccounter] == 'EOR':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]]\
                                                     ^ registers[self.rmarray[pccounter]]
            elif self.instructions[pccounter] == 'LSL':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]] << self.shamtarray[pccounter]
            elif self.instructions[pccounter] == 'LSR':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]] >> self.shamtarray[pccounter]
            elif self.instructions[pccounter] == 'ASR':
                if registers[self.rdarray[pccounter]] < 0:
                    registers[self.rdarray[pccounter]] =\
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> self.shamtarray[pccounter]
                    registers[self.rdarray[pccounter]] +=\
                        registers[self.rnarray[pccounter]] >> self.shamtarray[pccounter]
                else:
                    registers[self.rdarray[pccounter]] =\
                        registers[self.rnarray[pccounter]] >> self.shamtarray[pccounter]
# I-> rdarray[], rnarray[], immarray[]
            elif self.instructions[pccounter] == 'ADDI':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]] + self.immarray[pccounter]
            elif self.instructions[pccounter] == 'SUBI':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]] - self.immarray[pccounter]
# D-> rdarray[], rnarray[], addrarray[]
            elif self.instructions[pccounter] == 'LDUR':
                jumpaddress = registers[self.rnarray[pccounter]] + self.addrarray[pccounter]
                if jumpaddress in self.datasegment:
                    registers[self.rdarray[pccounter]] = self.datasegment[jumpaddress]
                else:
                    registers[self.rdarray[pccounter]] = 0
            elif self.instructions[pccounter] == 'STUR':
                jumpaddress = registers[self.rnarray[pccounter]] + self.addrarray[pccounter]
                self.datasegment[jumpaddress] = registers[self.rdarray[pccounter]]
                if jumpaddress > self.dataendindex:
                    self.dataendindex = jumpaddress
# IM-> rdarray[], immarray[], shamtarray[]
            elif self.instructions[pccounter] == 'MOVZ':
                registers[self.rdarray[pccounter]] = self.immarray[pccounter] << self.shamtarray[pccounter]
            elif self.instructions[pccounter] == 'MOVK':
                keepvalue = 0
                if self.shamtarray[pccounter] == 0:
                    keepvalue = registers[self.rdarray[pccounter]] & 0xFFFFFFFFFFFF0000
                elif self.shamtarray[pccounter] == 16:
                    keepvalue = registers[self.rdarray[pccounter]] & 0xFFFFFFFF0000FFFF
                elif self.shamtarray[pccounter] == 32:
                    keepvalue = registers[self.rdarray[pccounter]] & 0xFFFF0000FFFFFFFF
                elif self.shamtarray[pccounter] == 48:
                    keepvalue = registers[self.rdarray[pccounter]] & 0x0000FFFFFFFFFFFF
                keepvalue += self.immarray[pccounter] << self.shamtarray[pccounter]
                registers[self.rdarray[pccounter]] = keepvalue
# B-> addrarray[]
            elif self.instructions[pccounter] == 'B':
                pccounter += self.addrarray[pccounter]
                takebranch = 1
# CB-> rdarray[], offsarray[]
            elif self.instructions[pccounter] == 'CBZ' and registers[self.rdarray[pccounter]] == 0:
                pccounter += self.offsarray[pccounter]
                takebranch = 1
            elif self.instructions[pccounter] == 'CBNZ' and registers[self.rdarray[pccounter]] != 0:
                pccounter += self.offsarray[pccounter]
                takebranch = 1
            if not takebranch:
                pccounter += 1
# gather register info
            outline += "\n\nregisters:\nr00:\t" + str(registers[0]) + "\t" + str(registers[1]) + "\t"
            outline += str(registers[2]) + "\t" + str(registers[3]) + "\t" + str(registers[4]) + "\t"
            outline += str(registers[5]) + "\t" + str(registers[6]) + "\t" + str(registers[7]) + "\n"
            outline += "r08:\t" + str(registers[8]) + "\t" + str(registers[9]) + "\t"
            outline += str(registers[10]) + "\t" + str(registers[11]) + "\t" + str(registers[12]) + "\t"
            outline += str(registers[13]) + "\t" + str(registers[14]) + "\t" + str(registers[15]) + "\n"
            outline += "r16:\t" + str(registers[16]) + "\t" + str(registers[17]) + "\t"
            outline += str(registers[18]) + "\t" + str(registers[19]) + "\t" + str(registers[20]) + "\t"
            outline += str(registers[21]) + "\t" + str(registers[22]) + "\t" + str(registers[23]) + "\n"
            outline += "r24:\t" + str(registers[24]) + "\t" + str(registers[25]) + "\t"
            outline += str(registers[26]) + "\t" + str(registers[27]) + "\t" + str(registers[28]) + "\t"
            outline += str(registers[29]) + "\t" + str(registers[30]) + "\t" + str(registers[31]) + "\n\n"
# add data, if exists
            if self.dataendindex is not None:
                outline += "data:\n"
                datacounter = (self.datastartindex * 4) + 96
                while datacounter <= self.dataendindex:
                    outline += str(datacounter) + ": "
                    donewline = 0
                    while donewline <= 32:
                        if donewline:
                            outline += "\t"
                        if (datacounter+donewline) in self.datasegment:
                            outline += str(self.datasegment[datacounter+donewline])
                        else:
                            outline += "0"
                        donewline += 4
                    datacounter += 32
                    outline += "\n"
# end row, print
            print outline


#  function called when script ran from command line and acts as a disassembler for machine code
#  then iterates through machine code producing output stepping through the disassembly
#  ran in the form: $ python team1_project1.py -i test3_bin.txt -o team1_out_dis.txt
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
    decompiled = Decompiler()
    decompiled.run(inputFileName, outputFileName)
    decompiled.emulator()



