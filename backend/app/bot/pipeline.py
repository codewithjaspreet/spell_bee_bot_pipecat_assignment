import asyncio
import os
from dotenv import load_dotenv

from loguru import logger

from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.audio.vad_processor import VADProcessor
from pipecat.processors.frame_processor import FrameDirection

from pipecat.transports.daily.transport import DailyParams, DailyTransport

from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService

from pipecat.turns.user_start import VADUserTurnStartStrategy
from pipecat.turns.user_stop import TurnAnalyzerUserTurnStopStrategy
from pipecat.turns.user_turn_processor import UserTurnProcessor
from pipecat.turns.user_turn_strategies import UserTurnStrategies

from app.bot.processors import SpellBeeGameProcessor

load_dotenv()


async def create_spellbee_pipeline():
    room_url = os.getenv("DAILY_SAMPLE_ROOM_URL")
    if not room_url:
        logger.error("DAILY_SAMPLE_ROOM_URL is not set; bot cannot join a Daily room.")

    transport = DailyTransport(
        token=None,
        room_url=room_url,
        bot_name="SpellBeeBot",
        params=DailyParams(
            api_key=os.getenv("DAILY_API_KEY"),
            audio_in_enabled=True,
            audio_out_enabled=True,
            camera_out_enabled=False,
        ),
    )

    vad_analyzer = SileroVADAnalyzer(
        params=VADParams(
            start_secs=0.2,
            stop_secs=0.8,
        )
    )
    vad_processor = VADProcessor(vad_analyzer=vad_analyzer)

    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        settings=DeepgramSTTService.Settings(
            model="nova-3-general",
            language="en",
            punctuate=True,
            smart_format=True,
        ),
    )

    turn_processor = UserTurnProcessor(
        user_turn_strategies=UserTurnStrategies(
            start=[
                VADUserTurnStartStrategy(
                    enable_interruptions=True,
                    enable_user_speaking_frames=True,
                ),
            ],
            stop=[
                TurnAnalyzerUserTurnStopStrategy(
                    turn_analyzer=LocalSmartTurnAnalyzerV3(),
                ),
            ],
        ),
    )

    tts = DeepgramTTSService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        settings=DeepgramTTSService.Settings(
            voice="aura-2-helena-en",
        ),
    )

    spellbee_processor = SpellBeeGameProcessor()

    pipeline = Pipeline(
        [
            transport.input(),
            vad_processor,
            stt,
            turn_processor,
            spellbee_processor,
            tts,
            transport.output(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(enable_metrics=True),
    )

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        await asyncio.sleep(1.5)
        first_message = spellbee_processor.start_game()
        await task.queue_frame(TextFrame(first_message), FrameDirection.UPSTREAM)

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await task.cancel()

    runner = PipelineRunner(handle_sigint=True)
    await runner.run(task)
