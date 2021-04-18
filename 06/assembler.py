#! /usr/bin/python

import sys

comp_table = {
    '0':      '0101010',
    '1':      '0111111',
    '-1':     '0111010',
    'D':      '0001100',
    'A':      '0110000',
    'M':      '1110000',
    '!D':     '0001101',
    '!A':     '0110001',
    '!M':     '1110001',
    '-D':     '0001111',
    '-A':     '0110011',
    '-M':     '1110011',
    'D+1':    '0011111',
    'A+1':    '0110111',
    'M+1':    '1110111',
    'D-1':    '0001110',
    'A-1':    '0110010',
    'M-1':    '1110010',
    'D+A':    '0000010',
    'D+M':    '1000010',
    'D-A':    '0010011',
    'D-M':    '1010011',
    'A-D':    '0000111',
    'M-D':    '1000111',
    'D&A':    '0000000',
    'D&M':    '1000000',
    'D|A':    '0010101',
    'D|M':    '1010101'
}

dest_table = {
    #null   000
    'M':    '001',
    'D':    '010',
    'MD':   '011',
    'A':    '100',
    'AM':   '101',
    'AD':   '110',
    'AMD':  '111',
}

jump_table = {
    #null   000
    'JGT':  '001',
    'JEQ':  '010',
    'JGE':  '011',
    'JLT':  '100',
    'JNE':  '101',
    'JLE':  '110',
    'JMP':  '111'
}

symbols_table = {
    "R0":       0,
    "R1":       1,
    "R2":       2,
    "R3":       3,
    "R4":       4,
    "R5":       5,
    "R6":       6,
    "R7":       7,
    "R8":       8,
    "R9":       9,
    "R10":      10,
    "R11":      11,
    "R12":      12,
    "R13":      13,
    "R14":      14,
    "R15":      15,
    "SCREEN":   16384,
    "KBD":      24576,
    "SP":       0,
    "LCL":      1,
    "ARG":      2,
    "THIS":     3,
    "THAT":     4
}

class Assembler(object):
    """docstring for Assembler"""
    def __init__(self, filepath):
        super(Assembler, self).__init__()
        self.filepath = filepath
        self.custom_symbols = {}
        self.variables = {};
        self.currentFreeMemoryAddress = 16

    def _populateCustomSymbols(self):
        with open(self.filepath, 'r') as file:
            labelsEncounteredSoFar = 0
            labelsToHandle = []

            normalized = [self._normalize(l) for l in file.readlines()]
            filtered = [l for l in normalized if len(l) > 0]

            for inx,line in enumerate(filtered):
                if self._is_label_instruction(line):
                    endLabelInx = line.find(')')
                    if endLabelInx == -1:
                        raise Exception("Improper label syntax.")

                    label = line[1:endLabelInx];
                    labelsToHandle.append(label);
                    labelsEncounteredSoFar += 1
                else:
                    if len(labelsToHandle) > 0:
                        for l in labelsToHandle:
                            self.custom_symbols[l] = inx - labelsEncounteredSoFar

                        labelsToHandle = []

        return self.custom_symbols;



    def _normalize(self,line):
        '''Returns line trimmed with all chars after comment symbol (//) removed.'''
        normalized = line
        commentInx = normalized.find('//')
        
        if commentInx != -1:
            normalized = normalized[0:commentInx]

        normalized = normalized.strip()

        return normalized

    def _translate_instruction(self, instr):
        '''Returns the binary string representing the instruction.'''
        try:
            if self._is_a_instruction(instr):
                return self._handle_a_instruction(instr)
            else:
                return self._handle_c_instruction(instr)
        except Exception as e:
            print "Unable to translate instruction: " + instr
            raise e;

    def _handle_a_instruction(self, instr):
        value = instr[1:]
        createdNewVariable = False;
        if value.isdigit() == False:
            if value in symbols_table:
                value = symbols_table[value]
            elif value in self.custom_symbols:
                value = self.custom_symbols[value]
            else:
                # create variable
                if self.currentFreeMemoryAddress >= 16384:
                    raise IndexError("Memory only available between (16..16384]");
                self.custom_symbols[value] = self.currentFreeMemoryAddress
                value = self.currentFreeMemoryAddress
                createdNewVariable = True;
        
        address = int(value)

        if address < 0:
            raise Exception("address must be non-negative")

        binaryAddr = bin(address)[2:] # removes the 0b from the binary string
        binaryAddr = binaryAddr[-15:] # Gets the least significant 15 bits of the binary address

        bitlength = len(binaryAddr)
        
        if bitlength < 15:
            padding = '0'*(15-bitlength)
            binaryAddr = padding + binaryAddr

        if createdNewVariable:
            self.currentFreeMemoryAddress += 1
            
        return '0' + binaryAddr; # a-instr opcode + 15bit binary memory address

    def _handle_c_instruction(self, instr):
        inxOfDest = instr.find('=');
        begInxOfComp = inxOfDest + 1 if inxOfDest != -1 else 0

        inxOfJump = instr.find(';');
        endInxOfComp = inxOfJump if inxOfJump != -1 else len(instr)

        dest = '000';
        jump = '000';

        if inxOfDest != -1:
            destSymbol = instr[0:inxOfDest]
            dest = dest_table[destSymbol]

        if inxOfJump != -1:
            jumpSymbol = instr[inxOfJump+1:]
            jump = jump_table[jumpSymbol]

        compSymbol = instr[begInxOfComp:endInxOfComp]

        if compSymbol not in compSymbol:
            raise Exception('Computaion unrecognized: ' + compSymbol)

        comp = comp_table[compSymbol]
        
        return '111' + comp + dest + jump;

    def _is_a_instruction(self,instr):
        return instr.startswith("@")

    def _is_label_instruction(self,instr):
        return instr.startswith("(")

    def assemble(self):
        self.currentFreeMemoryAddress = 16 # Reset the free memory address each time we call assemble
        self._populateCustomSymbols()

        with open(self.filepath[:len(self.filepath)-4] + '.hack', 'a') as outFile:
            with open(self.filepath, 'r') as file:
                for line in file.readlines():
                    normalized = self._normalize(line);

                    if len(normalized) > 0:
                        if self._is_label_instruction(normalized):
                            continue;
                        else:
                            outline = self._translate_instruction(normalized);
                            outFile.write(outline+'\n')
                
        return None;


def main():
    try:
        filename = sys.argv[1];
    except IndexError as e:
        print "Program could not be assembled: No path to asm file specified."

    assembler = Assembler(filename)

    return assembler.assemble();

if __name__ == '__main__':
    main();
