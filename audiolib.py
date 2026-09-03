from pathlib import Path
from pydub import AudioSegment
from math import ceil
import static_ffmpeg
static_ffmpeg.add_paths(weak=True)
def get_audio_len_secs(audio_path: Path) -> float:
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio) / 1000.0
    return duration

def extend_audio(replacing_path: Path, override_path, export_folder: Path) -> Path:
    audio_path = override_path
    replacing_audio = AudioSegment.from_file(replacing_path)
    final_path = export_folder / (str(audio_path.stem) + "_len" + str(int(len(replacing_audio)/1000.0)) + str(audio_path.suffix))
    if final_path.is_file():
        return final_path
    override_audio = AudioSegment.from_file(override_path)
    loop_count = ceil(len(replacing_audio) / len(override_audio))
    audio = AudioSegment.from_file(audio_path)
    looped_audio: AudioSegment = audio * loop_count
    final_audio: AudioSegment = looped_audio[:len(replacing_audio)] # pyright: ignore[reportAssignmentType]
    export_folder.mkdir(parents=True, exist_ok=True)
    final_audio.export(final_path,format=(audio_path.suffix.lstrip(".").lower()))
    return final_path