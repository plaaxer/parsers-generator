import os
from src.scanner_framework.regex_processor import RegexProcessor
from src.scanner_framework.lexical_analyzer import LexicalAnalyzer
import src.scanner_framework.config as config
import src.scanner_framework.utils as utils

""""
Esta classe será a interface do framework de geração de analisadores léxicos.
No caso, ao menos por enquanto, Application será algum tipo de CLI, mas podemos adicionar uma interface gráfica depois.
"""

class SgFramework:
    def __init__(self, application):
        self.application = application
        self.loaded_lexical_analyzers = []
        self.current_lexical_analyzer = None
        self.save_to_file = True

    def generate_lexical_analyzer(self, ers_filename="ers.txt", name=config.LEXICAL_ANALYZER_DEFAULT_NAME) -> str | None:

        lexical_analyzer = LexicalAnalyzer(name, self.application)
        parsed_regexs = utils.parse_entries(ers_filename)

        for key, value in parsed_regexs.items():
            if not value:
                self.application.error(f"Erro ao processar a expressão regular: {key}")
                continue
            dfa = self._process_regular_expression(value, key)

            if not dfa:
                continue
            lexical_analyzer.add_dfa(key, dfa)

        self.application.log(f"Expressões regulares processadas com sucesso: {parsed_regexs}")

        lexical_analyzer.generate()

        if lexical_analyzer.has_errors:
            self.application.error("Erro ao gerar o analisador léxico.")
            return

        self.loaded_lexical_analyzers.append(lexical_analyzer)
        self.current_lexical_analyzer = lexical_analyzer
        self.application.log("Analisador léxico gerado com sucesso.\nAnalisadores léxicos carregados: " +
                             ", ".join([la.name for la in self.loaded_lexical_analyzers]))
        
        return lexical_analyzer.name

    def analyze(self, text, lexical_analyzer_name=None):
        if lexical_analyzer_name is None:
            lexical_analyzer = self.current_lexical_analyzer

        else:
            for la in self.loaded_lexical_analyzers:
                if la.name == lexical_analyzer_name:
                    self.application.log(f"Analisador léxico encontrado: {la.name}")
                    lexical_analyzer = la
                    break
        
        if lexical_analyzer is None:
            self.application.error("Nenhum analisador léxico carregado.")
            return

        try:
            result = lexical_analyzer.process(text)
            self.application.log(f"Análise realizada com sucesso: {result}")
            return result
        except Exception as e:
            self.application.error(f"Erro ao analisar o texto: {e}")

    def _process_regular_expression(self, regex, er_name="dfa"):
            try:
                dfa = RegexProcessor.regex_to_dfa(regex)
            except ValueError as e:
                self.application.error(f"Não foi possível processar a expressão regular: {e}")
                return

            self.application.log(f"Expressão regular {regex} convertida para autômato com sucesso.")

            if self.save_to_file:
                output_dir = "generated_afds"
                os.makedirs(output_dir, exist_ok=True)
                file_name = f"{er_name}.txt"
                file_path = os.path.join(output_dir, file_name)
                try:
                    with open(file_path, 'w') as f:
                        f.write(dfa.to_file_format())
                    self.application.log(f"DFA para {regex} salvo no arquivo: {file_name}")
                except Exception as e:
                    self.application.error(f"Erro ao salvar DFA no arquivo: {e}")

            return dfa

    def get_current_lexical_analyzer(self):
        return self.current_lexical_analyzer.name if self.current_lexical_analyzer else None
    
    def get_loaded_lexical_analyzers(self):
        loaded_str = [la.name for la in self.loaded_lexical_analyzers]
        return loaded_str if loaded_str else None
    
    def set_current_lexical_analyzer(self, analyzer_name: str) -> bool:
        for la in self.loaded_lexical_analyzers:
            if la.name == analyzer_name:
                self.current_lexical_analyzer = la
                self.application.log(f"Analisador léxico atual definido: {analyzer_name}")
                return True
        self.application.error(f"Analisador léxico '{analyzer_name}' não encontrado.")
        return False
    
    def delete_lexical_analyzer(self, analyzer_name: str) -> bool:
        for la in self.loaded_lexical_analyzers:
            if la.name == analyzer_name:
                self.loaded_lexical_analyzers.remove(la)
                if self.current_lexical_analyzer == la:
                    self.current_lexical_analyzer = None
                self.application.log(f"Analisador léxico '{analyzer_name}' removido com sucesso.")
                return True
        self.application.error(f"Analisador léxico '{analyzer_name}' não encontrado.")
        return False
    
    def get_lexical_analyzer_info(self, analyzer_name: str):
        for la in self.loaded_lexical_analyzers:
            if la.name == analyzer_name:
                return la.get_info()
        self.application.error(f"Analisador léxico '{analyzer_name}' não encontrado.")
        return None
    
    def set_save_to_file(self, save: bool):
        self.save_to_file = save
        if save:
            self.application.log("Configuração de salvar DFAs em arquivo ativada.")
        else:
            self.application.log("Configuração de salvar DFAs em arquivo desativada.")
