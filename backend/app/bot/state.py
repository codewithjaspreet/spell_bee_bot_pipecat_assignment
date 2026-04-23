
from app.bot.stats_hub import stats_hub

WORDS = [
    "apple",
    "mango",
    "computer",
    "curelink",
    "donald trump",
    "argentina"
]


class SpellBeeGameState:

    def __init__(self):
        self.reset()

    def _push_stats(self) -> None:
        stats_hub.emit_stats(self.get_stats())

    def reset(self):
        self.current_word = None
        self.current_score = 0
        self.rounds = 0
        self.index = 0
        self._push_stats()

    def next_word(self):
        if self.index >= len(WORDS):
            self._push_stats()
            return None

        self.current_word = WORDS[self.index]
        self.index += 1
        self.rounds += 1
        self._push_stats()
        return self.current_word

    def check_spelling(self, input_word: str):
        if not self.current_word:
            return False

        clean_input = input_word.strip().replace(" ", "").lower()
        correct = self.current_word.replace(" ", "").lower()

        if clean_input == correct:
            self.current_score += 1
            self._push_stats()
            return True

        return False

    def get_stats(self):
        return {
            "rounds": self.rounds,
            "score": self.current_score,
        }


_GAME_STATE = SpellBeeGameState()


def get_game_state() -> SpellBeeGameState:
    return _GAME_STATE