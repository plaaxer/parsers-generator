import pprint
from typing import List, Tuple
import src.parser_framework.config as config

class SLRParser:
    """
    Um analisador sintático SLR que utiliza uma tabela de parsing gerada
    para validar uma cadeia de tokens.
    """
    def __init__(self, parsing_table, name):
        """
        Inicializa o parser com a tabela de parsing gerada.
        """
        if not all(k in parsing_table for k in ['action', 'goto', 'productions']):
            raise ValueError("A tabela de parsing fornecida é inválida.")
        
        self.name = name
            
        self.action_table = parsing_table['action']
        self.goto_table = parsing_table['goto']
        self.productions = parsing_table['productions']
        self.start_state = 0

    def parse(self, tokens: List[Tuple[str, str]], verbose: bool = False):
        """
        Processa uma lista de tuplas (lexeme, token_type) de acordo com a gramática e a tabela SLR.
        Retorna True se a cadeia for aceita, levanta um ValueError em caso de erro.
        
        :param tokens: Uma lista de tuplas (lexeme, token_type) representando os tokens da entrada.
        :param verbose: Se True, imprime os passos da análise.
        """
        # --- ETAPA DE PRÉ-PROCESSAMENTO DA ENTRADA ---
        # Extrai os tipos de token para usar na lógica do parser
        token_types = [token[1] for token in tokens] + [config.END_OF_INPUT]
        # Mantém os lexemas originais para logs e mensagens de erro
        lexemes = [token[0] for token in tokens] + [config.END_OF_INPUT]
        
        stack = [self.start_state]
        input_ptr = 0

        if verbose:
            print(f"{'PILHA':<30} {'ENTRADA':<40} {'AÇÃO'}")
            print("-" * 80)

        while True:
            current_state = stack[-1]
            # Usa o TIPO de token para a lógica da tabela
            current_token_type = token_types[input_ptr]
            
            if verbose:
                stack_str = ' '.join(map(str, stack))
                # Mostra os LEXEMAS originais na fita de entrada para melhor legibilidade
                input_str = ' '.join(lexemes[input_ptr:])
                print(f"{stack_str:<30} {input_str:<40}", end="")

            # Consultar a tabela de ação usando o TIPO do token
            action = self.action_table[current_state].get(current_token_type)

            if action is None:
                # --- MENSAGEM DE ERRO MELHORADA ---
                # Usa o lexema original para uma mensagem mais clara
                unexpected_lexeme = lexemes[input_ptr]
                raise ValueError(
                    f"Erro de sintaxe: token inesperado '{unexpected_lexeme}' (tipo: {current_token_type}) no estado {current_state}."
                )

            # --- Ação de SHIFT ---
            if action[0] == 'shift':
                _, next_state = action
                stack.append(next_state)
                input_ptr += 1
                if verbose: print(f" Shift para o estado {next_state}")
            
            # --- Ação de REDUCE ---
            elif action[0] == 'reduce':
                _, prod_index = action
                head, body = self.productions[prod_index]
                
                # Pop da pilha (0 se for épsilon, len(body) caso contrário)
                if body != (config.EPSILON,):
                    for _ in body:
                        stack.pop()
                
                state_after_pop = stack[-1]
                # Consultar a tabela GOTO
                goto_state = self.goto_table[state_after_pop][head]
                stack.append(goto_state)
                if verbose: print(f" Reduzir por {head} -> {' '.join(body)}")

            # --- Ação de ACCEPT ---
            elif action[0] == 'accept':
                if verbose: print(" Aceito! Análise concluída.")
                return True
            
            else:
                # Isso não deve acontecer
                raise RuntimeError("Ação desconhecida na tabela de parsing.")
            
    def get_info(self):
        return f"Analisador Sintático: {self.name}\n{self.__repr__}"

    def __repr__(self):
        prod_str_list = []
        for i, (head, body) in enumerate(self.productions):
            body_str = ' '.join(body) if body else config.EPSILON
            prod_str_list.append(f"  {i}: {head} -> {body_str}")
        
        formatted_productions = "\n".join(prod_str_list)

        return (
            f"<SLRParser com {len(self.action_table)} estados>\n"
            f"=========================================\n\n"
            f"--- PRODUÇÕES NUMERADAS ---\n"
            f"{formatted_productions}\n\n"
            f"--- TABELA ACTION ---\n"
            f"{pprint.pformat(self.action_table, indent=2, width=120)}\n\n"
            f"--- TABELA GOTO ---\n"
            f"{pprint.pformat(self.goto_table, indent=2, width=120)}\n"
            f"========================================="
        )
