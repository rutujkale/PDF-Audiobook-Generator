import asyncio
import edge_tts
import os


class TextToSpeech:

    def __init__(self):

        self.chunk_size = 3500

    def split_text(self, text):

        chunks = []

        text = text.replace("\n", " ")

        while len(text) > self.chunk_size:

            split = text.rfind(" ", 0, self.chunk_size)

            if split == -1:

                split = self.chunk_size

            chunks.append(text[:split])

            text = text[split:].strip()

        if text:

            chunks.append(text)

        return chunks

    async def _generate_chunk(self, text, voice, rate, filename):

        communicate = edge_tts.Communicate(

            text=text,

            voice=voice,

            rate=rate

        )

        await communicate.save(filename)

    def create_audio(

        self,

        text,

        voice,

        speed,

        output_folder

    ):

        os.makedirs(output_folder, exist_ok=True)

        chunks = self.split_text(text)

        files = []

        # Convert speed slider into Edge-TTS format

        percent = int((speed - 1.0) * 100)

        rate = f"{percent:+d}%"

        for index, chunk in enumerate(chunks):

            filename = os.path.join(

                output_folder,

                f"part_{index+1}.mp3"

            )

            asyncio.run(

                self._generate_chunk(

                    chunk,

                    voice,

                    rate,

                    filename

                )

            )

            files.append(filename)

        return files