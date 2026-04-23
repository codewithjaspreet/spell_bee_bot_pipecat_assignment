

from typing_extensions import override

from pipecat.frames.frames import Frame, InterimTranscriptionFrame, TextFrame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from app.bot.state import get_game_state
from app.utils.helpers import normalize


class SpellBeeGameProcessor(FrameProcessor):
    def __init__(self):
        super().__init__()
        self.game_state = get_game_state()

    def start_game(self) -> str:
        word = self.game_state.next_word()
        return f"Welcome to Spell Bee! ... Your first word is: {word}"

    @override
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            user_input = frame.text.strip()
            print("🎤 USER SAID:", user_input)

            if not user_input:
                return

            response = self.manage_spelling(user_input)
            print("🧠 BOT RESPONDS:", response)

            await self.push_frame(TextFrame(response), direction)
            return

        if isinstance(frame, InterimTranscriptionFrame):
            return

        await self.push_frame(frame, direction)

    def manage_spelling(self, user_input: str):
        correct_word = self.game_state.current_word.lower()
        normalized_input = normalize(user_input)

        if "repeat" in user_input.lower():
            return f"The word is: {self.game_state.current_word}"

        if normalized_input == correct_word or user_input.lower() == correct_word:
            next_word = self.game_state.next_word()
            return f"Correct! ... Next word is: {next_word}"

        else:
            word_asked = self.game_state.current_word
            next_word = self.game_state.next_word()
            return f"Wrong. The correct spelling is {word_asked}. ... Next word is: {next_word}"

