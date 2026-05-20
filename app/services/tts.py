import abc
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class TTSProvider(abc.ABC):

    @abc.abstractmethod
    async def generate(self, prompt: str) -> bytes:
        raise NotImplementedError

    @abc.abstractmethod
    def build_speech_config(self) -> any:
        raise NotImplementedError


class GeminiTTS(TTSProvider):

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-preview-tts"):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def build_speech_config(self) -> types.SpeechConfig:
        return types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Anchor",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Charon"
                            )
                        )
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Expert",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Aoede"
                            )
                        )
                    ),
                ]
            )
        )

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(multiplier=1, min=2, max=16),
        stop=stop_after_attempt(3),
    )
    async def generate(self, prompt: str) -> bytes:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=self.build_speech_config(),
            )
        )
        return response.candidates[0].content.parts[0].inline_data.data