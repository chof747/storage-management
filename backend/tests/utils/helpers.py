import random
import string


def generate_random_text(length: int) -> str:
    """generate random text in given length

    Args:
        length (int): length of the text

    Returns:
        str: random text
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    random_text = "".join(random.choices(characters, k=length))
    return random_text
