from typing import Literal
import tiktoken


def count_tokens(
    text: str, model: Literal["gpt-4-turbo-preview", "gpt-3.5-turbo"]
) -> int:
    """
    Counts the number of tokens in the given text using the specified model.

    Args:
        text (str): The input text to count tokens from.
        model (Literal["gpt-4-turbo-preview", "gpt-3.5-turbo"]): The model to use for tokenization.

    Returns:
        int: The number of tokens.
    """
    enc = tiktoken.encoding_for_model(model)
    assert enc.decode(enc.encode(text)) == text

    return len(enc.encode(text))


def do_you_want_to_continue(
    text: str | int,
    model: Literal["gpt-4-turbo-preview", "gpt-3.5-turbo"],
    threshold: int,
    question: str = "Muitos tokens! Quer continuar? ",
) -> bool:
    """
    Checks if the number of tokens in the given text exceeds the threshold.
    Asks the user if they want to continue if the condition is met.

    Args:
        text (str | int): The text to count the tokens from or the number of tokens.
        model (Literal["gpt-4-turbo-preview", "gpt-3.5-turbo"]): The model to use for token counting.
        threshold (int): The maximum number of tokens allowed.
        question (str, optional): The question to ask the user. Defaults to "Muitos tokens! Quer continuar?".

    Returns:
        bool: True if the user wants to continue, False otherwise.
    """
    too_much_tokens: bool = False
    if isinstance(text, int):
        too_much_tokens = text >= threshold
    else:
        too_much_tokens = count_tokens(text, model) >= threshold

    if not too_much_tokens:
        return True

    if (
        input(question).strip().lower()
        not in "n not nao não nope no nein nunca nem tamaluco"
    ):
        return True

    return False
