from src.application import Application
from src.applicationGUI import ApplicationGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = Application()
    gui = ApplicationGUI(root, app)
    gui.run()
