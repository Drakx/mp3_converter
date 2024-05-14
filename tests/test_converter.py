import unittest
import shutil
from pathlib import Path
import subprocess
from unittest.mock import patch
from converter import convert_file, main

class TestMP3Converter(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for testing
        self.test_dir = Path("test_mp3_converter")
        self.flac_dir = self.test_dir / "flac"
        self.flac_dir.mkdir(parents=True, exist_ok=True)

        # Create a mock subprocess.run method to avoid executing ffmpeg
        self.mock_run = patch("subprocess.run").start()

    def tearDown(self):
        # Remove files and subdirectories within the temporary directory recursively
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("subprocess.run")
    def test_convert_file(self, mock_run):
        # Create a test FLAC file
        flac_file = self.flac_dir / "test.flac"
        flac_file.touch()

        # Call the function to convert the test FLAC file to MP3
        convert_file(flac_file, "mp3")

        # Check if subprocess.run was called with the correct arguments for MP3 conversion
        mock_run.assert_called_once_with(["ffmpeg", "-i", str(flac_file), str(flac_file.parent / "mp3" / "test.mp3")], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @patch("subprocess.run")
    def test_main(self, mock_run):
        # Create some test FLAC files
        flac_files = [self.flac_dir / f"test{i}.flac" for i in range(5)]
        for flac_file in flac_files:
            flac_file.touch()

        # Call the main function to convert FLAC files to MP3 and OGG
        main(self.flac_dir, "flac", ["mp3", "ogg"])

        # Check if subprocess.run was called with the correct arguments for MP3 conversion
        for flac_file in flac_files:
            mock_run.assert_any_call(["ffmpeg", "-i", str(flac_file), str(flac_file.parent / "mp3" / (flac_file.stem + ".mp3"))], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Check if subprocess.run was called with the correct arguments for OGG conversion
        for flac_file in flac_files:
            mock_run.assert_any_call(["ffmpeg", "-i", str(flac_file), str(flac_file.parent / "ogg" / (flac_file.stem + ".ogg"))], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    unittest.main()
