from core.utils.audio import audio_duration_seconds
from tests.utils import fixture_bytes


class TestAudioDurationSeconds:
    async def test_audio_duration_seconds_wav(self):
        bs = fixture_bytes("files/test.wav")
        dur = await audio_duration_seconds(bs, "audio/wav")
        assert dur == 3

    async def test_audio_duration_seconds_mp3(self):
        # This test requires ffmpeg to be installed
        bs = fixture_bytes("files/sample.mp3")
        dur = await audio_duration_seconds(bs, "audio/mpeg")
        assert dur == 10.043

    async def test_audio_duration_seconds_flac(self):
        bs = fixture_bytes("files/sample.flac")
        dur = await audio_duration_seconds(bs, "audio/flac")
        assert dur == 8.916
