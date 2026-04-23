import asyncio
import os
from dotenv import load_dotenv

from pipecat.frames.frames import TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.services.google.gemini_live.llm import GeminiLiveLLMService
from app.bot.processors import SpellBeeGameProcessor

load_dotenv()


async def create_spellbee_pipeline():
    # --- Transport (Daily WebRTC) ---
    transport = DailyTransport(
        token=None,  # public room
        room_url=os.getenv("DAILY_SAMPLE_ROOM_URL"),
        bot_name="SpellBeeBot",
        params=DailyParams(
            api_key=os.getenv("DAILY_API_KEY"),
            audio_in_enabled=True,
            audio_out_enabled=True,
            camera_out_enabled=False
        ),
    )

    # --- Services ---
    stt = DeepgramSTTService(
        
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        settings=DeepgramSTTService.Settings(
            
            model="nova-3-general",
            language="en",
            punctuate=True,
            smart_format=True,
        ),
    )

    tts = DeepgramTTSService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        settings=DeepgramTTSService.Settings(
            voice="aura-2-helena-en",
        ),
    )

    # llm = GeminiLiveLLMService(
    #     api_key=os.getenv("GOOGLE_API_KEY"),
    #     settings=GeminiLiveLLMService.Settings(
    #         system_instruction="""
    #             You are a Spell Bee game host.

    #             Rules:
    #             - Give a word to spell
    #             - Wait for user spelling
    #             - Check correctness
    #             - Respond with correct/wrong
    #             - Give next word

    #             Keep responses short.
    #             """
    #                 ),
    #             )

    # context = LLMContext([
    # {
    #     "role": "user",
    #     "content": "Start the spell bee game",
    # }
    # ])

    # user_agg, assistant_agg = LLMContextAggregatorPair(
    #     context,
    #     user_params=LLMUserAggregatorParams()
    # )

    # --- Game Processor ---
    spellbee_processor = SpellBeeGameProcessor()

    # --- Pipeline ---
    pipeline = Pipeline(
        [
            transport.input(),
            stt,
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
        print("🔥 Triggering welcome message")

        # Wait until pipeline + TTS fully stable
        await asyncio.sleep(1.5)

        first_message = spellbee_processor.start_game()

        await task.queue_frames([TextFrame(first_message)])
        # --- Event: User leaves ---
    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        await task.cancel()

    # --- Run pipeline ---
    runner = PipelineRunner(handle_sigint=True)

    await runner.run(task)

