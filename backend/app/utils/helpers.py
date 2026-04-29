def normalize(text: str) -> str:
    text = text.lower().strip()

    for ch in [".", ",", "-", "_"]:
        text = text.replace(ch, "")


    text = text.replace(" ", "")

    return text


def spell_word(word: str) -> str:
    return " ".join(list(word.upper()))
