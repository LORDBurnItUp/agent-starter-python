import logging
import os
import time
import uuid

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    inference,
    metrics,
)
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import RAG system
from rag_system import RAGManager

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Initialize RAG Manager (can be disabled via environment variable)
ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() == "true"
rag_manager = RAGManager(
    enable_rag=ENABLE_RAG,
    auto_improve=True,
    improvement_interval_conversations=100,
)


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.""",
        )

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Initialize RAG system for this session
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    conversation_tracker = {"user_message": None, "start_time": None}

    # Initialize RAG manager
    if ENABLE_RAG:
        await rag_manager.initialize()
        logger.info(f"RAG system initialized for session: {session_id}")

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=inference.STT(model="assemblyai/universal-streaming", language="en"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=inference.LLM(model="openai/gpt-4.1-mini"),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=inference.TTS(
            model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
        ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # RAG system: Track conversations
    if ENABLE_RAG:

        @session.on("user_speech_committed")
        async def _on_user_speech(ev):
            """Track when user speaks"""
            conversation_tracker["user_message"] = ev.text
            conversation_tracker["start_time"] = time.time()
            logger.debug(f"User said: {ev.text}")

        @session.on("agent_speech_committed")
        async def _on_agent_speech(ev):
            """Track when agent responds and log to RAG"""
            if (
                conversation_tracker["user_message"]
                and conversation_tracker["start_time"]
            ):
                user_msg = conversation_tracker["user_message"]
                agent_response = ev.text
                response_time = (time.time() - conversation_tracker["start_time"]) * 1000

                # Log conversation to RAG system
                try:
                    await rag_manager.log_conversation(
                        session_id=session_id,
                        user_message=user_msg,
                        agent_response=agent_response,
                        response_time_ms=response_time,
                        room_name=ctx.room.name,
                        success=True,
                        metadata={
                            "stt_model": "assemblyai/universal-streaming",
                            "llm_model": "openai/gpt-4.1-mini",
                            "tts_model": "cartesia/sonic-3",
                        },
                    )
                    logger.debug(f"Logged conversation to RAG (response_time: {response_time:.0f}ms)")
                except Exception as e:
                    logger.error(f"Failed to log conversation to RAG: {e}")

                # Reset tracker
                conversation_tracker["user_message"] = None
                conversation_tracker["start_time"] = None

        # Generate performance report on shutdown
        async def _generate_rag_report():
            try:
                report = await rag_manager.generate_performance_report(days=1)
                logger.info(f"Session performance: {report['summary']}")

                # Log high-priority suggestions
                for suggestion in report.get("suggestions", []):
                    if suggestion["severity"] == "high":
                        logger.warning(f"Improvement suggestion: {suggestion['suggestion']}")
            except Exception as e:
                logger.error(f"Failed to generate RAG report: {e}")

        ctx.add_shutdown_callback(_generate_rag_report)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
