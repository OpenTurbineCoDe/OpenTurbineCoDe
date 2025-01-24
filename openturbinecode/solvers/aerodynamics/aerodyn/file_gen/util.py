
def add_line(contents: str, value: str, identifier: str, description: str):
    """Add a line to the configuration file."""
    return contents + f"{value:>20}   {identifier:<14} - {description}\n"


def add_header(contents: str, header: str):
    """Add a header to the configuration file."""
    return contents + f"===== {header} {'='*(80-len(header))}\n"


def add_table_entry(contents: str, header_cols: list):
    """Add a table header to the configuration file."""
    return contents + " ".join([f"{col:<14}" for col in header_cols]) + "\n"


def add_word(contents: str, word: str):
    """Add a word to the configuration file."""
    return contents + f"{word}\n"
