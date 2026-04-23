# WORDS = [
#     "apple",
#     "mango",
#     "computer",
#     "curelink",
#     "donald trump",
#     "argentina"
# ]


# class SpellBeeGameState:

#     def __init__(self):
#         self.reset()

#     def reset(self):
#         self.current_word = None
#         self.current_score = 0
#         self.rounds = 0
#         self.index = 0
#         self.correct_count = 0
#         self.wrong_count = 0

#     def next_word(self):
#         if self.index >= len(WORDS):
#             return None

#         self.current_word = WORDS[self.index]
#         self.index += 1
#         self.rounds += 1
#         return self.current_word

#     def check_spelling(self, input_word: str):
#         clean_input = input_word.strip().replace(" ", "").lower()
#         correct = self.current_word.replace(" ", "").lower()

#         if clean_input == correct:
#             self.current_score += 1
#             self.correct_count += 1   # ✅ track correct
#             return True

#         self.wrong_count += 1         # ✅ track wrong
#         return False

#     def get_stats(self):
#         return {
#             "rounds": self.rounds,
#             "score": self.current_score,
#             "correct": self.correct_count,
#             "wrong": self.wrong_count,
#             "current_word": self.current_word
#         }


# _GAME_STATE = SpellBeeGameState()


# def get_game_state() -> SpellBeeGameState:
#     return _GAME_STATE

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

    def reset(self):
        self.current_word = None
        self.current_score = 0
        self.rounds = 0
        self.index = 0
        self.correct_count = 0
        self.wrong_count = 0

    def next_word(self):
        if self.index >= len(WORDS):
            return None

        self.current_word = WORDS[self.index]
        self.index += 1
        self.rounds += 1
        return self.current_word

    def check_spelling(self, input_word: str):
        clean_input = input_word.strip().replace(" ", "").lower()
        correct = self.current_word.replace(" ", "").lower()

        if clean_input == correct:
            self.current_score += 1
            self.correct_count += 1
            return True

        self.wrong_count += 1
        return False

    def get_stats(self):
        return {
            "rounds": self.rounds,
            "score": self.current_score,
            "correct": self.correct_count,
            "wrong": self.wrong_count
        }


_GAME_STATE = SpellBeeGameState()


def get_game_state() -> SpellBeeGameState:
    return _GAME_STATE