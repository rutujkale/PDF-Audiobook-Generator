import asyncio
import edge_tts
import os


class TextToSpeech:

    def __init__(self):

        self.voice = "en-US-GuyNeural"

        self.chunk_size = 3500

    def split_text(self, text):

        chunks = []

        while len(text) > self.chunk_size:

            split_index = text.rfind(" ", 0, self.chunk_size)

            if split_index == -1:

                split_index = self.chunk_size

            chunks.append(text[:split_index])

            text = text[split_index:]

        chunks.append(text)

        return chunks

    async def generate_chunk(self, text, filename):

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice
        )

        await communicate.save(filename)

    def create_audio(self, text, output_folder="audio"):

        os.makedirs(output_folder, exist_ok=True)

        chunks = self.split_text(text)

        audio_files = []

        for i, chunk in enumerate(chunks):

            filename = os.path.join(
                output_folder,
                f"part_{i+1}.mp3"
            )

            asyncio.run(
                self.generate_chunk(
                    chunk,
                    filename
                )
            )

            audio_files.append(filename)

        return audio_files