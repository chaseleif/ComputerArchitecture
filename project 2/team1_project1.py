#!/usr/bin/python
#  team1_project1.py
#  Chase Phelps and Trenton Hohle
#  clp186           tah138
#  this converts some machine code into LEGv8 asm

import sys


class Decompiler:

    def __init__(self):
        self.fullmachinecode = [None]
        self.opcodes = [None]
        self.instructionformat = [None]
        self.instructions = [None]
        self.rdarray = [None]
        self.rnarray = [None]
        self.rmarray = [None]
        self.shamtarray = [None]
        self.immarray = [None]
        self.addrarray = [None]
        self.offsarray = [None]
        self.datastartindex = None

    def run(self, infilename, outfilename):
        if infilename is None or outfilename is None:
            return
        outfilename += "_dis.txt"
        self.fullmachinecode = [line.rstrip() for line in open(infilename, 'rb')]

        self.datastartindex = None
        self.opcodes = [None] * len(self.fullmachinecode)
        self.instructionformat = [None] * len(self.fullmachinecode)
        self.instructions = [None] * len(self.fullmachinecode)
        self.rdarray = [None] * len(self.fullmachinecode)
        self.rnarray = [None] * len(self.fullmachinecode)
        self.rmarray = [None] * len(self.fullmachinecode)
        self.shamtarray = [None] * len(self.fullmachinecode)
        self.immarray = [None] * len(self.fullmachinecode)
        self.addrarray = [None] * len(self.fullmachinecode)
        self.offsarray = [None] * len(self.fullmachinecode)

        for i in range(len(self.fullmachinecode)):

            self.opcodes[i] = int(self.fullmachinecode[i], 2)
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
                self.rdarray[i] = int(self.fullmachinecode[i], 2) & 0x1F
                self.rnarray[i] = (int(self.fullmachinecode[i], 2) >> 5) & 0x1F
                if 1690 <= self.opcodes[i] <= 1691:
                    self.shamtarray[i] = (int(self.fullmachinecode[i], 2) >> 10) & 0x3F
                    if self.opcodes[i] == 1690:
                        self.instructions[i] = 'LSR'
                    elif self.opcodes[i] == 1692:
                        self.instructions[i] = 'ASR'
                    else:
                        self.instructions[i] = 'LSL'
                else:
                    self.rmarray[i] = (int(self.fullmachinecode[i], 2) >> 16) & 0x1F
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
# I - immediate
            elif (1160 <= self.opcodes[i] <= 1161 or
                  1672 <= self.opcodes[i] <= 1673):
                self.instructionformat[i] = 'I'
                self.rdarray[i] = int(self.fullmachinecode[i], 2) & 0x1F
                self.rnarray[i] = (int(self.fullmachinecode[i], 2) >> 5) & 0x1F
                self.immarray[i] = (int(self.fullmachinecode[i], 2) >> 10) & 0xFFF
                if self.immarray[i] >> 11 > 0:
                    self.immarray[i] ^= 0xFFF
                    self.immarray[i] += 1
                    self.immarray[i] *= -1
                if 1160 <= self.opcodes[i] <= 1161:
                    self.instructions[i] = 'ADDI'
                else:
                    self.instructions[i] = 'SUBI'
# D - data load / store
            elif self.opcodes[i] == 1986 or self.opcodes[i] == 1984:
                self.instructionformat[i] = 'D'
                self.rdarray[i] = int(self.fullmachinecode[i], 2) & 0x1F
                self.rnarray[i] = (int(self.fullmachinecode[i], 2) >> 5) & 0x1F
                self.addrarray[i] = (int(self.fullmachinecode[i], 2) >> 12) & 0x1FF
                if self.addrarray[i] >> 8 > 0:
                    self.addrarray[i] ^= 0x1FF
                    self.addrarray[i] += 1
                    self.addrarray[i] *= -1
                if self.opcodes[i] == 1986:
                    self.instructions[i] = 'LDUR'
                else:
                    self.instructions[i] = 'STUR'
# IM - move immediate / multiple
            elif (1684 <= self.opcodes[i] <= 1687 or
                  1940 <= self.opcodes[i] <= 1943):
                self.instructionformat[i] = 'IM'
                self.rdarray[i] = int(self.fullmachinecode[i], 2) & 0x1F
                self.shamtarray[i] = ((int(self.fullmachinecode[i], 2) >> 21) & 0x3) << 4
                self.immarray[i] = (int(self.fullmachinecode[i], 2) >> 5) & 0xFFFF
                if 1684 <= self.opcodes[i] <= 1687:
                    self.instructions[i] = 'MOVZ'
                else:
                    self.instructions[i] = 'MOVK'
# B - this is the branch instruction
            elif 160 <= self.opcodes[i] <= 191:
                self.instructionformat[i] = 'B'
                self.instructions[i] = 'B'
                self.addrarray[i] = int(self.fullmachinecode[i], 2) & 0x3FFFFFF
                if self.addrarray[i] >> 25 > 0:
                    self.addrarray[i] ^= 0x3FFFFFF
                    self.addrarray[i] += 1
                    self.addrarray[i] *= -1
#  CB - conditional branch
            elif (1440 <= self.opcodes[i] <= 1447 or
                  1448 <= self.opcodes[i] <= 1455):
                self.rdarray[i] = int(self.fullmachinecode[i], 2) & 0x1F
                self.offsarray[i] = (int(self.fullmachinecode[i], 2) >> 5) & 0x7FFFF
                if self.offsarray[i] >> 18 > 0:
                    self.offsarray[i] ^= 0x7FFFF
                    self.offsarray[i] += 1
                    self.offsarray[i] *= -1
                self.instructionformat[i] = 'CB'
                if 1440 <= self.opcodes[i] <= 1447:
                    self.instructions[i] = 'CBZ'
                else:
                    self.instructions[i] = 'CBNZ'
# BR - this is the data segment break
            elif self.opcodes[i] == 2038:
                self.instructionformat[i] = 'BR'
                self.datastartindex = i
                break
# for i in self.fullmachinecode[] end loop

#  now write the output file

        outfile = open(outfilename, 'w')
        memaddr = 92
        for i in range(len(self.fullmachinecode)):
            memaddr += 4
            outline = ""
# data segment
            if self.datastartindex is not None and i > self.datastartindex:
                outline += self.fullmachinecode[i] + "\t" + str(memaddr) + "\t"
                if int(self.fullmachinecode[i], 2) >> 31 > 0:
                    self.fullmachinecode[i] = int(self.fullmachinecode[i], 2) ^ 0xFFFFFFFF
                    self.fullmachinecode[i] += 1
                    self.fullmachinecode[i] *= -1
                    outline += str(self.fullmachinecode[i])
                else:
                    outline += str(self.fullmachinecode[i])
# instruction format not set
            elif self.instructionformat[i] is None:
                outline += "Instruction not recognized at address: " + str(memaddr)
# NOP - nop
            elif self.instructionformat[i] == 'NOP':
                outline += self.fullmachinecode[i] + "\t" + str(memaddr) + "\tNOP"
# R - register
            elif self.instructionformat[i] == 'R':
                outline += self.fullmachinecode[i][0:11] + " " + self.fullmachinecode[i][11:16] + " "
                outline += self.fullmachinecode[i][16:22] + " " + self.fullmachinecode[i][22:27] + " "
                outline += self.fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t" + str(self.instructions[i])
                outline += "\tR" + str(self.rdarray[i]) + ", R" + str(self.rnarray[i]) + ", "
                if self.instructions[i] == 'LSL' or self.instructions[i] == 'LSR' or self.instructions[i] == 'ASR':
                    outline += "#" + str(self.shamtarray[i])
                else:
                    outline += "R" + str(self.rmarray[i])
# I - immediate
            elif self.instructionformat[i] == 'I':
                outline += self.fullmachinecode[i][0:10] + " " + self.fullmachinecode[i][10:22] + " "
                outline += self.fullmachinecode[i][22:27] + " " + self.fullmachinecode[i][27:32] + "\t" + str(memaddr)
                outline += "\t" + self.instructions[i] + "\tR" + str(self.rdarray[i]) + ", R" + str(self.rnarray[i])
                outline += ", #" + str(self.immarray[i])
# D - data load / store
            elif self.instructionformat[i] == 'D':
                outline += self.fullmachinecode[i][0:11] + " " + self.fullmachinecode[i][11:20] + " "
                outline += self.fullmachinecode[i][20:22] + " " + self.fullmachinecode[i][22:27] + " "
                outline += self.fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t" + self.instructions[i] + "\tR"
                outline += str(self.rdarray[i]) + ", [R" + str(self.rnarray[i]) + ", #" + str(self.addrarray[i]) + "]"
# IM - move immediate / multiple
            elif self.instructionformat[i] == 'IM':
                outline += self.fullmachinecode[i][0:9] + " " + self.fullmachinecode[i][9:11] + " "
                outline += self.fullmachinecode[i][11:27] + " " + self.fullmachinecode[i][27:32] + "\t" + str(memaddr)
                outline += "\t" + self.instructions[i] + "\tR" + str(self.rdarray[i]) + ", " + str(self.immarray[i])
                outline += ", LSL " + str(self.shamtarray[i])
# B - this is the branch instruction
            elif self.instructionformat[i] == 'B':
                outline += self.fullmachinecode[i][0:6] + " " + self.fullmachinecode[i][6:32] + "\t"
                outline += str(memaddr) + "\tB\t#" + str(self.addrarray[i])
# CB - conditional branch
            elif self.instructionformat[i] == 'CB':
                outline += self.fullmachinecode[i][0:8] + " " + self.fullmachinecode[i][8:27] + " "
                outline += self.fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t" + self.instructions[i] + "\tR"
                outline += str(self.rdarray[i]) + ", #" + str(self.offsarray[i])
# BR - this is the data segment break
            elif self.instructionformat[i] == 'BR':
                outline += self.fullmachinecode[i][0:8] + " " + self.fullmachinecode[i][8:11] + " "
                outline += self.fullmachinecode[i][11:16] + " " + self.fullmachinecode[i][16:21] + " "
                outline += self.fullmachinecode[i][21:26] + " " + self.fullmachinecode[i][26:32] + "\t" + str(memaddr)
                outline += "\tBREAK"
# write output line and restart loop if more lines to process
            print >> outfile, outline
# for i in self.fullmachinecode[] end loop

        outfile.close()
        return self

    def emulator(self):

        datasegment = {}
        dataendindex = -1
        for i in range(self.datastartindex + 1, len(self.fullmachinecode)):
            datasegment[(i*4)+96] = self.fullmachinecode[i]
            dataendindex = (i*4)+96

        cyclecounter = 0
        pccounter = 0
        registers = [0] * 32
        while self.instructionformat[pccounter] != 'BR':
            cyclecounter += 1

            outline = "cycle: " + str(cyclecounter) + "\t" + str((pccounter * 4) + 96) + "\t"
            if self.instructionformat[pccounter] == 'NOP':
                outline += "NOP"
            elif self.instructionformat[pccounter] == 'R':
                outline += str(self.instructions[pccounter]) + "\tR" + str(self.rdarray[pccounter])
                outline += ", R" + str(self.rnarray[pccounter]) + ", "
                if self.instructions[pccounter] == 'LSL' or self.instructions[pccounter] == 'LSR'\
                        or self.instructions[pccounter] == 'ASR':
                    outline += "#" + str(self.shamtarray[pccounter])
                else:
                    outline += "R" + str(self.rmarray[pccounter])
            elif self.instructionformat[pccounter] == 'I':
                outline += self.instructions[pccounter] + "\tR" + str(self.rdarray[pccounter])
                outline += ", R" + str(self.rnarray[pccounter]) + ", #" + str(self.immarray[pccounter])
            elif self.instructionformat[pccounter] == 'D':
                outline += self.instructions[pccounter] + "\tR" + str(self.rdarray[pccounter])
                outline += ", [R" + str(self.rnarray[pccounter]) + ", #" + str(self.addrarray[pccounter]) + "]"
            elif self.instructionformat[pccounter] == 'IM':
                outline += self.instructions[pccounter] + "\tR" + str(self.rdarray[pccounter]) + ", "
                outline += str(self.immarray[pccounter]) + ", LSL " + str(self.shamtarray[pccounter])
            elif self.instructionformat[pccounter] == 'B':
                outline += "B\t#" + str(self.addrarray[pccounter])
            elif self.instructionformat[pccounter] == 'CB':
                outline += self.instructions[pccounter] + "\tR" + str(self.rdarray[pccounter]) + ", #"
                outline += str(self.offsarray[pccounter])
            elif self.instructionformat[pccounter] == 'BR':
                outline += "BREAK"
# flag for whether to update pc counter +1 or if branch is changing it
            takebranch = 0
# R -> instructions[] rdarray[] rnarray[] { rmarray[] or shamtarray[] }
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
                registers[self.rdarray[pccounter]] = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> self.shamtarray[pccounter]
                registers[self.rdarray[pccounter]] += registers[self.rnarray[pccounter]] >> self.shamtarray[pccounter]
# I-> instructions[] rdarray[] rnarray[] immarray[]
            elif self.instructions[pccounter] == 'ADDI':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]] + self.immarray[pccounter]
            elif self.instructions[pccounter] == 'SUBI':
                registers[self.rdarray[pccounter]] = registers[self.rnarray[pccounter]] - self.immarray[pccounter]
# D-> instructions[] rdarray[] rnarray[] addrarray[]
            elif self.instructions[pccounter] == 'LDUR':
                jumpaddress = registers[self.rnarray[pccounter]] + self.addrarray[pccounter]
                if jumpaddress in datasegment:
                    registers[self.rdarray[pccounter]] = datasegment[jumpaddress]
                else:
                    registers[self.rdarray[pccounter]] = 0
            elif self.instructions[pccounter] == 'STUR':
                jumpaddress = registers[self.rnarray[pccounter]] + self.addrarray[pccounter]
                datasegment[jumpaddress] = registers[self.rdarray[pccounter]]
                if jumpaddress > dataendindex:
                    dataendindex = jumpaddress
# IM-> instructions[] rdarray[] immarray[] shamtarray[]
            elif self.instructions[pccounter] == 'MOVZ':
                registers[self.rdarray[pccounter]] = self.immarray[pccounter] << self.shamtarray[pccounter]
            elif self.instructions[pccounter] == 'MOVK':
                keepvalue = 0
                print "The shamt is " + str(self.shamtarray[pccounter])
                if self.shamtarray[pccounter] == 0:
                    keepvalue = registers[self.rdarray[pccounter]] & 0xFFFFFFFFFFFF0000
                elif self.shamtarray[pccounter] == 16:
                    keepvalue = registers[self.rdarray[pccounter]] & 0xFFFFFFFF0000FFFF
                elif self.shamtarray[pccounter] == 32:
                    keepvalue = registers[self.rdarray[pccounter]] & 0xFFFF0000FFFFFFFF
                elif self.shamtarray[pccounter] == 48:
                    keepvalue = registers[self.rdarray[pccounter]] & 0x0000FFFFFFFFFFFF
                print "The keep is " + str(keepvalue)
                keepvalue += self.immarray[pccounter] << self.shamtarray[pccounter]
                print "The keep is now " + str(keepvalue)
                registers[self.rdarray[pccounter]] = keepvalue
# B-> addrarray[]
            elif self.instructions[pccounter] == 'B':
                pccounter += self.addrarray[pccounter]
                takebranch = 1
#CB-> rdarray[] offsarray[]
            elif self.instructions[pccounter] == 'CBZ' and registers[self.rdarray[pccounter]] == 0:
                pccounter += self.offsarray[pccounter]
                takebranch = 1
            elif self.instructions[pccounter] == 'CBNZ' and registers[self.rdarray[pccounter]] != 0:
                pccounter += self.offsarray[pccounter]
                takebranch = 1
            if not takebranch:
                pccounter += 1
            print "===================="
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
            if dataendindex > 0:
                outline += "data:\n"
                datacounter = ((self.datastartindex+1) * 4) + 96
                while datacounter <= dataendindex:
                    outline += str(datacounter) + ": "
                    donewline = 0
                    while donewline <= 32:
                        if (datacounter+donewline) in datasegment:
                            outline += str(datasegment[datacounter+donewline]) + "\t"
                        else:
                            outline += "0\t"
                        donewline += 4
                    datacounter += 32
                    outline += "\n"
            print outline

#  function called when script ran from command line and acts as a disassembler for machine code
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



