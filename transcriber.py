import os
from pydub import AudioSegment
from faster_whisper import WhisperModel

model = WhisperModel("large-v2", compute_type="int8")

def transcribe_voice(ogg_path: str, wav_path: str) -> str:
    # Convert .ogg -> .wav (16kHz mono)
    """
    Transcribes a given .ogg file into text using WhisperModel.

    :param ogg_path: Path to the .ogg file to transcribe.
    :param wav_path: Path to write the .wav file to (16kHz mono).
    :return: The transcribed text.
    """
    audio = AudioSegment.from_file(ogg_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(wav_path, format="wav")

    segments, _ = model.transcribe(wav_path, language="uk")
    result = "".join([segment.text for segment in segments])
    return result
