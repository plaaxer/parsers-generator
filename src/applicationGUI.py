import tkinter as tk
from src.application import Application
from tkinter import ttk, filedialog, scrolledtext, messagebox



class ApplicationGUI:
    def __init__(self, root, application: Application):
        self.root = root
        self.root.title("Lexical Analyzer Generator GUI")
        self.root.geometry("800x700")

        self.application = application

        self.er_file_path = tk.StringVar()
        self.analyzer_name_entry_var = tk.StringVar()
        self.save_dfa_var = tk.BooleanVar(value=False)
        self.current_analyzer_status = tk.StringVar(value="Current Analyzer: None")

        self._setup_styles()
        self._create_widgets()
        self._update_analyzers_list()

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'alt', 'default', 'classic', 'vista', 'xpnative'

        self.style.configure("TLabel", padding=5, font=('Helvetica', 10))
        self.style.configure("TButton", padding=5, font=('Helvetica', 10))
        self.style.configure("TEntry", padding=5, font=('Helvetica', 10))
        self.style.configure("TFrame", padding=10)
        self.style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))
        self.style.configure("Status.TLabel", font=('Helvetica', 9, 'italic'))

    def _create_widgets(self):

        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        top_frame = ttk.Labelframe(main_frame, text="Lexical Analyzer Setup", padding="10")
        top_frame.pack(fill=tk.X, pady=5)

        ttk.Label(top_frame, text="ER File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_path_entry = ttk.Entry(top_frame, textvariable=self.er_file_path, width=50, state="readonly")
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2) # Span 2 cols
        self.load_er_button = ttk.Button(top_frame, text="📂 Load ER File", command=self._load_er_file)
        self.load_er_button.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(top_frame, text="Analyzer Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.analyzer_name_entry = ttk.Entry(top_frame, textvariable=self.analyzer_name_entry_var)
        self.analyzer_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.save_dfa_checkbutton = ttk.Checkbutton(top_frame, text="Save DFAs to files", variable=self.save_dfa_var)
        self.save_dfa_checkbutton.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.generate_button = ttk.Button(top_frame, text="⚙️ Generate Analyzer", command=self._generate_analyzer)
        self.generate_button.grid(row=1, column=3, padx=5, pady=5)
        
        top_frame.grid_columnconfigure(1, weight=1)

        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        management_frame = ttk.Labelframe(middle_frame, text="Analyzer Management", padding="10")
        management_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        ttk.Label(management_frame, text="Available Analyzers:", style="Header.TLabel").pack(pady=(0,5), anchor="w")
        self.analyzers_listbox = tk.Listbox(management_frame, height=8, exportselection=False, font=('Courier', 10))
        self.analyzers_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        analyzer_scrollbar = ttk.Scrollbar(self.analyzers_listbox, orient=tk.VERTICAL, command=self.analyzers_listbox.yview)
        self.analyzers_listbox.configure(yscrollcommand=analyzer_scrollbar.set)
        analyzer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        mng_button_frame = ttk.Frame(management_frame)
        mng_button_frame.pack(fill=tk.X, pady=5)

        self.set_current_button = ttk.Button(mng_button_frame, text="✔️ Set Current", command=self._set_current_analyzer)
        self.set_current_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        self.info_button = ttk.Button(mng_button_frame, text="ℹ️ Show Info", command=self._show_analyzer_info)
        self.info_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        self.delete_button = ttk.Button(mng_button_frame, text="🗑️ Delete", command=self._delete_analyzer)
        self.delete_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)


        analysis_frame = ttk.Labelframe(middle_frame, text="Analysis", padding="10")
        analysis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))

        ttk.Label(analysis_frame, text="Input String:", style="Header.TLabel").pack(pady=(0,5), anchor="w")
        self.input_string_entry = ttk.Entry(analysis_frame, width=40)
        self.input_string_entry.pack(fill=tk.X, pady=5)
        self.input_string_entry.bind("<Return>", lambda event: self._analyze_string())

        self.analyze_button = ttk.Button(analysis_frame, text="▶️ Analyze String", command=self._analyze_string)
        self.analyze_button.pack(fill=tk.X, pady=5)
        
        ttk.Label(analysis_frame, textvariable=self.current_analyzer_status, style="Status.TLabel").pack(pady=5, anchor="w")

        log_frame = ttk.Labelframe(main_frame, text="Output & Logs", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, state=tk.DISABLED, wrap=tk.WORD, font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("SUCCESS", foreground="green")


    def _log_message(self, message: str, level: str = "NORMAL"):
        self.log_text.configure(state=tk.NORMAL)
        if self.log_text.index('end-1c') != "1.0":
                self.log_text.insert(tk.END, "\n")
        self.log_text.insert(tk.END, f"{message}", level.upper())
        self.log_text.configure(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def log(self, message: str):
        self._log_message(message, "NORMAL")

    def error(self, message: str):
        self._log_message(f"ERROR: {message}", "ERROR")
        messagebox.showerror("Error", message)

    def warning(self, message: str):
        self._log_message(f"WARNING: {message}", "WARNING")
        messagebox.showwarning("Warning", message)

    def _load_er_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Regular Expressions File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filepath:
            self.er_file_path.set(filepath)
            self.log(f"Selected ER file: {filepath}")
        else:
            self.log("File selection cancelled.")

    def _generate_analyzer(self):
        filepath = self.er_file_path.get()
        if not filepath:
            self.error("Please load an ER file first.")
            return
        
        analyzer_name_input = self.analyzer_name_entry_var.get().strip()
        if not analyzer_name_input:
            self.error("Please enter a name for the analyzer.")
            return
        
        save_dfas_to_file = self.save_dfa_var.get()
        self.application.ag_framework.set_save_to_file(save_dfas_to_file)
        
        analyzer_name = self.application.ag_framework.generate_lexical_analyzer(filepath, analyzer_name_input)
        
        if analyzer_name:
            self._log_message(f"Lexical Analyzer '{analyzer_name}' generated successfully.", "SUCCESS")
            self._update_analyzers_list()
            try:
                idx = self.analyzers_listbox.get(0, tk.END).index(analyzer_name)
                self.analyzers_listbox.selection_clear(0, tk.END)
                self.analyzers_listbox.selection_set(idx)
                self.analyzers_listbox.activate(idx)
                self.analyzers_listbox.see(idx)
            except ValueError:
                pass
            self._update_current_analyzer_status()

    def _update_analyzers_list(self):
        self.analyzers_listbox.delete(0, tk.END)
        analyzers = self.application.ag_framework.get_loaded_lexical_analyzers()
        print("Loaded analyzers:", analyzers)
        if analyzers:
            for name in sorted(analyzers):
                self.analyzers_listbox.insert(tk.END, name)
        else:
            self.analyzers_listbox.insert(tk.END, "(No analyzers loaded)")
        self._update_current_analyzer_status()


    def _get_selected_analyzer_name(self):
        selected_indices = self.analyzers_listbox.curselection()
        if not selected_indices:
            return None
        return self.analyzers_listbox.get(selected_indices[0])

    def _set_current_analyzer(self):
        analyzer_name = self._get_selected_analyzer_name()
        if analyzer_name == "(No analyzers loaded)":
            self.error("No analyzers available to set as current.")
            return
        if analyzer_name:
            if self.application.ag_framework.set_current_lexical_analyzer(analyzer_name):
                self._log_message(f"'{analyzer_name}' is now the current analyzer.", "INFO")
            self._update_current_analyzer_status()
        else:
            self.error("Please select an analyzer from the list to set as current.")


    def _show_analyzer_info(self):
        analyzer_name = self._get_selected_analyzer_name()
        if analyzer_name == "(No analyzers loaded)":
            self.error("No analyzers available to show info for.")
            return
        if analyzer_name:
            info = self.application.ag_framework.get_lexical_analyzer_info(analyzer_name)
            if info:
                self.log(info)
            else:
                self.error(f"Could not retrieve info for '{analyzer_name}'.")
        else:
            self.error("Please select an analyzer from the list to show its info.")

    def _delete_analyzer(self):
        analyzer_name = self._get_selected_analyzer_name()
        if analyzer_name == "(No analyzers loaded)":
            self.error("No analyzers available to delete.")
            return
        if analyzer_name:
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the lexical analyzer '{analyzer_name}'?"):
                if self.application.ag_framework.delete_lexical_analyzer(analyzer_name):
                    self._log_message(f"Analyzer '{analyzer_name}' deleted.", "INFO")
                self._update_analyzers_list()
        else:
             self.error("Please select an analyzer from the list to delete.")


    def _analyze_string(self):
        input_str = self.input_string_entry.get()
        if not self.application.ag_framework.get_current_lexical_analyzer():
            self.error("No current lexical analyzer selected. Please generate or set one.")
            return
        if not input_str:
            pass

        tokens = self.application.ag_framework.analyze(input_str)

        self._update_current_analyzer_status()

    def _update_current_analyzer_status(self):
        current_analyzer = self.application.ag_framework.get_current_lexical_analyzer()
        if current_analyzer:
            self.current_analyzer_status.set(f"Current Analyzer: {current_analyzer}")
        else:
            self.current_analyzer_status.set("Current Analyzer: None")

    def run(self):
        self.root.mainloop()
