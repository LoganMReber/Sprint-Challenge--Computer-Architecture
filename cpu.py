"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.reg = [0]*8
        self.ram = [0]*256
        self.pc = 0
        self.sp = 255
        self.fl = 0

    def ram_read(self, loc):
        return self.ram[loc]

    def ram_write(self, loc, val):
        self.ram[loc] = val

    def load(self, filepath):
        """Load a program into memory."""

        address = 0
        file = open(filepath)
        program = []
        for line in file:
            cmd = line.strip()
            cmd = cmd.split(' ')[0]
            if len(cmd) == 8:
                program.append(int(cmd, 2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == 0b0000:  # ADD
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b0001:  # SUB
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 0b0010:  # MUL
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 0b0011:  # DIV
            self.reg[reg_a] //= self.reg[reg_b]
        elif op == 0b0100:  # MOD
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == 0b0101:  # INC
            self.reg[reg_a] += 1
        elif op == 0b0110:  # DEC
            self.reg[reg_a] -= 1
        elif op == 0b0111:  # CMP
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 4
            else:
                self.fl = 2
        elif op == 0b1000:
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == 0b1001:
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == 0b1010:
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == 0b1011:
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == 0b1100:
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == 0b1101:
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def mut(self, op, reg_a, size):
        """PC Mutators"""
        if op == 0b0000:  # CALL
            self.sp -= 1
            self.ram_write(self.sp, self.pc + size + 1)
            self.pc = self.reg[reg_a]

        elif op == 0b0001:  # RET
            self.pc = self.ram_read(self.sp)
            self.sp += 1

        elif op == 0b0100:  # JMP
            self.pc = self.reg[reg_a]
        elif op == 0b0101:  # JEQ
            if self.fl == 1:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2
        elif op == 0b0110:  # JNE
            if self.fl != 1:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2
        elif op == 0b0111:  # JGT
            if self.fl == 2:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2
        elif op == 0b1000:  # JLT
            if self.fl == 4:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2
        elif op == 0b0101:  # JLE
            if self.fl == 1 or self.fl == 4:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2
        elif op == 0b0101:  # JGE
            if self.fl == 1 or self.fl == 2:
                self.pc = self.reg[reg_a]
            else:
                self.pc += 2
        else:
            raise Exception("Unsupported PCM operation")

    def misc(self, op, reg_a, reg_b):
        if op == 0b0000:  # NOP
            return
        elif op == 0b0010:  # LDI
            self.reg[reg_a] = reg_b
        elif op == 0b00101:  # PUSH
            self.sp -= 1
            self.ram_write(self.sp, self.reg[reg_a])
        elif op == 0b0110:  # POP
            self.reg[reg_a] = self.ram_read(self.sp)
            self.sp += 1
        elif op == 0b0111:  # PRN
            print(self.reg[reg_a])
        else:
            raise Exception("Unsupported CU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %02X %02X | %02X %02X %02X |" % (
            self.pc,
            self.sp,
            self.ram_read(self.sp),
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):

        self.pc = 0
        while True:
            ir = self.ram_read(self.pc)
            if ir == 1:
                break
            size = (ir & 0b11000000) >> 6
            alu = (ir & 0b00100000) >> 5
            pcm = (ir & 0b00010000) >> 4
            cmd = ir & 0b00001111
            if alu:
                self.alu(
                    cmd,
                    self.ram_read(self.pc+1),
                    self.ram_read(self.pc+2)
                )
            elif pcm:
                self.mut(cmd, self.ram_read(self.pc+1), size)
            else:
                self.misc(
                    cmd,
                    self.ram_read(self.pc+1),
                    self.ram_read(self.pc+2)
                )
            if not pcm:
                self.pc += size + 1
