import asyncio
import edge_tts
import os
import subprocess


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


    def merge_audio(self, files, output_file):

        list_file = "audio/files.txt"

        with open(list_file, "w", encoding="utf-8") as f:

            for file in files:

                f.write(f"file '{os.path.abspath(file)}'\n")

        command = [

            "ffmpeg",

            "-y",

            "-f",

            "concat",

            "-safe",

            "0",

            "-i",

            list_file,

            "-c",

            "copy",

            output_file

        ]

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        os.remove(list_file)

        for file in files:

            os.remove(file)


    def create_audio(self, text):

        os.makedirs("audio", exist_ok=True)

        chunks = self.split_text(text)

        audio_files = []

        for i, chunk in enumerate(chunks):

            filename = f"audio/part_{i+1}.mp3"

            asyncio.run(
                self.generate_chunk(
                    chunk,
                    filename
                )
            )

            audio_files.append(filename)

        final_output = "audio/audiobook.mp3"

        self.merge_audio(
            audio_files,
            final_output
        )

        return final_output