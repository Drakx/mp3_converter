import unittest
import shutil
from pathlib import Path
import subprocess
from unittest.mock import patch
from converter import convert_to_ogg_flac

class TestMP3Converter(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.test_dir = Path("test_mp3_converter")
        self.mp3_dir = self.test_dir / "mp3"
        self.mp3_dir.mkdir(parents=True, exist_ok=True)
        self.flac_dir = self.mp3_dir / "flac"
        self.ogg_dir = self.mp3_dir / "ogg"
        self.mp3_output_dir = self.mp3_dir / "mp3"
        self.flac_dir.mkdir(exist_ok=True)
        self.ogg_dir.mkdir(exist_ok=True)
        self.mp3_output_dir.mkdir(exist_ok=True)

        # Create a mock subprocess.run method to avoid executing ffmpeg
        self.mock_run = patch("subprocess.run").start()

    def tearDown(self):
        # Remove files and subdirectories within the temporary directory recursively
        for item in self.test_dir.glob('**/*'):
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item, ignore_errors=True)

        # Remove mp3, ogg, and flac directories within the temporary directory
        mp3_dir = self.test_dir / 'mp3'
        for subdir in ['ogg', 'mp3', 'flac']:
            if (mp3_dir / subdir).exists():
                (mp3_dir / subdir).rmdir()

        # Remove the temporary directory itself
        self.test_dir.rmdir()

    def test_convert_to_ogg_flac(self):
        # Create a test MP3 file
        mp3_file = self.mp3_dir / "test.mp3"
        mp3_file.touch()

        # Call the function to convert the test MP3 file
        convert_to_ogg_flac(mp3_file)

        # Check if subprocess.run was called with the correct arguments for OGG conversion
        self.mock_run.assert_any_call(["ffmpeg", "-i", str(mp3_file), "-c:a", "libvorbis", "-q:a", "5", str(self.ogg_dir / "test.ogg")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Check if subprocess.run was called with the correct arguments for FLAC conversion
        self.mock_run.assert_any_call(["ffmpeg", "-i", str(mp3_file), "-c:a", "flac", str(self.flac_dir / "test.flac")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Check if the original MP3 file was moved to the mp3_output_dir
        self.assertTrue((self.mp3_output_dir / "test.mp3").exists())

if __name__ == "__main__":
    unittest.main()
