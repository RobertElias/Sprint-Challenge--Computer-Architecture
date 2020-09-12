import sys
#python3 ls8.py sctest.ls8
# OPS
CALL = 0b01010000
ADD = 0b10100000
DIV = 0b10100011
MUL = 0b10100010
SUB = 0b10100001
LDI = 0b10000010
POP = 0b01000110
PUSH = 0b01000101
PRA = 0b01001000
PRN = 0b01000111
RET = 0b00010001
ST = 0b10000100
CMP = 0b10100111
JEQ = 0b01010101
JMP = 0b01010100
JNE = 0b01010110
HLT = 0b00000001
SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.pc = 0
        self.reg = [0] * 8
        self.fl = 0b00000000
        self.reg[SP] = 0xF4
        self.branchtable = {
            CALL: self.call,
            ADD : self.alu,
            DIV : self.alu,
            MUL : self.alu,
            SUB : self.alu,
            LDI : self.ldi,
            POP : self.pop,
            PUSH : self.push,
            PRA : self.pra,
            PRN : self.prn,
            RET : self.ret,
            ST : self.st,
            CMP : self.alu,
            JEQ : self.jeq,
            JMP : self.jmp,
            JNE : self.jne,
            HLT : self.hlt
        }
    
    def load(self, filename):
        """Load a program into memory."""
        address = 0
        # this runs the load
        with open(filename) as file:
            for line in file:
                line = line.split("#")
                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue
                self.ram[address] = v
                address += 1

    def call(self, reg_a, reg_b=None):
        # this is the subroutine for reg[reg_a]
        # & sp -=1
        self.reg[SP] -= 1
        #this will come back
        self.ram_write(self.reg[SP], self.pc + 2)
        self.pc = self.reg[reg_a]

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
            print(f"ADD at REG[{self.pc + 1}]: {self.reg[self.pc + 1]}")

        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
            print(f"SUB at REG[{self.pc + 1}]: {self.reg[self.pc + 1]}")

        elif op == DIV:
            if self.reg[reg_b] != 0:
                self.reg[reg_a] /= self.reg[reg_b]
                print(f"DIV at REG[{self.pc + 1}]: {self.reg[self.pc + 1]}")
            else:
                raise Exception("Unsupported DIV operation")

        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
            print(f"MUL at REG[{self.pc + 1}]: {self.reg[self.pc + 1]}")

        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

        else:
            raise Exception("Unsupported ALU operation")
     # ram_read function memory address register       
    def ram_read(self, address):
        return self.ram[address]
    # ram_write function memory address register
    def ram_write(self, value, address):
        self.ram[address] = value

    def run(self):
        """Run the CPU.       
        
        """
        
        while True:
            ir = self.ram[self.pc]
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)
            #this updates the cpu/pc
            update = (ir >> 6) + 1
            
            alu_op = ((ir >> 5) & 0b1)
            #pc will be set
            set_pc = ((ir >> 4) & 0b1)
    
            if ir in self.branchtable:
                if alu_op:
                    #this will pass in type of operation 
                    self.branchtable[ir](ir, reg_a, reg_b)
                else:
                    #pass reg_a, reg_b
                    self.branchtable[ir](reg_a, reg_b)
            else:
                print('Unsupported command')
            if not set_pc:
                self.pc += update

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ldi(self, reg_a, reg_b):
        self.reg[reg_a] = reg_b 
    #pop function
    def pop(self, reg_a, reg_b=None):
        #get value 
        value = self.ram_read(self.reg[SP])
        #this will set reg = value
        self.reg[reg_a] = value
        #then sp +1
        self.reg[SP] += 1
        return value
    #push function
    def push(self, reg_a, reg_b=None):
        #the value pushed onto stack, then changes pointer
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.reg[reg_a])
    #pra function
    def pra(self, reg_a, reg_b=None):
        # ascii
        print(chr(self.reg[reg_a]))
    #prn function
    def prn(self, reg_a, reg_b=None):
        # decimal
        print("Returning", self.reg[reg_a])
    #return function
    def ret(self, reg_a=None, reg_b=None):
        #this pops + store in pc
        self.pc = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
    # st function
    def st(self, reg_a, reg_b):
        self.ram_write(self.reg[reg_a], self.reg[reg_b])
    #jeq function
    def jeq(self, reg_a, reg_b=None):
        #(fl) 'jump' to given reg
        if self.fl & 0b1 == 1:
            self.pc = self.reg[reg_a]
        else:
            self.pc += 2
    #jmp function
    def jmp(self, reg_a, reg_b=None):
        # go to stored reg
        self.pc = self.reg[reg_a]
    #jne function
    def jne(self, reg_a, reg_b=None):
        # if equal (fl) is 0 go to given reg
        if self.fl & 0b1 == 0:
            self.pc = self.reg[reg_a]
        else:
            self.pc += 2
    #hlt function
    def hlt(self, reg_a=None, reg_b=None):
        #this stops
        sys.exit()

