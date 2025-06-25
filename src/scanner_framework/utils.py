def parse_entries(filename):
    """
        def-reg1: ER1
        def-reg2: ER2
        ...
        def-regn: ERn
    {def-regn: ERn, ...}
    """
    result = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
    except FileNotFoundError:
        raise ValueError(f"Arquivo não encontrado: {filename}")
    except Exception as e:
        raise ValueError(f"Erro ao ler o arquivo '{filename}': {e}")
    return result
