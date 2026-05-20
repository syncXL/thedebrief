from pathlib import Path
import io
import wave
import logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)

INTER_SEGMENT_SILENCE_MS = 600
TARGET_LUFS = -16.0
MP3_BITRATE = "192k"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _bytes_to_segment(wav_bytes: bytes, index: int) -> AudioSegment:
    """Gemini TTS returns raw 16-bit PCM at 24kHz mono — wrap in WAV container."""
    try:
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(wav_bytes)
        wav_buffer.seek(0)
        return AudioSegment.from_file(wav_buffer, format="wav")
    except Exception as e:
        raise ValueError(
            f"Segment {index} could not be decoded. "
            f"Received {len(wav_bytes)} bytes. "
            f"Original error: {e}"
        ) from e


def _normalise(segment: AudioSegment, target_lufs: float) -> AudioSegment:
    current_dbfs = segment.dBFS
    if current_dbfs == float("-inf"):
        return segment
    gain_db = target_lufs - current_dbfs
    return segment.apply_gain(gain_db)


def _silence(ms: int) -> AudioSegment:
    return AudioSegment.silent(duration=ms)


# ---------------------------------------------------------------------------
# AudioMerger
# ---------------------------------------------------------------------------

class AudioMerger:

    def __init__(
        self,
        silence_ms: int = INTER_SEGMENT_SILENCE_MS,
        target_lufs: float = TARGET_LUFS,
        bitrate: str = MP3_BITRATE,
    ):
        self._silence_ms = silence_ms
        self._target_lufs = target_lufs
        self._bitrate = bitrate

    def _merge_segments(
        self,
        segments: list[bytes],
        skip_invalid: bool = False,
    ) -> AudioSegment:
        if not segments:
            raise ValueError("segments list is empty — nothing to merge.")

        pause = _silence(self._silence_ms)
        merged = AudioSegment.empty()
        decoded_count = 0

        for i, wav_bytes in enumerate(segments):
            label = "anchor" if i == 0 else f"story_{i}"
            try:
                segment = _bytes_to_segment(wav_bytes, index=i)
            except ValueError as e:
                if skip_invalid:
                    logger.warning("Skipping segment %d (%s): %s", i, label, e)
                    continue
                raise

            segment = _normalise(segment, self._target_lufs)

            duration_sec = len(segment) / 1000
            logger.debug(
                "Segment %d (%s): %.1fs, %.1f dBFS",
                i, label, duration_sec, segment.dBFS,
            )

            if decoded_count > 0:
                merged += pause
            merged += segment
            decoded_count += 1

        if decoded_count == 0:
            raise RuntimeError("All segments were skipped or invalid — no audio to export.")

        if len(merged) == 0:
            raise RuntimeError("Merged AudioSegment is empty after processing.")

        return merged

    def to_bytes(self, segments: list[bytes], skip_invalid: bool = False) -> bytes:
        """Merge segments and return MP3 bytes without saving to disk."""
        merged = self._merge_segments(segments, skip_invalid)
        buffer = io.BytesIO()
        merged.export(buffer, format="mp3", bitrate=self._bitrate)
        buffer.seek(0)
        return buffer.getvalue()

    def to_file(self, segments: list[bytes], output_path: str, skip_invalid: bool = False) -> str:
        """Merge segments and save MP3 to disk. Returns absolute path."""
        merged = self._merge_segments(segments, skip_invalid)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        merged.export(str(output), format="mp3", bitrate=self._bitrate)
        total_sec = len(merged) / 1000
        logger.info(
            "Episode written: %s (%.1f min)",
            output.resolve(),
            total_sec / 60,
        )
        return str(output.resolve())

    def save_wav(self, pcm_bytes: bytes, output_path: str) -> str:
        """Save raw Gemini TTS PCM bytes as a WAV file. Useful for debugging."""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(pcm_bytes)
        return str(output.resolve())