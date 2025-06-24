from framework.pg_framework import PgFramework

if __name__ == "__main__":
    grammar_string = """
    E ::= E + T
    E ::= T
    T ::= T * F
    T ::= F
    F ::= ( E )
    F ::= id
    """

    reserved_words_list = []

    framework = PgFramework(application=None)
    framework.generate(grammar_string, reserved_words_list)
    framework.select_parser("Parser")
    framework.parse(["id", "+", "id"], verbose=True)