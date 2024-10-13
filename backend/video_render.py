from moviepy.editor import *
import pysrt
import os
from PIL import Image

class VideoCreator:
    def __init__(self, input_folder, output_folder, target_size, audio_path, srt_path, image_srt_path, output_path):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.target_size = target_size
        self.audio_path = audio_path
        self.srt_path = srt_path
        self.image_srt_path = image_srt_path
        self.output_path = output_path
        self.audio = AudioFileClip(audio_path)

    def resize_and_crop_image(self, input_path, output_path):
        with Image.open(input_path) as img:
            img_ratio = img.width / img.height
            target_ratio = self.target_size[0] / self.target_size[1]

            if target_ratio > img_ratio:
                scale_factor = self.target_size[0] / img.width
                new_size = (self.target_size[0], int(img.height * scale_factor))
            else:
                scale_factor = self.target_size[1] / img.height
                new_size = (int(img.width * scale_factor), self.target_size[1])

            img = img.resize(new_size, Image.LANCZOS)

            left = (img.width - self.target_size[0]) / 2
            top = (img.height - self.target_size[1]) / 2
            right = (img.width + self.target_size[0]) / 2
            bottom = (img.height + self.target_size[1]) / 2

            img = img.crop((left, top, right, bottom))
            img.save(output_path)

    def resize_images_in_folder(self):
        os.makedirs(self.output_folder, exist_ok=True)

        # remove files in output folder
        for filename in os.listdir(self.output_folder):
            file_path = os.path.join(self.output_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file: {file_path}")

        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                input_path = os.path.join(self.input_folder, filename)
                output_path = os.path.join(self.output_folder, filename)
                self.resize_and_crop_image(input_path, output_path)
                print(f"Processed image saved: {output_path}")

    def srt_to_moviepy_subtitles(self):
        subs = pysrt.open(self.srt_path)
        subtitle_clips = []
        max_width = self.target_size[0] * 0.8

        for sub in subs:
            start_time = sub.start.to_time()
            end_time = sub.end.to_time()
            start_seconds = (
                start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond / 1e6
            )
            end_seconds = (
                end_time.hour * 3600 + end_time.minute * 60 + end_time.second + end_time.microsecond / 1e6
            )
            duration = end_seconds - start_seconds
            formatted_text = sub.text.replace("\n", " ")

            text_clip = TextClip(
                formatted_text,
                fontsize=int(self.target_size[1] * 0.05),
                color='white',
                stroke_color='orange',
                bg_color='black',
                stroke_width=2,
                size=(max_width, None),
                method='caption',
                align='center',
            )

            text_clip = text_clip.set_position(("center", "center"))
            text_clip = text_clip.set_start(start_seconds)
            text_clip = text_clip.set_duration(duration)
            text_clip = text_clip.fx(vfx.fadein, 0.25).fx(vfx.fadeout, 0.25)

            subtitle_clips.append(text_clip)

        return CompositeVideoClip(subtitle_clips, size=(self.target_size[0], self.target_size[1]))

    def parse_image_timings(self):
        subs = pysrt.open(self.image_srt_path)
        image_timings = []

        for sub in subs:
            image_index = sub.index
            start_time = sub.start.ordinal / 1000.0
            end_time = sub.end.ordinal / 1000.0
            duration = end_time - start_time
            image_timings.append({
                'image_index': image_index,
                'start_time': start_time,
                'end_time': end_time,
                'duration': duration
            })

        return image_timings

    def create_video_with_images_and_subtitles(self):
        audio_clip = self.audio
        image_timings = self.parse_image_timings()
        image_clips = []

        for timing in image_timings:
            image_path = os.path.join(self.output_folder, f"{timing['image_index']}.png")
            if not os.path.isfile(image_path):
                continue

            image_clip = ImageClip(image_path)
            target_aspect_ratio = 9 / 16
            original_width, original_height = image_clip.size
            original_aspect_ratio = original_width / original_height

            if original_aspect_ratio > target_aspect_ratio:
                new_width = int(original_height * target_aspect_ratio)
                new_height = original_height
            else:
                new_width = original_width
                new_height = int(original_width / target_aspect_ratio)

            x_center = original_width / 2
            y_center = original_height / 2
            image_clip = image_clip.crop(width=new_width, height=new_height, x_center=x_center, y_center=y_center)
            image_clip = image_clip.set_duration(timing['duration'])
            image_clip = image_clip.set_start(timing['start_time'])
            image_clip = image_clip.crossfadein(0.1).crossfadeout(0.1)

            image_clips.append(image_clip)

        if image_clips:
            first_clip = image_clips[0]
            video_size = (first_clip.w, first_clip.h)

            video_clip = CompositeVideoClip(image_clips, size=video_size)
            video_clip = video_clip.set_audio(audio_clip)
            

            subtitles = self.srt_to_moviepy_subtitles()
            final_video = CompositeVideoClip([video_clip, subtitles])
            final_video = final_video.set_duration(audio_clip.duration)

            # final_video.write_videofile(self.output_path, fps=24, codec='mpeg4')
            final_video.write_videofile(self.output_path, fps=24, codec='libx264')

    def render_video(self):
        self.resize_images_in_folder()
        self.create_video_with_images_and_subtitles()

if __name__ == "__main__":
    input_folder = 'results/images'
    output_folder = 'results/resized_images'
    target_size = (1080, 1920)
    audio_path = "output.mp3"
    srt_path = "output_subtitles.srt"
    image_srt_path = "output_images.srt"
    output_path = "output_video.mp4"

    video_creator = VideoCreator(input_folder, output_folder, target_size, audio_path, srt_path, image_srt_path, output_path)
    video_creator.render_video()