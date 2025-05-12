import os
import random
import re
from pathlib import Path
import argparse
class MutationInjector:
    """
    Our defect injector based on mutation testing.
    Supports seven injection patterns:
      1. Statement insertion
      2. Statement deletion
      3. Method parameter mutation
      4. Condition expression mutation
      5. Variable mutation
      6. Operator mutation
      7. Other mutations
    """
    def __init__(self):
        # operators mapping for mutation
        self.operators = {
            '+': '-',
            '-': '+',
            '*': '/',
            '/': '*',
            '==': '!=',
            '!=': '==',
            '>': '<',
            '<': '>',
            '>=': '<=',
            '<=': '>='
        }

    def inject(self, code_line, pattern=None):
        """
        Inject a new defect into the given code line.
        If pattern is None, choose randomly from 1-7.
        Returns mutated code line.
        """
        if pattern is None:
            pattern = random.randint(1, 7)
        method = getattr(self, f'_pattern_{pattern}', None)
        if not method:
            raise ValueError(f"Unsupported mutation pattern: {pattern}")
        return method(code_line)

    def _pattern_1(self, line):
        # Statement insertion: insert an erroneous function call
        insert = "logger.error('unexpected error')"
        return insert + "; " + line

    def _pattern_2(self, line):
        # Statement deletion: return empty or comment out
        return f"// {line.strip()}  // deleted by mutation"

    def _pattern_3(self, line):
        # Method parameter mutation: swap or replace literal
        return re.sub(r"(\w+\()([^\)]+)(\))",
                      lambda m: f"{m.group(1)}null{m.group(3)}", line)

    def _pattern_4(self, line):
        # Condition expression mutation: flip boolean or insert wrong expr
        return re.sub(r"(if\s*\()([^\)]+)(\))",
                      lambda m: f"{m.group(1)}!( {m.group(2)} ){m.group(3)}", line)

    def _pattern_5(self, line):
        # Variable mutation: replace variable with constant 0
        return re.sub(r"\b(\w+)\b", '0', line, count=1)

    def _pattern_6(self, line):
        # Operator mutation: change one operator
        for op, sub in self.operators.items():
            if op in line:
                return line.replace(op, sub, 1)
        return line

    def _pattern_7(self, line):
        # Other mutations: change return statement
        return re.sub(r"return\s+(.+);", r"return null;  // mutated", line)

def main(input_dir: str, output_dir: str):
    """
    Process JIT defect files in input_dir, inject new defects, and write results to output_dir.
    Each input file is read line by line as defect entries (old defects).
    For each line, a new defect (new defects) is injected and paired.
    Output files mirror input names in output_dir, with each line formatted as:
    (old_defect_line  new_defect_line)
    """
    src = Path(input_dir)
    dst = Path(output_dir)
    dst.mkdir(parents=True, exist_ok=True)

    injector = MutationInjector()

    for txt_file in src.glob('*.txt'):
        mappings = []
        with txt_file.open('r', encoding='utf-8') as f:
            lines = f.read().splitlines()

        for old in lines:
            new = injector.inject(old)
            mappings.append((old, new))

        out_file = dst / txt_file.name
        with out_file.open('w', encoding='utf-8') as f:
            f.write('old_defect\tnew_defect\n')
            for old, new in mappings:
                f.write(f"{old}\t{new}\n")

        print(f"Processed {txt_file.name}: {len(mappings)} entries written to {out_file}")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Defect Mutation Injector for a folder of txt files')
    parser.add_argument('input_dir', help='Path to folder JIT_defect containing various defect files')
    parser.add_argument('output_dir', help='Path to folder res to write mutated files')
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)