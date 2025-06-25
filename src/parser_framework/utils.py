def read_file_as_string(filename):
    """
    Reads the entire contents of a file and returns it as a single string.

    :param filename: Path to the file.
    :return: File content as a string.
    :raises ValueError: If the file cannot be read.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"Arquivo não encontrado: {filename}")
    except Exception as e:
        raise ValueError(f"Erro ao ler o arquivo '{filename}': {e}")
