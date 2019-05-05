#!/usr/bin/python
#  team1_project2.py
#  Chase Phelps and Trenton Hohle
#  clp186           tah138
#  part one: this converts some machine code into LEGv8 asm
#  part two: this then emulates step-through execution, printing info
#  part three: emulator from part two essentially removed, now simulates a pipeline
#   because we are now fetching from memory, decoding instructions, and all within the pipeline ...
#   previous decoded information from disassembler is thrown away
#   the asm class is still kept, it now fills out the data{} of the binary file read, keyed by memory address
#   the asm class also saves the file prefix (from command line) for output, and the initial data start /end addresses

import sys


# This is the Instruction fetch unit
class IF:
    def __init__(self, dacache, preissuebuffa, registerfile, programcounter):
        self.cache = dacache
        self.preissue = preissuebuffa
        self.registers = registerfile
        self.pc = programcounter

    def run(self):
        self.pc += 4


# This is the Issue unit, can issue up to two instructions (which may be out of order) to pre-mem / pre-alu
# Instructions issued if room in pre-mem and pre-alu and no hazards exist
# Stall one cycle:
# Read After Write:     R1 = R2+R3 *** writing to R1, can't use R1 for 2 cycles ***
#                       R4 = R1+R3 *** R1 will be available at beginning of second cycle
# Write After Read:     R1 = R2+R3 *** does not cause an issue with design ***
#                       R3 = R2+R4
# Write After Write:    R1 = R2+R3 ** kind of redundant ... ***
#                       R1 = R3+R4
# A load must wait for stores to be issued
# Store instructions must be executed in order
# preissue [operation, left, right, destination] * 4
# prealu = [operation, left, right, destination] * 2
# premem = [load/store, address, value] * 2
class Issue:
    def __init__(self, preissuebuffa, premembuffa, prealubuffa, registerfile):
        self.preissue = preissuebuffa
        self.premem = premembuffa
        self.prealu = prealubuffa
        self.registers = registerfile
        self.waitlist = {}

    def run(self):
        for register in self.waitlist:
            register.waitval -= 1
            if register.waitval is 0:
                del register
        issuedinstructions = 0
        for i in range(0,3):
            if self.preissue[i][0] is not 0:
                self.prealu[0][0] = self.preissue[i][0]
                self.prealu[0][1] = self.preissue[i][1]
                self.prealu[0][2] = self.preissue[i][2]
                self.prealu[0][3] = self.preissue[i][3]


# This is the MEM unit, only handles LDUR and STUR instructions, (LOAD and STORE)
# Result will equal None if the cache misses, then just ignore and this will reattempt next cycle
# premem = [load/store, address, value] * 2
# postmem = [destination, value]
class MEM:
    def __init__(self, premembuffa, postmembuffa, dacache):
        self.premem = premembuffa
        self.postmem = postmembuffa
        self.cache = dacache

    def run(self):
        if self.premem[0][0] is not 0:
            if self.premem[0][0] is 'LOAD':
                result = self.cache.fetch(self.premem[0][1])
                if result is not None:
                    self.postmem[0] = self.premem[0][1]
                    self.postmem[1] = result
                    del self.premem[0]
                    self.premem.append([0, 0, 0])
            # store
            else:
                result = self.cache.store(self.premem[0][1], self.premem[0][2])
                if result is not None:
                    del self.premem[0]
                    self.premem.append([0, 0, 0])


# This is the ALU unit
# prealu is list: [operation, left, right, destination] * 2
# postalu is list: [destination, value]
class ALU:
    def __init__(self, prealubuffa, postalubuffa):
        self.prealu = prealubuffa
        self.postalu = postalubuffa

    def run(self):
        if self.prealu[0][0] is not 0:
            result = self.prealu[0][1]
            # ADD or ADDI
            if self.prealu[0][0] is '+':
                result += self.prealu[0][2]
            # SUB OR SUBI
            elif self.prealu[0][0] is '-':
                result -= self.prealu[0][2]
            # AND
            elif self.prealu[0][0] is '&':
                result &= self.prealu[0][2]
            # ORR
            elif self.prealu[0][0] is '|':
                result /= self.prealu[0][2]
            # EOR
            elif self.prealu[0][0] is '^':
                result ^= self.prealu[0][2]
            # LSL
            elif self.prealu[0][0] is 'LSL':
                result <<= self.prealu[0][2]
            # LSR
            elif self.prealu[0][0] is 'LSR':
                result >>= self.prealu[0][2]
            elif self.prealu[0][0] is 'ASR':
                result >>= self.prealu[0][2]
                if result < 0:
                    result += (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> self.prealu[0][2])
            self.postalu[0] = self.prealu[0][3]
            self.postalu[1] = result
            del self.prealu[0]
            self.prealu.append([0, 0, 0, 0])


# This is the Write-Back unit
# postalu is list: [destination, value]
# postmem is list: [destination, value]
class WB:
    def __init__(self, postmembuffa, postalubuffa, registerfile):
        self.postmem = postmembuffa
        self.postalu = postalubuffa
        self.registers = registerfile

    def run(self):
        if self.postmem[0] is not 0:
            self.registers[self.postmem[0]] = self.postmem[1]
            self.postmem[0] = 0
            self.postmem[1] = 0
        if self.postalu[0] is not 0:
            self.registers[self.postalu[0]] = self.postalu[1]
            self.postalu[0] = 0
            self.postalu[1] = 0


# CacheLine, actually a half of a line, one element of the Cache's [[]] 4x2 (either first/second word of a line)
class CacheLine:
    def __init__(self, tagbits, wordbits, validbit=1):
        self.valid = validbit
        self.dirty = 0
        self.tag = tagbits
        self.word = wordbits


# This is the Cache, run() is for cycle start, run() will fetch data from memory if there was a cache miss
# Attempts to fetch or store when not in cache will return None ... run() will populate the data next cycle
# fetch() will return a value and store() will return 1 upon success
# fetchnext used for cache miss, full used until cache initially filled
# datastart could be used to ensure not writing to text segment. dataend keeps track of end of data
class Cache:
    def __init__(self, datasegment, datastarti, dataendi):
        self.disk = datasegment
        self.datastart = datastarti
        self.dataend = dataendi
        self.cache = [[CacheLine(0, 0, 0)], [CacheLine(0, 0, 0)]] * 4
        self.fetchnext = None
        self.full = 0

# called at the beginning of each cycle, the cache performs its read from disk for misses from last cycle
# self.fetchnext is set on a Cache miss (no success) from class fetch() and store() methods
    def run(self):
        if self.fetchnext is not None:
            # cache has not yet been filled
            if not self.full:
                for i in range(0, 4):
                    # this is the next spot in the cache
                    if not self.cache[i][0].valid:
                        self.cache[i][0].tag = self.fetchnext >> 3
                        self.cache[i][0].word = self.disk[self.fetchnext]
                        self.cache[i][1].word = self.disk[self.fetchnext+4]
                        self.cache[i][0].valid = 1
                        self.cache[i][1].valid = 1
                        if i == 3:
                            self.full = 1
            # cache has been initially filled, had a miss, remove oldest and append new item
            else:
                # oldest has been modified, must first write it
                if self.cache[0][0].dirty or self.cache[0][1].dirty:
                    writeaddy = self.cache[0][0].tag << 3
                    if self.cache[0][1].dirty:
                        self.disk[writeaddy + 4] = self.cache[0][1].word
                        if writeaddy + 4 > self.dataend:
                            self.dataend = writeaddy + 4
                    if self.cache[0][0].dirty:
                        self.disk[writeaddy] = self.cache[0][0].word
                        if writeaddy > self.dataend:
                            self.dataend = writeaddy
                # remove the oldest in the cache and append a new
                del self.cache[0]
                self.cache.append(CacheLine(self.fetchnext >> 3, self.disk[self.fetchnext]),
                                  CacheLine(self.fetchnext >> 3, self.disk[self.fetchnext+4]))
            self.fetchnext = None

# 96 = 1100000 ... 100 = 1100100
# fetch(address) returns data for specified address, or None for cache miss
    def fetch(self, addr):
        searchtag = addr >> 3
        for i in range(0, 4):
            if self.cache[i].tag is searchtag and self.cache[i][0].valid:
                # bubble the cache[i] up
                while i < 3:
                    # cache is not full, next entry is not yet valid so this is at the top of valid, break
                    if not self.cache[i+1][0].valid:
                        break
                    swap = self.cache[i+1]
                    self.cache[i+1] = self.cache[i]
                    self.cache[i] = swap
                    i += 1
                # i will either equal 3, or the last valid entry, anyway i is the index of the found searchtag
                # addr >> 2 anded with 1 reveals whether first or second word is desired
                if (addr >> 2) & 1 is 0:
                    return self.cache[i][0].word
                else:
                    return self.cache[i][1].word
        # didn't find it, we will fetch it next cycle, when self.run() is called (unless Cache busy)
        if self.fetchnext is None:
            self.fetchnext = addr
        return None

# accepts value and destination address. returns 1 for success, returns None for cache miss
    def store(self, toaddress, thevalue):
        writetag = toaddress >> 3
        for i in range(0, 4):
            if self.cache[i][0].tag is writetag and self.cache[i][0].valid:
                # if toaddress >= datastart, **NO EXCEPTION HANDLING**
                if (toaddress >> 2) & 1 is 0:
                    self.cache[i][0].word = thevalue
                else:
                    self.cache[i][1].word = thevalue
                return 1
        # trying to write to something not in the cache
        # must fetch data from memory and store request must be resubmitted next cycle (unless Cache busy)
        if self.fetchnext is None:
            self.fetchnext = toaddress
        return None


# This is essentially the control-unit for the pipeline simulation, holds all registers/buffers between pipe stages
# Cache.run() must be called at the beginning of every cycle to fetch cache misses
# cache misses caused by calls to Cache.fetch() and Cache.store() methods, called by MEM and IF classes
class Emulator:

    def __init__(self):
        pass

# input Decompiler asm has -> .outfileprefix .fullmachinecode[] .datastartindex .dataendindex = None
    @staticmethod
    def run(asm):
        # set counters, empty registers, and empty buffers
        registers = [0] * 32
        # preissue [operation, left, right, destination]
        preissue = [0, 0, 0] * 4
        # prealu [operation, left, right, destination]
        prealu = [0, 0, 0, 0] * 2
        # premem [load/store, address, value]
        premem = [0, 0, 0] * 2
        # postalu [destination, value]
        postalu = [0, 0]
        # postmem [destination, value]
        postmem = [0, 0]
        cyclecounter = 0
        pccounter = 96
        # initialize empty cache and functional units
        cache = Cache(asm.data, asm.datastartindex, asm.dataendindex)
        ifUnit = IF(cache, preissue, registers, pccounter)
        issueUnit = Issue(preissue, premem, prealu, registers)
        memUnit = MEM(premem, postmem, cache)
        aluUnit = ALU(prealu, postalu)
        wbUnit = WB(postmem, postalu, registers)

        outfile = open(asm.outfileprefix + "_pipeline.txt", 'w')

        # while True:
        #       cache.run()
        #
        #
        #     cyclecounter += 1
        #     outline = "--------------------\n"
        #     outline += "Cycle: " + str(cyclecounter) + "\n"
            # flag for whether to update pc counter +1 or if branch is changing it
        #     takebranch = 0
        #     # R -> rdarray[], rnarray[], (rmarray[] or shamtarray[])
        #     if asm.instructions[pccounter] == 'ADD':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
        #                                              + registers[asm.rmarray[pccounter]]
        #     elif asm.instructions[pccounter] == 'SUB':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
        #                                              - registers[asm.rmarray[pccounter]]
        #     elif asm.instructions[pccounter] == 'AND':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
        #                                              & registers[asm.rmarray[pccounter]]
        #     elif asm.instructions[pccounter] == 'ORR':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
        #                                              | registers[asm.rmarray[pccounter]]
        #     elif asm.instructions[pccounter] == 'EOR':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] \
        #                                              ^ registers[asm.rmarray[pccounter]]
        #     elif asm.instructions[pccounter] == 'LSL':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] << asm.shamtarray[
        #             pccounter]
        #     elif asm.instructions[pccounter] == 'LSR':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] >> asm.shamtarray[
        #             pccounter]
        #     elif asm.instructions[pccounter] == 'ASR':
        #         if registers[asm.rnarray[pccounter]] < 0:
        #             registers[asm.rdarray[pccounter]] = \
        #                 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> asm.shamtarray[pccounter]
        #             registers[asm.rdarray[pccounter]] += \
        #                 registers[asm.rnarray[pccounter]] >> asm.shamtarray[pccounter]
        #         else:
        #             registers[asm.rdarray[pccounter]] = \
        #                 registers[asm.rnarray[pccounter]] >> asm.shamtarray[pccounter]
        #     # I-> rdarray[], rnarray[], immarray[]
        #     elif asm.instructions[pccounter] == 'ADDI':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] + asm.immarray[pccounter]
        #     elif asm.instructions[pccounter] == 'SUBI':
        #         registers[asm.rdarray[pccounter]] = registers[asm.rnarray[pccounter]] - asm.immarray[pccounter]
        #     # D-> rdarray[], rnarray[], addrarray[]
        #     elif asm.instructions[pccounter] == 'LDUR':
        #         jumpaddress = registers[asm.rnarray[pccounter]] + (asm.addrarray[pccounter] * 4)
        #         if jumpaddress in asm.datasegment:
        #             registers[asm.rdarray[pccounter]] = asm.datasegment[jumpaddress]
        #         else:
        #             registers[asm.rdarray[pccounter]] = 0
        #     elif asm.instructions[pccounter] == 'STUR':
        #         jumpaddress = registers[asm.rnarray[pccounter]] + (asm.addrarray[pccounter] * 4)
        #         asm.datasegment[jumpaddress] = registers[asm.rdarray[pccounter]]
        #         if jumpaddress > asm.dataendindex:
        #             asm.dataendindex = jumpaddress
        #     # IM-> rdarray[], immarray[], shamtarray[]
        #     elif asm.instructions[pccounter] == 'MOVZ':
        #         registers[asm.rdarray[pccounter]] = asm.immarray[pccounter] << asm.shamtarray[pccounter]
        #     elif asm.instructions[pccounter] == 'MOVK':
        #         keepvalue = 0
        #         if asm.shamtarray[pccounter] == 0:
        #             keepvalue = registers[asm.rdarray[pccounter]] & 0xFFFFFFFFFFFF0000
        #         elif asm.shamtarray[pccounter] == 16:
        #             keepvalue = registers[asm.rdarray[pccounter]] & 0xFFFFFFFF0000FFFF
        #         elif asm.shamtarray[pccounter] == 32:
        #             keepvalue = registers[asm.rdarray[pccounter]] & 0xFFFF0000FFFFFFFF
        #         elif asm.shamtarray[pccounter] == 48:
        #             keepvalue = registers[asm.rdarray[pccounter]] & 0x0000FFFFFFFFFFFF
        #         keepvalue += asm.immarray[pccounter] << asm.shamtarray[pccounter]
        #         registers[asm.rdarray[pccounter]] = keepvalue
        #     # B-> addrarray[]
        #     elif asm.instructions[pccounter] == 'B':
        #         pccounter += asm.addrarray[pccounter]
        #         takebranch = 1
        #     # CB-> rdarray[], offsarray[]
        #     elif asm.instructions[pccounter] == 'CBZ' and registers[asm.rdarray[pccounter]] == 0:
        #         pccounter += asm.offsarray[pccounter]
        #         takebranch = 1
        #     elif asm.instructions[pccounter] == 'CBNZ' and registers[asm.rdarray[pccounter]] != 0:
        #         pccounter += asm.offsarray[pccounter]
        #         takebranch = 1
        #     if not takebranch and asm.instructions[pccounter] != 'BR':
        #         pccounter += 1
        #     # gather register info
        #     outline += "\n\nregisters:\nr00:\t" + str(registers[0]) + "\t" + str(registers[1]) + "\t"
        #     outline += str(registers[2]) + "\t" + str(registers[3]) + "\t" + str(registers[4]) + "\t"
        #     outline += str(registers[5]) + "\t" + str(registers[6]) + "\t" + str(registers[7]) + "\n"
        #     outline += "r08:\t" + str(registers[8]) + "\t" + str(registers[9]) + "\t"
        #     outline += str(registers[10]) + "\t" + str(registers[11]) + "\t" + str(registers[12]) + "\t"
        #     outline += str(registers[13]) + "\t" + str(registers[14]) + "\t" + str(registers[15]) + "\n"
        #     outline += "r16:\t" + str(registers[16]) + "\t" + str(registers[17]) + "\t"
        #     outline += str(registers[18]) + "\t" + str(registers[19]) + "\t" + str(registers[20]) + "\t"
        #     outline += str(registers[21]) + "\t" + str(registers[22]) + "\t" + str(registers[23]) + "\n"
        #     outline += "r24:\t" + str(registers[24]) + "\t" + str(registers[25]) + "\t"
        #     outline += str(registers[26]) + "\t" + str(registers[27]) + "\t" + str(registers[28]) + "\t"
        #     outline += str(registers[29]) + "\t" + str(registers[30]) + "\t" + str(registers[31]) + "\n\n"
        #
        #     outline += "data:\n"
        #     # add data, if exists
        #     if asm.dataendindex is not None:
        #         datacounter = (asm.datastartindex * 4) + 96
        #         while datacounter <= asm.dataendindex:
        #             outline += str(datacounter) + ":"
        #             donewline = 0
        #             while donewline < 32 and (datacounter + donewline) <= asm.dataendindex:
        #                 outline += "\t"
        #                 if (datacounter + donewline) in asm.datasegment:
        #                     outline += str(int(asm.datasegment[datacounter + donewline]))
        #                 else:
        #                     outline += "0"
        #                 donewline += 4
        #             datacounter += 32
        #             outline += "\n"
        #         outline = outline[:-1]
        #     else:
        #         outline += "\n"
        #     # end row, print
        #     print >> outfile, outline
        #     if asm.instructionformat[pccounter-1] == 'BR':
        #         break
        # outfile.close()


class Decompiler:

    def __init__(self):
        self.outfileprefix = None
        self.datastartindex = None
        self.dataendindex = None
        self.data = {}

    def run(self, infilename, outfilename):
        if infilename is None or outfilename is None:
            return
        self.outfileprefix = outfilename
        outfilename += "_dis.txt"
        fullmachinecode = [line.rstrip() for line in open(infilename, 'rb')]

        self.datastartindex = None
        self.dataendindex = None
        opcodes = [None] * len(fullmachinecode)
        instructionformat = [None] * len(fullmachinecode)
        instructions = [None] * len(fullmachinecode)
        instrdisplaystring = [None] * len(fullmachinecode)
        rdarray = [None] * len(fullmachinecode)
        rnarray = [None] * len(fullmachinecode)
        rmarray = [None] * len(fullmachinecode)
        shamtarray = [None] * len(fullmachinecode)
        immarray = [None] * len(fullmachinecode)
        addrarray = [None] * len(fullmachinecode)
        offsarray = [None] * len(fullmachinecode)
        self.data = {}

        for i in range(len(fullmachinecode)):
# data
            if self.datastartindex is not None:
                self.dataendindex = (i * 4) + 96
                self.data[self.dataendindex] = fullmachinecode[i]
                continue
# text
            self.data[(i * 4) + 96] = fullmachinecode[i]
            opcodes[i] = int(fullmachinecode[i], 2)
            opcodes[i] >>= 21
# NOP - nop
            if opcodes[i] == 0:
                instructionformat[i] = 'NOP'
# R - register
            elif (opcodes[i] == 1112 or opcodes[i] == 1624 or
                  opcodes[i] == 1691 or opcodes[i] == 1690 or
                  opcodes[i] == 1692 or opcodes[i] == 1104 or
                  opcodes[i] == 1360 or opcodes[i] == 1872):
                instructionformat[i] = 'R'
                rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                rnarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x1F
                if 1690 <= opcodes[i] <= 1692:
                    shamtarray[i] = (int(fullmachinecode[i], 2) >> 10) & 0x3F
                    if opcodes[i] == 1690:
                        instructions[i] = 'LSR'
                    elif opcodes[i] == 1691:
                        instructions[i] = 'LSL'
                    elif opcodes[i] == 1692:
                        instructions[i] = 'ASR'
                else:
                    rmarray[i] = (int(fullmachinecode[i], 2) >> 16) & 0x1F
                    if opcodes[i] == 1104:
                        instructions[i] = 'AND'
                    elif opcodes[i] == 1112:
                        instructions[i] = 'ADD'
                    elif opcodes[i] == 1360:
                        instructions[i] = 'ORR'
                    elif opcodes[i] == 1624:
                        instructions[i] = 'SUB'
                    else:
                        instructions[i] = 'EOR'
# I - immediates
            elif (1160 <= opcodes[i] <= 1161 or
                  1672 <= opcodes[i] <= 1673):
                instructionformat[i] = 'I'
                rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                rnarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x1F
                immarray[i] = (int(fullmachinecode[i], 2) >> 10) & 0xFFF
                if immarray[i] >> 11 > 0:
                    immarray[i] ^= 0xFFF
                    immarray[i] += 1
                    immarray[i] *= -1
                if 1160 <= opcodes[i] <= 1161:
                    instructions[i] = 'ADDI'
                else:
                    instructions[i] = 'SUBI'
# D - data load and store
            elif opcodes[i] == 1986 or opcodes[i] == 1984:
                instructionformat[i] = 'D'
                rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                rnarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x1F
                addrarray[i] = (int(fullmachinecode[i], 2) >> 12) & 0x1FF
                if addrarray[i] >> 8 > 0:
                    addrarray[i] ^= 0x1FF
                    addrarray[i] += 1
                    addrarray[i] *= -1
                if opcodes[i] == 1986:
                    instructions[i] = 'LDUR'
                else:
                    instructions[i] = 'STUR'
# IM - move immediate and movezk
            elif (1684 <= opcodes[i] <= 1687 or
                  1940 <= opcodes[i] <= 1943):
                instructionformat[i] = 'IM'
                rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                shamtarray[i] = ((int(fullmachinecode[i], 2) >> 21) & 0x3) << 4
                immarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0xFFFF
                if 1684 <= opcodes[i] <= 1687:
                    instructions[i] = 'MOVZ'
                else:
                    instructions[i] = 'MOVK'
# B - branch
            elif 160 <= opcodes[i] <= 191:
                instructionformat[i] = 'B'
                instructions[i] = 'B'
                addrarray[i] = int(fullmachinecode[i], 2) & 0x3FFFFFF
                if addrarray[i] >> 25 > 0:
                    addrarray[i] ^= 0x3FFFFFF
                    addrarray[i] += 1
                    addrarray[i] *= -1
#  CB - conditional branch
            elif (1440 <= opcodes[i] <= 1447 or
                  1448 <= opcodes[i] <= 1455):
                rdarray[i] = int(fullmachinecode[i], 2) & 0x1F
                offsarray[i] = (int(fullmachinecode[i], 2) >> 5) & 0x7FFFF
                if offsarray[i] >> 18 > 0:
                    offsarray[i] ^= 0x7FFFF
                    offsarray[i] += 1
                    offsarray[i] *= -1
                instructionformat[i] = 'CB'
                if 1440 <= opcodes[i] <= 1447:
                    instructions[i] = 'CBZ'
                else:
                    instructions[i] = 'CBNZ'
# BR - data segment break
            elif opcodes[i] == 2038:
                instructionformat[i] = 'BR'
# self.datastartindex = i, multiplied by 4 for words, plus 96 for start address of 96, plus 4 for next word
                self.datastartindex = (i * 4) + 100
# for i in fullmachinecode[] end loop

# write the disassembled output file
# after return, self._[] retains info
        outfile = open(outfilename, 'w')
        memaddr = 92
        for i in range(len(fullmachinecode)):
            memaddr += 4
            outline = ""
# data segment
            if self.dataendindex is not None and memaddr >= self.datastartindex:
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\t"
                if int(fullmachinecode[i], 2) >> 31 > 0:
                    fullmachinecode[i] = int(fullmachinecode[i], 2) ^ 0xFFFFFFFF
                    fullmachinecode[i] += 1
                    fullmachinecode[i] *= -1
                    outline += str(fullmachinecode[i])
                else:
                    outline += str(fullmachinecode[i])
# instruction format wasn't found
            elif instructionformat[i] is None:
                outline += "Instruction not recognized at address: " + str(memaddr) + "\t"
                instrdisplaystring[i] = "Could not determine opcode"
# nop
            elif instructionformat[i] == 'NOP':
                outline += fullmachinecode[i] + "\t" + str(memaddr) + "\t"
                instrdisplaystring[i] = "NOP"
# R - register (add/sub/ ... )
            elif instructionformat[i] == 'R':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:16] + " "
                outline += fullmachinecode[i][16:22] + " " + fullmachinecode[i][22:27] + " "
                outline += fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t"
                instrdisplaystring[i] = str(instructions[i]) + "\tR" + str(rdarray[i]) + ", R"
                instrdisplaystring[i] += str(rnarray[i]) + ", "
                if instructions[i] == 'LSL' or instructions[i] == 'LSR' or instructions[i] == 'ASR':
                    instrdisplaystring[i] += "#" + str(shamtarray[i])
                else:
                    instrdisplaystring[i] += "R" + str(rmarray[i])
# I - immediate
            elif instructionformat[i] == 'I':
                outline += fullmachinecode[i][0:10] + " " + fullmachinecode[i][10:22] + " "
                outline += fullmachinecode[i][22:27] + " " + fullmachinecode[i][27:32]
                outline += "\t" + str(memaddr) + "\t"
                instrdisplaystring[i] = instructions[i] + "\tR" + str(rdarray[i]) + ", R"
                instrdisplaystring[i] += str(rnarray[i]) + ", #" + str(immarray[i])
# D - data load or store
            elif instructionformat[i] == 'D':
                outline += fullmachinecode[i][0:11] + " " + fullmachinecode[i][11:20] + " "
                outline += fullmachinecode[i][20:22] + " " + fullmachinecode[i][22:27] + " "
                outline += fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t"
                instrdisplaystring[i] = instructions[i] + "\tR" + str(rdarray[i]) + ", [R"
                instrdisplaystring[i] += str(rnarray[i]) + ", #" + str(addrarray[i]) + "]"
# IM - move immediate and movezk
            elif instructionformat[i] == 'IM':
                outline += fullmachinecode[i][0:9] + " " + fullmachinecode[i][9:11] + " "
                outline += fullmachinecode[i][11:27] + " " + fullmachinecode[i][27:32]
                outline += "\t" + str(memaddr) + "\t"
                instrdisplaystring[i] = instructions[i] + "\tR" + str(rdarray[i]) + ", "
                instrdisplaystring[i] += str(immarray[i]) + ", LSL " + str(shamtarray[i])
# B - branch
            elif instructionformat[i] == 'B':
                outline += fullmachinecode[i][0:6] + " " + fullmachinecode[i][6:32] + "\t"
                outline += str(memaddr) + "\t"
                instrdisplaystring[i] = "B\t#" + str(addrarray[i])
# CB - conditional branch
            elif instructionformat[i] == 'CB':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:27] + " "
                outline += fullmachinecode[i][27:32] + "\t" + str(memaddr) + "\t"
                instrdisplaystring[i] = instructions[i] + "\tR"
                instrdisplaystring[i] += str(rdarray[i]) + ", #" + str(offsarray[i])
# BR - data segment break
            elif instructionformat[i] == 'BR':
                outline += fullmachinecode[i][0:8] + " " + fullmachinecode[i][8:11] + " "
                outline += fullmachinecode[i][11:16] + " " + fullmachinecode[i][16:21] + " "
                outline += fullmachinecode[i][21:26] + " " + fullmachinecode[i][26:32] + "\t" + str(memaddr)
                outline += "\t"
                instrdisplaystring[i] = "BREAK"
# write output line and restart loop until eof
            if self.datastartindex is None or i < self.datastartindex:
                outline += instrdisplaystring[i]
            print >> outfile, outline

        outfile.close()
        return self


#  function called when script ran from command line and acts as a disassembler for machine code
#  then iterates through machine code simulating pipelined execution with output stepping at each stage
#  ran in the form: $ python team1_project1.py -i test3_bin.txt -o team1
#  where test3_bin.txt is the input machine code text file that is read and team1 is the prefix for file output
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
# decompiled.run() sets -> .outfileprefix .self.data{} .datastartindex .dataendindex
    Emulator.run(decompiled)
