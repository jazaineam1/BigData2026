"""Regression: S11 no recorta audio después de 60 s y guarda PCM16 íntegro."""
from pathlib import Path
from tempfile import TemporaryDirectory
import math
import wave
import unittest

import numpy as np
import soundfile as sf
from utils import s11_etl_core as core


def make_wav(path, hz, seconds, channels=1):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Crear en fragmentos para NO cargar todos los minutos en RAM.
    t = np.arange(hz, dtype=np.float64)/hz
    tone = np.rint(np.sin(2*np.pi*220*t)*11000).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(hz)
        part = tone.tobytes() if channels == 1 else np.repeat(tone[:,None],channels,axis=1).astype("<i2").tobytes()
        for _ in range(seconds):
            w.writeframesraw(part)


class AudioLargoTest(unittest.TestCase):
    def _test_audio(self, hz, duration, channels=1):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            raw=root/"raw"/"audios"/"prueba.wav"
            make_wav(raw,hz,duration,channels)
            signature=core.sha256(raw)
            entry={"original_path":raw.relative_to(root).as_posix(),
                   "original_sha256":signature,"article_id":None,
                   "source_record_id":None,"source_id":"test_audio_largo",
                   "source_kind":"synthetic_regression"}
            progress=[]
            result=core.transformar_audios(
                root,[entry],ganancia=1.0,block_seconds=8,
                on_block=lambda e:progress.append(e),verbose=False)[0]
            out=root/result["derived_path"]
            with sf.SoundFile(out) as wav:
                self.assertEqual(wav.samplerate,16000)
                self.assertEqual(wav.channels,1)
                self.assertEqual(wav.subtype,"PCM_16")
                self.assertEqual(wav.frames,duration*16000)
            self.assertEqual(result["metrics"]["processing_blocks"],len(progress))
            self.assertGreater(len(progress),1)
            self.assertEqual(progress[-1]["processed_input_frames"],duration*hz)
            self.assertEqual(progress[-1]["progress"],1.0)
            self.assertEqual(result["metrics"]["processed_input_frames"],duration*hz)
            self.assertEqual(core.sha256(raw),signature)
            self.assertEqual(core.sha256(out),result["derived_sha256"])
            again=core.transformar_audios(root,[entry],ganancia=1.0,block_seconds=8,verbose=False)[0]
            self.assertEqual(again["derived_sha256"],result["derived_sha256"])

    def test_mono_65s_16khz(self):
        self._test_audio(16000,65)

    def test_estereo_62s_44100hz_resampled(self):
        self._test_audio(44100,62,2)

    def test_invalid_block_size(self):
        with self.assertRaisesRegex(ValueError,"block_seconds"):
            core.transformar_audios(Path("/tmp"),[],block_seconds=0)


if __name__=="__main__":
    unittest.main()
