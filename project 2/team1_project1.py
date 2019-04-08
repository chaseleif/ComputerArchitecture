#!/usr/bin/python
#  team1_project1.py
#  Chase Phelps and Trenton Hohle
#  clp186           tah138
#  part one: this converts some machine code into LEGv8 asm
#  part two: this then emulates step-through execution, printing info

import sys


class Emulator:

    def __init__(self):
        pass

    @staticmethod
    def run(asm):
        # set counters and empty registers
        cyclecounter = 0
        pccounter = 0
        registers = [0] * 32

        outfile = open(asm.outfileprefix + "_sim.txt", 'w')

        while asm.instructionformat[pccounter] != 'BR':
            cyclecounter += 1
            outline = "====================\n"
            outline += "cycle: " + str(cyclecounter) + "\t" + str((pccounter * 4) + 96) + "\t"
            outline += asm.instrdisplaystring[pccounter]
            # flag for whether to update pc counter +1 or if branch is changing it
            takebranch = 0
            # R -> rdarray[], rnarray[], (rmarray[] or shamtarray[])
            if asm.instructions[pccounter] == 'ADD':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
                                                     + registers[asm.rmarray[pccounter]]
            elif asm.instructions[pccounter] == 'SUB':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
                                                     - registers[asm.rmarray[pccounter]]
            elif asm.instructions[pccounter] == 'AND':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
                                                     & registers[asm.rmarray[pccounter]]
            elif asm.instructions[pccounter] == 'ORR':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
                                                     | registers[asm.rmarray[pccounter]]
            elif asm.instructions[pccounter] == 'EOR':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
                                                     ^ registers[asm.rmarray[pccounter]]
            elif asm.instructions[pccounter] == 'LSL':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] << asm.shamtarray[
                    pccounter]
            elif asm.instructions[pccounter] == 'LSR':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] >> asm.shamtarray[
                    pccounter]
            elif asm.instructions[pccounter] == 'ASR':
                if registers[asm.rdarray[pccounter]] < 0:
                    registers[asm.rdarray[pccounter]] = \
                        0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> asm.shamtarray[pccounter]
                    registers[asm.rdarray[pccounter]] += \
                        registers[asm.rnarray[pccounter]] >> asm.shamtarray[pccounter]
                else:
                    registers[asm.rdarray[pccounter]] = \
                        registers[asm.rnarray[pccounter]] >> asm.shamtarray[pccounter]
            # I-> rdarray[], rnarray[], immarray[]
            elif asm.instructions[pccounter] == 'ADDI':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] + asm.immarray[pccounter]
            elif asm.instructions[pccounter] == 'SUBI':
                registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] - asm.immarray[pccounter]
            # D-> rdarray[], rnarray[], addrarray[]
            elif asm.instructions[pccounter] == 'LDUR':
                jumpaddress = registers[asm.rnarray[pccounter]] + (asm.addrarray[pccounter] * 4)
                if jumpaddress in asm.datasegment:
                    registers[asm.rdarray[pccounter]] = asm.datasegment[jumpaddress]
                else:
                    registers[asm.rdarray[pccounter]] = 0
            elif asm.instructions[pccounter] == 'STUR':
                jumpaddress = registers[asm.rnarray[pccounter]] + (asm.addrarray[pccounter] * 4)
                asm.datasegment[jumpaddress] = registers[asm.rdarray[pccounter]]
                if jumpaddress > asm.dataendindex:
                    asm.dataendindex = jumpaddress
            # IM-> rdarray[], immarray[], shamtarray[]
            elif asm.instructions[pccounter] == 'MOVZ':
                registers[asm.rdarray[pccounter]] = asm.immarray[pccounter] << asm.shamtarray[pccounter]
            elif asm.instructions[pccounter] == 'MOVK':
                keepvalue = 0
                if asm.shamtarray[pccounter] == 0:
                    keepvalue = registers[asm.rdarray[pccounter]] & 0xFFFFFFFFFFFF0000
                elif asm.shamtarray[pccounter] == 16:
                    keepvalue = registers[asm.rdarray[pccounter]] & 0xFFFFFFFF0000FFFF
                elif asm.shamtarray[pccounter] == 32:
                    keepvalue = registers[asm.rdarray[pccounter]] & 0xFFFF0000FFFFFFFF
                elif asm.shamtarray[pccounter] == 48:
                    keepvalue = registers[asm.rdarray[pccounter]] & 0x0000FFFFFFFFFFFF
                keepvalue += asm.immarray[pccounter] << asm.shamtarray[pccounter]
                registers[asm.rdarray[pccounter]] = keepvalue
            # B-> addrarray[]
            elif asm.instructions[pccounter] == 'B':
                pccounter += asm.addrarray[pccounter]
                takebranch = 1
            # CB-> rdarray[], offsarray[]
            elif asm.instructions[pccounter] == 'CBZ' and registers[asm.rdarray[pccounter]] == 0:
                pccounter += asm.offsarray[pccounter]
                takebranch = 1
            elif asm.instructions[pccounter] == 'CBNZ' and registers[asm.rdarray[pccounter]] != 0:
                pccounter += asm.offsarray[pccounter]
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
            if asm.dataendindex is not None:
                outline += "data:\n"
                datacounter = (asm.datastartindex * 4) + 96
                while datacounter <= asm.dataendindex:
                    outline += str(datacounter) + ": "
                    donewline = 0
                    while donewline <= 32:
                        if donewline:
                            outline += "\t"
                        if (datacounter + donewline) in asm.datasegment:
                            outline += str(asm.datasegment[datacounter + donewline])
                        else:
                            outline += "0"
                        donewline += 4
                    datacounter += 32
                    outline += "\n"
            # end row, print
            print >> outfile, outline
        outfile.close()



class Decompiler:

    def __init__(self):
        self.outfileprefix = None
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
        self.outfileprefix = outfilename
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
                self.dataendindex = (i * 4) + 96
                self.datasegment[self.dataendindex] = fullmachinecode[i]
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
            if self.datastartindex is None or i < self.datastartindex:
                outline += self.instrdisplaystring[i]
            print >> outfile, outline

        outfile.close()
        return self


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
    Emulator.run(decompiled)



