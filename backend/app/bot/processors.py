
from typing_extensions import override
from pipecat.frames.frames import (
    Frame,
    InterimTranscriptionFrame,
    TranscriptionFrame,
    TextFrame,
    InterruptionFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from app.bot.state import get_game_state
from app.utils.helpers import normalize, spell_word


class SpellBeeGameProcessor(FrameProcessor):
    def __init__(self):
        super().__init__()
        self.game_state = get_game_state()
        self.buffer = ""  # stores partial user input across turns

    def start_game(self) -> str:
        word = self.game_state.next_word()
        if not word:
            return "No words available."

        return (
            f"Welcome to Spell Bee. "
            f"Your first word is {word}. "
            f"Spell it like: {spell_word(word)}"
        )

    @override
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        # reset buffer on interruption to avoid mixing inputs
        if isinstance(frame, InterruptionFrame):
            self.buffer = ""
            await self.push_frame(frame, direction)
            return

        # forward interim frames without processing
        if isinstance(frame, InterimTranscriptionFrame):
            await self.push_frame(frame, direction)
            return

        # handle final transcription input
        if isinstance(frame, TranscriptionFrame):
            user_input = frame.text.strip()
            if not user_input:
                await self.push_frame(frame, direction)
                return

            # accumulate input across pauses
            self.buffer += " " + user_input
            normalized_input = normalize(self.buffer)

            # wait until input is likely complete
            if not self.is_complete(normalized_input):
                await self.push_frame(frame, direction)
                return

            # process spelling once complete
            response = self.handle_spelling(normalized_input)

            # reset buffer after evaluation
            self.buffer = ""

            # send bot response downstream
            await self.push_frame(TextFrame(response), direction)

            # forward original frame to maintain pipeline integrity
            await self.push_frame(frame, direction)
            return

        # forward all other frames
        await self.push_frame(frame, direction)

    def is_complete(self, text: str) -> bool:
        if not self.game_state.current_word:
            return False

        clean_input = text.replace(" ", "")
        target = self.game_state.current_word.replace(" ", "")

        return len(clean_input) >= len(target)

    def handle_spelling(self, user_input: str) -> str:
        if not self.game_state.current_word:
            word = self.game_state.next_word()
            return (
                f"Welcome to Spell Bee. "
                f"Your first word is {word}. "
                f"Spell it like: {spell_word(word)}"
            )

        if "repeat" in user_input.lower():
            word = self.game_state.current_word
            return f"The word is {word}. Spell it like: {spell_word(word)}"

        normalized_input = normalize(user_input)
        is_correct = self.game_state.check_spelling(normalized_input)

        if is_correct:
            next_word = self.game_state.next_word()
            if not next_word:
                return "Great job!"

            return (
                f"Correct! "
                f"Next word is {next_word}. "
                f"Spell it like: {spell_word(next_word)}"
            )

        else:
            word_asked = self.game_state.current_word
            next_word = self.game_state.next_word()

            if not next_word:
                return (
                    f"Wrong. The correct spelling was {spell_word(word_asked)}. "
                    f"Game over."
                )

            return (
                f"Wrong. The correct spelling is {spell_word(word_asked)}. "
                f"Next word is {next_word}. "
                f"Spell it like: {spell_word(next_word)}"
            )
