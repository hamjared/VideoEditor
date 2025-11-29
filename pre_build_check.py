#!/usr/bin/env python
"""
Pre-build check script for PyInstaller executables.

Run this before building to catch common issues that appear in frozen executables.
"""

import sys
import os
import ast
import re
from pathlib import Path


class PreBuildChecker:
    """Check code for common frozen executable issues."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.checked_files = 0

    def check_file(self, filepath):
        """Check a single Python file for issues."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        self.checked_files += 1
        self.check_print_statements(filepath, content)
        self.check_stdout_usage(filepath, content)
        self.check_subprocess_calls(filepath, content)

    def check_print_statements(self, filepath, content):
        """Check for print statements that might fail when stdout is None."""
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    # Found a print statement
                    self.warnings.append(
                        f"{filepath}:{node.lineno}: "
                        f"print() statement found - may fail in frozen GUI app. "
                        f"Consider using logging instead."
                    )

    def check_stdout_usage(self, filepath, content):
        """Check for direct stdout/stderr access."""
        patterns = [
            (r'sys\.stdout(?!.*is not None)', 'stdout'),
            (r'sys\.stderr(?!.*is not None)', 'stderr'),
            (r'sys\.stdin(?!.*is not None)', 'stdin'),
        ]

        for pattern, stream_name in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                # Check if it's a None check (which is good)
                line = content.split('\n')[line_num - 1]
                if 'is not None' not in line and 'is None' not in line:
                    self.warnings.append(
                        f"{filepath}:{line_num}: "
                        f"Direct sys.{stream_name} access - may be None in frozen app. "
                        f"Check for None first or use logging."
                    )

    def check_subprocess_calls(self, filepath, content):
        """Check for subprocess calls without explicit stdout/stderr."""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check if it's subprocess.run, subprocess.Popen, etc.
                if isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and
                        node.func.value.id == 'subprocess' and
                        node.func.attr in ['run', 'Popen', 'call', 'check_call']):

                        # Check if stdout/stderr are specified
                        has_stdout = False
                        has_stderr = False

                        for keyword in node.keywords:
                            if keyword.arg == 'stdout':
                                has_stdout = True
                            if keyword.arg == 'stderr':
                                has_stderr = True

                        if not (has_stdout and has_stderr):
                            self.warnings.append(
                                f"{filepath}:{node.lineno}: "
                                f"subprocess.{node.func.attr} without explicit stdout/stderr. "
                                f"May fail in frozen app. Add stdout=subprocess.PIPE, stderr=subprocess.PIPE"
                            )

    def check_project(self, root_dir='.'):
        """Check all Python files in the project."""
        print("[*] Checking for frozen executable compatibility issues...\n")

        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk(root_dir):
            # Skip test directories and virtual environments
            if any(skip in root for skip in ['tests', 'venv', '.venv', '__pycache__', 'build', 'dist']):
                continue

            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))

        # Check each file
        for filepath in python_files:
            self.check_file(filepath)

        # Print results
        print(f"[+] Checked {self.checked_files} Python files\n")

        if self.issues:
            print("[!] ISSUES FOUND (must fix before building):")
            for issue in self.issues:
                print(f"  - {issue}")
            print()

        if self.warnings:
            print("[!] WARNINGS (review before building):")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()

        if not self.issues and not self.warnings:
            print("[+] No issues found! Code looks good for frozen executable.\n")

        return len(self.issues) == 0

    def run_frozen_tests(self):
        """Run the frozen compatibility unit tests."""
        print("[*] Running frozen compatibility tests...\n")

        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/test_frozen_compatibility.py', '-v'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0


def main():
    """Run all pre-build checks."""
    print("=" * 70)
    print("PyInstaller Pre-Build Check")
    print("=" * 70)
    print()

    checker = PreBuildChecker()

    # Check code
    code_ok = checker.check_project()

    print()
    print("=" * 70)

    # Run tests if they exist
    if os.path.exists('tests/test_frozen_compatibility.py'):
        print()
        tests_ok = checker.run_frozen_tests()
        print()
        print("=" * 70)
    else:
        print("[i] Frozen compatibility tests not found (tests/test_frozen_compatibility.py)")
        tests_ok = True

    print()

    # Summary
    if code_ok and tests_ok:
        print("[+] All pre-build checks passed!")
        print()
        print("Next steps:")
        print("  1. Build executable: pyinstaller build.spec")
        print("  2. Test the executable manually")
        print("  3. Check for any runtime errors in the log file")
        return 0
    else:
        print("[!] Pre-build checks failed!")
        print()
        print("Please fix the issues above before building.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
