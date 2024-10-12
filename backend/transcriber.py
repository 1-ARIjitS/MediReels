import edge_tts
import asyncio
import os

class Transcriber:
    def __init__(self, text, output_filename, output_vtt_subtitles, output_vtt_images, srt_filename_subtitles, srt_filename_images):
        self.text = text
        self.output_filename = output_filename
        self.output_vtt_subtitles = output_vtt_subtitles
        self.output_vtt_images = output_vtt_images
        self.srt_filename_subtitles = srt_filename_subtitles
        self.srt_filename_images = srt_filename_images

    async def generate_audio_and_convert(self):
        communicate = edge_tts.Communicate(self.text, "en-AU-WilliamNeural")
        submaker = edge_tts.SubMaker()
        
        with open(self.output_filename, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

        with open(self.output_vtt_subtitles, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs(2))
        with open(self.output_vtt_images, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs(15))

        # Convert VTT to SRT for subtitles
        self.convert_vtt_to_srt(self.output_vtt_subtitles, self.srt_filename_subtitles)
        # Convert VTT to SRT for images
        self.convert_vtt_to_srt(self.output_vtt_images, self.srt_filename_images)

        if os.path.exists(self.output_vtt_subtitles):
            os.remove(self.output_vtt_subtitles)

        if os.path.exists(self.output_vtt_images):
            os.remove(self.output_vtt_images)

    def convert_vtt_to_srt(self, vtt_filename, srt_filename):
        with open(vtt_filename, 'r', encoding='utf-8') as vtt_file:
            lines = vtt_file.readlines()

        srt_lines = []
        index = 1
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("WEBVTT"):
                i += 1
                continue

            if "-->" in line:
                start_time, end_time = line.split(" --> ")
                start_time = start_time.replace('.', ',')
                end_time = end_time.replace('.', ',')
                i += 1
                subtitle_text = []
                while i < len(lines) and lines[i].strip():
                    subtitle_text.append(lines[i].strip())
                    i += 1
                srt_lines.append(f"{index}")
                srt_lines.append(f"{start_time} --> {end_time}")
                srt_lines.extend(subtitle_text)
                srt_lines.append('')
                index += 1
            else:
                i += 1

        with open(srt_filename, 'w', encoding='utf-8') as srt_file:
            srt_file.write('\n'.join(srt_lines))

if __name__ == "__main__":
    text = open("article.txt").read()
    transcriber = Transcriber(text, "output.mp3", "output_subtitles.vtt", "output_images.vtt", "output_subtitles.srt", "output_images.srt")
    asyncio.run(transcriber.generate_audio_and_convert())