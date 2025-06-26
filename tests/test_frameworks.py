import os
import sys
from typing import List, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, PROJECT_ROOT)

class MockConfig:
    LEXICAL_ANALYZER_DEFAULT_NAME = "MyLexer"
    SYNTAX_ANALYZER_DEFAULT_NAME = "MyParser"

config = MockConfig()

try:

    from src.parser_framework.pg_framework import PgFramework
    from src.scanner_framework.sg_framework import SgFramework
except ImportError as e:
    print(f"Error importing frameworks: {e}")
    print("Please ensure your project structure is:")
    print("project_root/")
    print("├── src/")
    print("│   ├── parser_framework/")
    print("│   │   └── pg_framework.py")
    print("│   └── scanner_framework/")
    print("│       └── sg_framework.py")
    print("└── tests/")
    print("    └── test_frameworks.py")
    sys.exit(1)

# --- Mock Application Class ---
class MockApplication:
    """
    A mock application class to satisfy the dependency of SgFramework and PgFramework.
    It provides basic logging functionality to the console.
    """
    def __init__(self, gui_logger=None):
        self.gui_logger = gui_logger

        pass

    def log(self, message: str, level: str = "NORMAL"):
        """Logs a message, either via a GUI logger or to the console."""
        if self.gui_logger:
            self.gui_logger._log_message(message, level)
        else:
            print(f"LOG ({level}): {message}")

    def error(self, message: str):
        """Logs an error message, either via a GUI logger or to the console."""
        if self.gui_logger:
            self.gui_logger.error(message) # Use the GUI's error method for dialog
        else:
            print(f"ERROR: {message}")

    def warning(self, message: str):
        """Logs a warning message, either via a GUI logger or to the console."""
        if self.gui_logger:
            self.gui_logger.warning(message) # Use the GUI's warning method for dialog
        else:
            print(f"WARNING: {message}")


def run_framework_test(test_case_name: str, expect_success: bool = True):
    """
    Runs a complete test for the scanner and parser frameworks using
    files from a specified test case directory.

    Args:
        test_case_name (str): The name of the test case, which corresponds
                              to a subdirectory in project_root/tests/test_data/.
    """
    parse_result = None

    print(f"\n--- Running test case: '{test_case_name}' ---")

    test_data_dir = os.path.join(PROJECT_ROOT, "tests", "test_data", test_case_name)

    regex_file = os.path.join(test_data_dir, "regex.txt")
    grammar_file = os.path.join(test_data_dir, "grammar.txt")
    entry_file = os.path.join(test_data_dir, "entry.txt")

    # Check if all required files exist
    if not all(os.path.exists(f) for f in [regex_file, grammar_file, entry_file]):
        print(f"Error: Missing one or more required test files in {test_data_dir}")
        print(f"Expected files: {os.path.basename(regex_file)}, {os.path.basename(grammar_file)}, {os.path.basename(entry_file)}")
        print("Please ensure your test data structure is:")
        print("project_root/")
        print("└── tests/")
        print("    ├── test_frameworks.py")
        print(f"    └── test_data/")
        print(f"        └── {test_case_name}/")
        print(f"            ├── regex.txt")
        print(f"            ├── grammar.txt")
        print(f"            └── entry.txt")
        return

    # --- 1. Initialize Mock Application and Frameworks ---
    print("\nInitializing mock application and frameworks...")

    mock_app = MockApplication()

    scanner_framework = SgFramework(mock_app)
    parser_framework = PgFramework(mock_app)
    print("Mock application and frameworks initialized.")

    # --- 2. Generate Lexical Analyzer (Scanner) ---
    print(f"Generating lexical analyzer from: {regex_file}")
    try:
        scanner_framework.generate_lexical_analyzer(regex_file)
        print(f"Lexical analyzer '{config.LEXICAL_ANALYZER_DEFAULT_NAME}' generated successfully.")
    except Exception as e:
        print(f"Error generating lexical analyzer: {e}")
        return

    # --- 3. Generate Parser ---
    print(f"Generating parser from: {grammar_file}")
    try:
        parser_framework.generate(grammar_file)
        print(f"Parser '{config.SYNTAX_ANALYZER_DEFAULT_NAME}' generated successfully.")
    except Exception as e:
        print(f"Error generating parser: {e}")
        return

    # --- 4. Read Entry Text ---
    print(f"Reading entry text from: {entry_file}")
    try:
        with open(entry_file, 'r', encoding='utf-8') as f:
            entry_text = f.read()
        print("Entry text loaded.")
    except IOError as e:
        print(f"Error reading entry file: {e}")
        return

    # --- 5. Analyze Text with Scanner ---
    print("\nAnalyzing entry text with the generated lexical analyzer...")
    try:
        tokens: List[Tuple[str, str]] = scanner_framework.analyze(entry_text)
        print("Lexical analysis complete. Generated tokens:")
        for token_type, token_value in tokens:
            print(f"  ({token_type}, '{token_value}')")
    except Exception as e:
        print(f"Error during lexical analysis: {e}")
        return

    # --- 6. Parse Tokens with Parser ---
    print("\nParsing tokens with the generated parser...")
    try:
        parse_result = parser_framework.parse(tokens, verbose=True)
        print("Parsing complete. Parser result:")

        print(parse_result)
    except Exception as e:
        print(f"\nError during parsing: {e}")
        return
    
    if (parse_result is None or not parse_result) and expect_success:
        print(f"\nTest case '{test_case_name}' FAILED: No parse result returned.")
        return
    
    if parse_result and not expect_success:
        print(f"\nTest case '{test_case_name}' FAILED: Expected failure but got a parse result.")
        return
    
    if expect_success:
        print(f"\nTest case '{test_case_name}' PASSED: Parse result returned successfully.")


    print(f"--- Test case '{test_case_name}' finished. ---\n")


if __name__ == "__main__":

    run_framework_test("test1", True)

    run_framework_test("aritmetica", True)

    run_framework_test("test2", True)

