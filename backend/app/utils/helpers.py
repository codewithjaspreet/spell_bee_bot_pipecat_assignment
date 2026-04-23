def normalize(text: str) -> str:
    text = text.lower().strip()

    # remove punctuation
    for ch in [".", ",", "-", "_"]:
        text = text.replace(ch, "")

    # remove spaces (handles "m a n g o")
    text = text.replace(" ", "")

    return text