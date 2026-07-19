import os
import subprocess


class AudioMerger:

    @staticmethod
    def merge(audio_files, output_file):

        if not audio_files:
            raise ValueError("No audio files to merge.")

        temp_list = os.path.join(
            os.path.dirname(output_file),
            "concat_list.txt"
        )

        with open(temp_list, "w", encoding="utf-8") as file:

            for audio in audio_files:

                absolute = os.path.abspath(audio).replace("\\", "/")

                file.write(f"file '{absolute}'\n")

        command = [

            "ffmpeg",

            "-y",

            "-f",

            "concat",

            "-safe",

            "0",

            "-i",

            temp_list,

            "-c",

            "copy",

            output_file

        ]

        result = subprocess.run(

            command,

            capture_output=True,

            text=True

        )

        os.remove(temp_list)

        if result.returncode != 0:

            raise RuntimeError(result.stderr)

        return output_file