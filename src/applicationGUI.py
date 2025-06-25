import tkinter as tk
from src.application import Application
from tkinter import ttk, filedialog, scrolledtext, messagebox



class ApplicationGUI:
    def __init__(self, root, application: Application):
        self.root = root
        self.root.title("Lexical Analyzer and Syntax Analyzer GUI")
        self.root.geometry("1000x900")

        self.application = application

        self.er_file_path = tk.StringVar()
        self.glc_file_path = tk.StringVar()
        self.lexical_analyzer_name_entry_var = tk.StringVar()
        self.syntax_analyzer_name_var = tk.StringVar()
        self.save_dfa_var = tk.BooleanVar(value=False)
        self.save_parse_tree_var = tk.BooleanVar(value=False)
        self.current_lexical_analyzer_status = tk.StringVar(value="Current Scanner: None")
        self.current_syntax_analyzer_status = tk.StringVar(value="Current Parser: None")

        self._setup_styles()
        self._create_widgets()
        self._update_scanners_list()

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

        # --- Lexical Analyzer Setup ---
        top_frame = ttk.Labelframe(main_frame, text="Lexical Analyzer Setup", padding="10")
        top_frame.pack(fill=tk.X, pady=5)

        ttk.Label(top_frame, text="ER File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.file_path_entry = ttk.Entry(top_frame, textvariable=self.er_file_path, width=50, state="readonly")
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        self.load_er_button = ttk.Button(top_frame, text="📂 Load ER File", command=self._load_er_file)
        self.load_er_button.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(top_frame, text="Lexical Analyzer Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.lexical_analyzer_name_entry = ttk.Entry(top_frame, textvariable=self.lexical_analyzer_name_entry_var)
        self.lexical_analyzer_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.save_dfa_checkbutton = ttk.Checkbutton(top_frame, text="Save DFAs to files", variable=self.save_dfa_var)
        self.save_dfa_checkbutton.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.generate_button = ttk.Button(top_frame, text="⚙️ Generate Analyzer", command=self._generate_lexical_analyzer)
        self.generate_button.grid(row=1, column=3, padx=5, pady=5)

        top_frame.grid_columnconfigure(1, weight=1)


        # --- Syntax Analyzer Setup ---
        syntax_setup_frame = ttk.Labelframe(main_frame, text="Syntax Analyzer Setup", padding="10")
        syntax_setup_frame.pack(fill=tk.X, pady=5)

        ttk.Label(syntax_setup_frame, text="Grammar File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.grammar_file_entry = ttk.Entry(syntax_setup_frame, textvariable=self.glc_file_path, width=50, state="readonly")
        self.grammar_file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        self.load_grammar_button = ttk.Button(syntax_setup_frame, text="📂 Load Grammar File", command=self._load_grammar_file)
        self.load_grammar_button.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(syntax_setup_frame, text="Syntax Analyzer Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.syntax_analyzer_name_entry = ttk.Entry(syntax_setup_frame, textvariable=self.syntax_analyzer_name_var)
        self.syntax_analyzer_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.save_parse_tree_checkbutton = ttk.Checkbutton(syntax_setup_frame, text="Save Parse Trees", variable=self.save_parse_tree_var)
        self.save_parse_tree_checkbutton.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.generate_syntax_button = ttk.Button(syntax_setup_frame, text="⚙️ Generate Parser", command=self._generate_syntax_analyzer)
        self.generate_syntax_button.grid(row=1, column=3, padx=5, pady=5)

        syntax_setup_frame.grid_columnconfigure(1, weight=1)


        # --- Middle Section: Lexical + Syntax Management + Analysis ---
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Lexical Management
        lexical_mgmt_frame = ttk.Labelframe(middle_frame, text="Lexical Analyzer Management", padding="10")
        lexical_mgmt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))

        ttk.Label(lexical_mgmt_frame, text="Available Analyzers:", style="Header.TLabel")\
            .pack(pady=(0,5), anchor="w")
        self.lexical_analyzers_listbox = tk.Listbox(lexical_mgmt_frame, height=8, exportselection=False, font=('Courier', 10))
        self.lexical_analyzers_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        lex_scroll = ttk.Scrollbar(self.lexical_analyzers_listbox, orient=tk.VERTICAL, command=self.lexical_analyzers_listbox.yview)
        self.lexical_analyzers_listbox.configure(yscrollcommand=lex_scroll.set)
        lex_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        lex_btn_frame = ttk.Frame(lexical_mgmt_frame)
        lex_btn_frame.pack(fill=tk.X, pady=5)
        self.set_current_button = ttk.Button(lex_btn_frame, text="✔️ Set Current", command=self._set_current_lexical_analyzer)
        self.set_current_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        self.info_button = ttk.Button(lex_btn_frame, text="ℹ️ Show Info", command=self._show_lexical_analyzer_info)
        self.info_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        self.delete_button = ttk.Button(lex_btn_frame, text="🗑️ Delete", command=self._delete_lexical_analyzer)
        self.delete_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)


        # Syntax Management
        syntax_mgmt_frame = ttk.Labelframe(middle_frame, text="Syntax Analyzer Management", padding="10")
        syntax_mgmt_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(syntax_mgmt_frame, text="Available Parsers:", style="Header.TLabel")\
            .pack(pady=(0,5), anchor="w")
        self.parsers_listbox = tk.Listbox(syntax_mgmt_frame, height=8, exportselection=False, font=('Courier', 10))
        self.parsers_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        syn_scroll = ttk.Scrollbar(self.parsers_listbox, orient=tk.VERTICAL, command=self.parsers_listbox.yview)
        self.parsers_listbox.configure(yscrollcommand=syn_scroll.set)
        syn_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        syn_btn_frame = ttk.Frame(syntax_mgmt_frame)
        syn_btn_frame.pack(fill=tk.X, pady=5)
        self.set_current_syntax_btn = ttk.Button(syn_btn_frame, text="✔️ Set Current", command=self._set_current_syntax_analyzer)
        self.set_current_syntax_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        self.syntax_info_btn = ttk.Button(syn_btn_frame, text="ℹ️ Show Info", command=self._show_syntax_analyzer_info)
        self.syntax_info_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        self.delete_syntax_btn = ttk.Button(syn_btn_frame, text="🗑️ Delete", command=self._delete_syntax_analyzer)
        self.delete_syntax_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)


        # Analysis Pane (shared)
        analysis_frame = ttk.Labelframe(middle_frame, text="Analysis", padding="10")
        analysis_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))

        ttk.Label(analysis_frame, text="Input String:", style="Header.TLabel")\
            .pack(pady=(0,5), anchor="w")
        self.input_string_entry = ttk.Entry(analysis_frame, width=40)
        self.input_string_entry.pack(fill=tk.X, pady=5)
        self.input_string_entry.bind("<Return>", lambda e: self._analyze_string())

        self.analyze_button = ttk.Button(analysis_frame, text="▶️ Analyze String", command=self._analyze_string)
        self.analyze_button.pack(fill=tk.X, pady=5)

        ttk.Label(analysis_frame, textvariable=self.current_lexical_analyzer_status,
                  style="Status.TLabel").pack(pady=5, anchor="w")


        # --- Output & Logs ---
        log_frame = ttk.Labelframe(main_frame, text="Output & Logs", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=10, width=80, state=tk.DISABLED, wrap=tk.WORD, font=('Courier', 9)
        )
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

    def _load_grammar_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Grammar File",
            filetypes=(("Grammar files", "*.txt *.glc *.cfg"), ("All files", "*.*"))
        )
        if filepath:
            self.glc_file_path.set(filepath)
            self.log(f"Selected Grammar file: {filepath}")
        else:
            self.log("Grammar file selection cancelled.")

    def _generate_lexical_analyzer(self):
        filepath = self.er_file_path.get()
        if not filepath:
            self.error("Please load an ER file first.")
            return
        
        lexical_analyzer_name_input = self.lexical_analyzer_name_entry_var.get().strip()
        if not lexical_analyzer_name_input:
            self.error("Please enter a name for the analyzer.")
            return
        
        save_dfas_to_file = self.save_dfa_var.get()
        self.application.sg_framework.set_save_to_file(save_dfas_to_file)
        
        lexical_analyzer_name = self.application.sg_framework.generate_lexical_analyzer(filepath, lexical_analyzer_name_input)
        
        if lexical_analyzer_name:
            self._log_message(f"Lexical Analyzer '{lexical_analyzer_name}' generated successfully.", "SUCCESS")
            self._update_scanners_list()
            try:
                idx = self.lexical_analyzers_listbox.get(0, tk.END).index(lexical_analyzer_name)
                self.lexical_analyzers_listbox.selection_clear(0, tk.END)
                self.lexical_analyzers_listbox.selection_set(idx)
                self.lexical_analyzers_listbox.activate(idx)
                self.lexical_analyzers_listbox.see(idx)
            except ValueError:
                pass
            self._update_current_lexical_analyzer_status()

    def _generate_syntax_analyzer(self):
        #TODO:
        pass

    def _update_scanners_list(self):
        self.lexical_analyzers_listbox.delete(0, tk.END)
        analyzers = self.application.sg_framework.get_loaded_lexical_analyzers()
        print("Loaded scanners:", analyzers)
        if analyzers:
            for name in sorted(analyzers):
                self.lexical_analyzers_listbox.insert(tk.END, name)
        else:
            self.lexical_analyzers_listbox.insert(tk.END, "(No analyzers loaded)")
        self._update_current_lexical_analyzer_status()

    def _update_parsers_list(self):
        self.parsers_listbox.delete(0, tk.END)
        analyzers = self.application.pg_framework.get_loaded_parsers()
        print("Loaded parsers:", analyzers)
        if analyzers:
            for name in sorted(analyzers):
                self.parsers_listbox.insert(tk.END, name)
        else:
            self.parsers_listbox.insert(tk.END, "(No analyzers loaded)")
        self._update_current_lexical_analyzer_status()

    def _get_selected_lexical_analyzer_name(self):
        selected_indices = self.lexical_analyzers_listbox.curselection()
        if not selected_indices:
            return None
        return self.lexical_analyzers_listbox.get(selected_indices[0])

    def _get_selected_syntax_analyzer_name(self):
        selected_indices = self.parsers_listbox.curselection()
        if not selected_indices:
            return None
        return self.parsers_listbox.get(selected_indices[0])

    def _set_current_lexical_analyzer(self):
        lexical_analyzer_name = self._get_selected_lexical_analyzer_name()
        if lexical_analyzer_name == "(No analyzers loaded)":
            self.error("No analyzers available to set as current.")
            return
        if lexical_analyzer_name:
            if self.application.sg_framework.set_current_lexical_analyzer(lexical_analyzer_name):
                self._log_message(f"'{lexical_analyzer_name}' is now the current analyzer.", "INFO")
            self._update_current_lexical_analyzer_status()
        else:
            self.error("Please select an analyzer from the list to set as current.")

    def _set_current_syntax_analyzer(self):
        selected_indices = self.parsers_listbox.curselection()
        if not selected_indices:
            self.error("Please select a parser from the list to set as current.")
            return

        parser_name = self.parsers_listbox.get(selected_indices[0])
        if parser_name == "(No parsers loaded)":
            self.error("No parsers available to set as current.")
            return

        if self.application.pg_framework.set_current_parser(parser_name):
            self._log_message(f"'{parser_name}' is now the current parser.", "INFO")
            self.current_syntax_analyzer_status.set(f"Current Parser: {parser_name}")
        else:
            self.error(f"Could not set '{parser_name}' as current parser.")

    def _show_lexical_analyzer_info(self):
        lexical_analyzer_name = self._get_selected_lexical_analyzer_name()
        if lexical_analyzer_name == "(No analyzers loaded)":
            self.error("No analyzers available to show info for.")
            return
        if lexical_analyzer_name:
            info = self.application.sg_framework.get_lexical_analyzer_info(lexical_analyzer_name)
            if info:
                self.log(info)
            else:
                self.error(f"Could not retrieve info for '{lexical_analyzer_name}'.")
        else:
            self.error("Please select an analyzer from the list to show its info.")

    def _show_syntax_analyzer_info(self):
        selected_indices = self.parsers_listbox.curselection()
        if not selected_indices:
            self.error("Please select a parser from the list to show its info.")
            return

        parser_name = self.parsers_listbox.get(selected_indices[0])
        if parser_name == "(No parsers loaded)":
            self.error("No parsers available to show info for.")
            return

        info = self.application.pg_framework.get_parser_info(parser_name)
        if info:
            self.log(info)
        else:
            self.error(f"Could not retrieve info for '{parser_name}'.")

    def _delete_lexical_analyzer(self):
        lexical_analyzer_name = self._get_selected_lexical_analyzer_name()
        if lexical_analyzer_name == "(No analyzers loaded)":
            self.error("No analyzers available to delete.")
            return
        if lexical_analyzer_name:
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the lexical analyzer '{lexical_analyzer_name}'?"):
                if self.application.sg_framework.delete_lexical_analyzer(lexical_analyzer_name):
                    self._log_message(f"Analyzer '{lexical_analyzer_name}' deleted.", "INFO")
                self._update_scanners_list()
        else:
             self.error("Please select an analyzer from the list to delete.")

    def _delete_syntax_analyzer(self):
        syntax_analyzer_name = self._get_selected_syntax_analyzer_name()
        if syntax_analyzer_name == "(No analyzers loaded)":
            self.error("No analyzers available to delete.")
            return
        if syntax_analyzer_name:
            if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the syntax analyzer '{syntax_analyzer_name}'?"):
                if self.application.sg_framework.delete_lexical_analyzer(syntax_analyzer_name):
                    self._log_message(f"Analyzer '{syntax_analyzer_name}' deleted.", "INFO")
                self._update_scanners_list()
        else:
             self.error("Please select an analyzer from the list to delete.")


    def _analyze_string(self):
        input_str = self.input_string_entry.get()
        if not self.application.sg_framework.get_current_lexical_analyzer():
            self.error("No current lexical analyzer selected. Please generate or set one.")
            return
        if not input_str:
            pass

        self.application.analyze(input_str)

        self._update_current_lexical_analyzer_status()

    def _update_current_lexical_analyzer_status(self):
        current_lexical_analyzer = self.application.sg_framework.get_current_lexical_analyzer()
        if current_lexical_analyzer:
            self.current_lexical_analyzer_status.set(f"Current Analyzer: {current_lexical_analyzer}")
        else:
            self.current_lexical_analyzer_status.set("Current Analyzer: None")

    def run(self):
        self.root.mainloop()
