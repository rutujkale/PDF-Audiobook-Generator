import asyncio
import edge_tts
import os

from pydub import AudioSegment


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

        files = []

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

            files.append(filename)

        final_audio = AudioSegment.empty()

        for file in files:

            final_audio += AudioSegment.from_mp3(file)

        final_path = os.path.join(
            output_folder,
            "audiobook.mp3"
        )

        final_audio.export(
            final_path,
            format="mp3"
        )

        for file in files:

            os.remove(file)

        return final_path