
# Hack Assembler
# Nand2Tetris Capstone Project
# Personal Number K = 55

import os
import re
import sys


K = 55

PREDEFINED_SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

for i in range(16):
    PREDEFINED_SYMBOLS["R" + str(i)] = i


# -----------------------------------
# C-Instruction Tables
# -----------------------------------

COMP_TABLE = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}


DEST_TABLE = {
    "": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}


JUMP_TABLE = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


# -----------------------------------
# Check Symbol Name
# -----------------------------------

def valid_symbol(symbol):

    pattern = r"[A-Za-z_.$:][A-Za-z0-9_.$:]*"

    return re.fullmatch(pattern, symbol) is not None


# -----------------------------------
# Read Assembly File
# -----------------------------------

def read_file(filename):

    instructions = []

    with open(filename, "r") as file:

        lines = file.readlines()

    for line_number, line in enumerate(lines, start=1):

        # Remove comments
        line = line.split("//")[0]

        # Remove extra spaces
        line = line.strip()

        # Ignore blank lines
        if line != "":

            instructions.append((line_number, line))

    return instructions


# -----------------------------------
# First Pass: Find Labels
# -----------------------------------

def first_pass(instructions):

    symbol_table = PREDEFINED_SYMBOLS.copy()

    rom_address = 0
    errors = []

    for line_number, instruction in instructions:

        if instruction.startswith("(") or instruction.endswith(")"):

            if not (
                instruction.startswith("(")
                and instruction.endswith(")")
                and instruction.count("(") == 1
                and instruction.count(")") == 1
            ):

                errors.append(
                    (line_number, "Invalid label declaration")
                )

                continue

            label = instruction[1:-1]

            if not valid_symbol(label):

                errors.append(
                    (line_number, "Invalid label name")
                )

            elif label in symbol_table:

                errors.append(
                    (line_number, "Duplicate or reserved label")
                )

            else:

                symbol_table[label] = rom_address

        else:

            rom_address += 1

    if rom_address > 32768:

        errors.append(
            (1, "Program exceeds ROM address limit")
        )

    return symbol_table, errors


# -----------------------------------
# Second Pass: Allocate Variables
# -----------------------------------

def second_pass(instructions, symbol_table):

    next_variable = 16
    errors = []

    for line_number, instruction in instructions:

        if instruction.startswith("@"):

            symbol = instruction[1:]

            if symbol.isdigit():
                continue

            if not valid_symbol(symbol):

                continue

            if symbol not in symbol_table:

                if next_variable > 16383:

                    errors.append(
                        (line_number, "Variable memory limit exceeded")
                    )

                else:

                    symbol_table[symbol] = next_variable
                    next_variable += 1

    return symbol_table, errors


# -----------------------------------
# Convert A-Instruction
# -----------------------------------

def convert_a_instruction(instruction, symbol_table):

    symbol = instruction[1:]

    if symbol == "":

        raise ValueError("Empty A-instruction")

    if symbol.isdigit():

        address = int(symbol)

    else:

        if not valid_symbol(symbol):

            raise ValueError("Invalid symbol name")

        if symbol not in symbol_table:

            raise ValueError("Undefined symbol")

        address = symbol_table[symbol]

    if address < 0 or address > 32767:

        raise ValueError("Address out of range")

    return format(address, "016b")


# -----------------------------------
# Convert C-Instruction
# -----------------------------------

def convert_c_instruction(instruction):

    # Remove spaces and tabs
    instruction = instruction.replace(" ", "")
    instruction = instruction.replace("\t", "")

    dest = ""
    jump = ""

    # Check for multiple separators
    if instruction.count("=") > 1:

        raise ValueError("Invalid destination")

    if instruction.count(";") > 1:

        raise ValueError("Invalid jump")

    # Separate jump
    if ";" in instruction:

        instruction, jump = instruction.split(";")

    # Separate destination
    if "=" in instruction:

        dest, comp = instruction.split("=")

    else:

        comp = instruction

    # Check destination
    if dest not in DEST_TABLE:

        # Allow valid destination permutations
        if (
            len(dest) != len(set(dest))
            or not dest
            or any(char not in "ADM" for char in dest)
        ):

            raise ValueError("Invalid destination")

        dest = "".join(
            char for char in "ADM" if char in dest
        )

    # Check computation
    if comp not in COMP_TABLE:

        raise ValueError("Invalid computation")

    # Check jump
    if jump not in JUMP_TABLE:

        raise ValueError("Invalid jump")

    # Generate 16-bit C-instruction
    binary = (
        "111"
        + COMP_TABLE[comp]
        + DEST_TABLE[dest]
        + JUMP_TABLE[jump]
    )

    return binary


# -----------------------------------
# Main Assembler Function
# -----------------------------------

def assemble(input_file):

    print("\nWelcome to Hack Assembler!")
    print("Personal Number K =", K)

    # Read assembly instructions
    instructions = read_file(input_file)

    print("\nInput file:", input_file)

    # First pass
    symbols, errors = first_pass(instructions)

    # Second pass
    symbols, variable_errors = second_pass(
        instructions, symbols
    )

    errors.extend(variable_errors)

    machine_code = []

    # Generate machine code
    for line_number, instruction in instructions:

        # Skip labels
        if instruction.startswith("(") and instruction.endswith(")"):
            continue

        try:

            if instruction.startswith("@"):

                binary = convert_a_instruction(
                    instruction, symbols
                )

            else:

                binary = convert_c_instruction(
                    instruction
                )

            if len(binary) != 16:

                raise ValueError("Invalid instruction length")

            machine_code.append(binary)

        except ValueError as error:

            errors.append(
                (line_number, str(error))
            )

    # -----------------------------------
    # Display Errors
    # -----------------------------------

    if errors:

        print("\nAssembly Errors:")

        for line_number, message in errors:

            print(
                "Line", line_number, ":", message
            )

        print("\nAssembly failed.")

        print("No new output file was generated.")

        return False

    # -----------------------------------
    # Generate Output File
    # -----------------------------------

    output_file = os.path.splitext(input_file)[0] + ".hack"

    with open(output_file, "w") as file:

        for binary in machine_code:

            file.write(binary + "\n")

    print("\nMachine code successfully generated!")

    print("Output file:", output_file)

    print("Total instructions:", len(machine_code))

    return True


# -----------------------------------
# Main Program
# -----------------------------------

if __name__ == "__main__":

    if len(sys.argv) > 2:

        print("Usage: python assembler.py [filename.asm]")

    else:

        input_file = (
            sys.argv[1] if len(sys.argv) == 2
            else "Add.asm"
        )

        if not input_file.lower().endswith(".asm"):

            print("Error: Please provide an .asm file.")

        elif not os.path.isfile(input_file):

            print("Error: Assembly file not found:", input_file)

        else:

            try:

                assemble(input_file)

            except OSError as error:

                print("File error:", error)
