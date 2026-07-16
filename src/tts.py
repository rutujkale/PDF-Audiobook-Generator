import asyncio
import edge_tts
import os


class TextToSpeech:

    def __init__(self):

        self.voice = "en-US-GuyNeural"

    async def generate(self, text, output_file):

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice
        )

        await communicate.save(output_file)

    def create_audio(self, text, output_file):

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        asyncio.run(
            self.generate(text, output_file)
        )

        return output_file