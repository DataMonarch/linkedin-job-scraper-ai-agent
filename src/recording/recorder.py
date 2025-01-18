import subprocess
import platform


class ScreenRecorder:
    def __init__(self):
        self.process = None

    def start(self, output_file="recording.mp4"):
        """
        Starts recording the entire screen.
        On Windows, we can use FFmpeg with gdigrab.
        (Make sure ffmpeg is installed and on PATH.)
        """
        if platform.system() == "Windows":
            command = [
                "ffmpeg",
                "-y",
                "-f",
                "gdigrab",
                "-i",
                "desktop",
                "-vcodec",
                "libx264",
                "-r",
                "30",
                output_file,
            ]
        else:
            # Placeholder for other OS capturing
            command = ["echo", "Recording not implemented on this OS"]

        self.process = subprocess.Popen(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
