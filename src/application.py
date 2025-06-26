from src.scanner_framework.sg_framework import SgFramework
from src.parser_framework.pg_framework import PgFramework


class Application:
    def __init__(self, gui_logger=None):
        self.gui_logger = gui_logger
        self.sg_framework = SgFramework(self)
        self.pg_framework = PgFramework(self)

    def analyze(self, input_str):
        try:
            self.log("Performing lexical analysis...")
            tokens = self.sg_framework.analyze(input_str)
            
            self.log("Performing syntax analysis...")
            valid = self.pg_framework.parse(tokens, verbose=True)
            
            if valid:
                self.log("Syntax analysis successful. Input accepted.", level="SUCCESS")
            else:
                self.error("Syntax analysis failed for an unknown reason.")

        except ValueError as e:
            self.error(f"Syntax analysis failed: {e}")
        except Exception as e:
            self.error(f"An unexpected error occurred during analysis: {e}")

    def log(self, message: str, level: str = "NORMAL"):
        if self.gui_logger:
            self.gui_logger._log_message(message, level)
        else:
            print(f"LOG: {message}")

    def error(self, message: str):
        if self.gui_logger:
            self.gui_logger.error(message) # Use the GUI's error method for dialog
        else:
            print(f"ERROR: {message}")

    def warning(self, message: str):
        if self.gui_logger:
            self.gui_logger.warning(message) # Use the GUI's warning method for dialog
        else:
            print(f"WARNING: {message}")

