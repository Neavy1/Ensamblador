import re
from typing import Tuple

class IMeta:
    def __init__(self, iType: str, opcode:str, funct3:str|None = None, funct7:str|None = None):
        self.iType = iType
        self.opcode = opcode
        self.funct3 = funct3
        self.funct7 = funct7

    def __str__(self):
        return f"{self.iType} {self.opcode} {self.funct3} {self.funct7}"

iMetas = {
    'add':   IMeta('R', '0110011', '000', '0000000'),
    'sub':   IMeta('R', '0110011', '000', '0100000'),
    'sll':   IMeta('R', '0110011', '001', '0000000'),
    'slt':   IMeta('R', '0110011', '010', '0000000'),
    'sltu':  IMeta('R', '0110011', '011', '0000000'),
    'xor':   IMeta('R', '0110011', '100', '0000000'),
    'srl':   IMeta('R', '0110011', '101', '0000000'),
    'sra':   IMeta('R', '0110011', '101', '0100000'),
    'or':    IMeta('R', '0110011', '110', '0000000'),
    'and':   IMeta('R', '0110011', '111', '0000000'),

    'addi':  IMeta('I', '0010011', '000'),
    'slli':  IMeta('I', '0010011', '001'),
    'slti':  IMeta('I', '0010011', '010'),
    'sltiu': IMeta('I', '0010011', '011'),
    'xori':  IMeta('I', '0010011', '100'),
    'srli':  IMeta('I', '0010011', '101'),
    'srai':  IMeta('I', '0010011', '101'),
    'ori':   IMeta('I', '0010011', '110'),
    'andi':  IMeta('I', '0010011', '111'),

    'lb':    IMeta('I', '0000011', '000'),
    'lh':    IMeta('I', '0000011', '001'),
    'lw':    IMeta('I', '0000011', '010'),
    'lbu':   IMeta('I', '0000011', '100'),
    'lhu':   IMeta('I', '0000011', '101'),
    'jalr':  IMeta('I', '1100111', '000'),

    'beq':   IMeta('B', '1100011', '000'),
    'bne':   IMeta('B', '1100011', '001'),
    'blt':   IMeta('B', '1100011', '100'),
    'bge':   IMeta('B', '1100011', '101'),
    'bltu':  IMeta('B', '1100011', '110'),
    'bgeu':  IMeta('B', '1100011', '111'),

    'sb':    IMeta('S', '0100011', '000'),
    'sh':    IMeta('S', '0100011', '001'),
    'sw':    IMeta('S', '0100011', '010'),

    'jal':   IMeta('J', '1101111'),

    'lui':   IMeta('U', '0110111'),
    'auipc': IMeta('U', '0010111'),
}

registers = {
    'x0': 0, 'zero': 0,
    'x1': 1, 'ra': 1,
    'x2': 2, 'sp': 2,
    'x3': 3, 'gp': 3,
    'x4': 4, 'tp': 4,
    'x5': 5, 't0': 5,
    'x6': 6, 't1': 6,
    'x7': 7, 't2': 7,
    'x8': 8, 's0': 8, 'fp': 8,
    'x9': 9, 's1': 9,
    'x10': 10, 'a0': 10,
    'x11': 11, 'a1': 11,
    'x12': 12, 'a2': 12,
    'x13': 13, 'a3': 13,
    'x14': 14, 'a4': 14,
    'x15': 15, 'a5': 15,
    'x16': 16, 'a6': 16,
    'x17': 17, 'a7': 17,
    'x18': 18, 's2': 18,
    'x19': 19, 's3': 19,
    'x20': 20, 's4': 20,
    'x21': 21, 's5': 21,
    'x22': 22, 's6': 22,
    'x23': 23, 's7': 23,
    'x24': 24, 's8': 24,
    'x25': 25, 's9': 25,
    'x26': 26, 's10': 26,
    'x27': 27, 's11': 27,
    'x28': 28, 't3': 28,
    'x29': 29, 't4': 29,
    'x30': 30, 't5': 30,
    'x31': 31, 't6': 31,

}

iSelectors = {
    'rd': ['I', 'R', 'S'],
    'rs1': ['I', 'R', 'S', 'B', 'U', 'J'],
    'rs2': ['R', 'S', 'B'],
    'imm': ['I', 'S', 'B', 'U', 'J'],
}

def verifyImmType(imm: str)->bool|None:
    try:
        imm = int(imm,0)
        return imm
    except ValueError:
        return None

def getIMeta(instruccion: str) -> IMeta:
    instruccion = instruccion.lower()
    return iMetas.get(instruccion, None)

def extractParts(instruccion: str) -> Tuple[str, str|None, str|None, str|None, str|None]: #? instruccion, rd, rs1, rs2, imm
    re1 = r'(?P<instruccion>\w+)\s+(?P<rd>\w+),?\s+(?P<rs1>\w+),?\s+(?P<rs2>.+)' # R type 
    # ? re2 is included in r1, needs validation
    # re2 = r'(?P<instruccion>\w+)\s+(?P<rd>\w+),?\s+(?P<rs1>\w+),?\s+(?P<imm>\w+)' # I( no load), B type
    re3 = r'(?P<instruccion>\w+)\s+(?P<rd>\w+),?\s+(?P<imm>\w+)\((?P<rs1>\w+)\)' # S, I (load) type
    re4 = r'(?P<instruccion>\w+)\s+(?P<rd>\w+),?\s+(?P<imm>\w+)$' # U, J type

    if m := re.match(re1, instruccion):
        instruccion = m.group('instruccion')
        rd = m.group('rd')
        rs1 = m.group('rs1')
        rs2 = m.group('rs2')
        
        if rd not in registers or rs1 not in registers or instruccion not in iMetas:
            raise ValueError("Registro no valido")
        
        if iMetas[instruccion].iType == 'R':
            if rs2 not in registers:
                raise ValueError("Registro no valido")
            return instruccion, registers[rd], registers[rs1], registers[rs2], None
        
        elif iMetas[instruccion].iType == 'I':
            imm = rs2
            # Verificar que sea un numero decimal o hexadecimal
            
            if verifyImmType(imm) is None:
                print(imm)
                raise ValueError("Inmediato no valido 1I")
            
            return instruccion, registers[rd], registers[rs1], None, verifyImmType(imm)
        
        elif iMetas[instruccion].iType == 'B':
            imm = rs2
            rs2 = rs1
            rs1 = rd

            if verifyImmType(imm) is None:
                raise ValueError("Inmediato no valido1B")
            
            return instruccion, None, registers[rs1], registers[rs2], verifyImmType(imm)
        else:
            raise ValueError("Instruccion no valida")

    if m := re.match(re3, instruccion):
        instruccion = m.group('instruccion')
        rd = m.group('rd')
        imm = m.group('imm')
        rs1 = m.group('rs1')

        if rd not in registers or rs1 not in registers or instruccion not in iMetas:
            raise ValueError("Registro no valido")
        
        if iMetas[instruccion].iType == 'S':
            rs2 = rd
            if verifyImmType(imm) is None:
                raise ValueError("Inmediato no valido")
            return instruccion, None, registers[rs1], registers[rs2], verifyImmType(imm)
        elif iMetas[instruccion].iType == 'I':
            if verifyImmType(imm) is None:
                raise ValueError("Inmediato no valido")
            return instruccion, registers[rd], registers[rs1], None, verifyImmType(imm)
        else:
            raise ValueError("Instruccion no valida")
        
    if m := re.match(re4, instruccion):
        instruccion = m.group('instruccion')
        rd = m.group('rd')
        imm = m.group('imm')

        if rd not in registers or instruccion not in iMetas:
            raise ValueError("Registro no valido")
        
        if iMetas[instruccion].iType == 'U':
            if verifyImmType(imm) is None:
                raise ValueError("Inmediato no valido")
            return instruccion, registers[rd], None, None, verifyImmType(imm)
        elif iMetas[instruccion].iType == 'J':
            if verifyImmType(imm) is None:
                raise ValueError("Inmediato no valido")
            return instruccion, registers[rd], None, None, verifyImmType(imm)
        else:
            raise ValueError("Instruccion no valida")
        
    raise ValueError("Instruccion no valida")
            

def translate(instruccion: str, bina: bool = False) -> str:
    try:
        instruccion, rd, rs1, rs2, imm = extractParts(instruccion)
        # instruccion = extractParts(instruccion)
        # print(instruccion)
    except ValueError as e:
        print(e)
        return ''

    iMeta = getIMeta(instruccion)

    if iMeta is None:
        return ''
    
    if imm is not None:
        imm = format(imm, '032b')

    if iMeta.iType == 'R':
        binInst = f"{iMeta.funct7}{rs2:05b}{rs1:05b}{iMeta.funct3}{rd:05b}{iMeta.opcode}"
    elif iMeta.iType == 'I':
        binInst = f"{imm[-12:]}{rs1:05b}{iMeta.funct3}{rd:05b}{iMeta.opcode}"
    elif iMeta.iType == 'S':
        binInst = f"{imm[-12:-5]}{rs2:05b}{rs1:05b}{iMeta.funct3}{imm[-5:]}{iMeta.opcode}"
    elif iMeta.iType == 'B':
        binInst = f"{imm[-13]}{imm[-11:-5]}{rs2:05b}{rs1:05b}{iMeta.funct3}{imm[-5:-1]}{imm[-12]}{iMeta.opcode}"
    elif iMeta.iType == 'U':
        binInst = f"{imm[-32:-12]}{rd:05b}{iMeta.opcode}"
    elif iMeta.iType == 'J':
        binInst = f"{imm[-21]}{imm[-11:-1]}{imm[-12]}{imm[-20:-12]}{rd:05b}{iMeta.opcode}"
    else:
        return ''
    
    if bina:
        return binInst
    return f'{int(binInst, 2):08x}'

def translateFile(iFile: str, oFile: str, bina: bool):
    try:
        with open(iFile, 'r') as f:
            instrucciones = f.readlines()
    except FileNotFoundError:
        print(f"Archivo {iFile} no encontrado")
        return
    
    if oFile is None:
        oFile = 'output'
    fileExt = ('.bin' if bina else '.hex')

    f1 = open(oFile+f'1{fileExt}', 'w')
    f2 = open(oFile+f'2{fileExt}', 'w')
    f3 = open(oFile+f'3{fileExt}', 'w')
    f4 = open(oFile+f'4{fileExt}', 'w')
    f1.write('v2.0 raw')
    f2.write('v2.0 raw')
    f3.write('v2.0 raw')
    f4.write('v2.0 raw')
    for instruccion in instrucciones:
        translated = translate(instruccion, bina)
        if translated == '':
            continue
        f1.write('\n'+translated[:2])
        f2.write('\n'+translated[2:4])
        f3.write('\n'+translated[4:6])
        f4.write('\n'+translated[6:8])
    
    f1.close()
    f2.close()
    f3.close()
    f4.close()

def translateConsole(oSrc: str|None, bina: bool):
    if oSrc:
        fileExt = ('.bin' if bina else '.hex')
        f1 = open(f'{oSrc}1{fileExt}', 'w')
        f1.write('v2.0 raw')
        f2 = open(f'{oSrc}2{fileExt}', 'w')
        f2.write('v2.0 raw')
        f3 = open(f'{oSrc}3{fileExt}', 'w')
        f3.write('v2.0 raw')
        f4 = open(f'{oSrc}4{fileExt}', 'w')
        f4.write('v2.0 raw')

    inst = input(" > ")
    while inst != 'exit':
        translated = translate(inst, bina)
        if oSrc:
            if translated == '':
                continue
            f1.write('\n' + translated[:2])
            f2.write('\n' + translated[2:4])
            f3.write('\n' + translated[4:6])
            f4.write('\n' + translated[6:8])
        else:
            print(translated)
        inst = input(" > ")

    if oSrc:
        f1.close()
        f2.close()
        f3.close()
        f4.close()

if __name__ == '__main__':
    import argparse
    print("Conversor de instrucciones RISCV a hexadecimal")

    parser = argparse.ArgumentParser(description='Conversor de instrucciones RISCV a hexadecimal')
    parser.add_argument('-i', '--in', metavar='inputFile', dest='inFile', type=str, help='Archivo de entrada')
    parser.add_argument('-o', '--out', metavar='outputFile', dest='outFile', type=str,help='Archivo de salida', nargs='?', const='output')
    parser.add_argument('-b', '--bin', dest='bina', help='Transforma a binario en lugar de hexadecimal', action='store_true')

    args = parser.parse_args()

    print("Archivo de entrada: ", args)
    if args.inFile: 
        translateFile(args.inFile, args.outFile, args.bina)
    else:
        translateConsole(args.outFile, args.bina)