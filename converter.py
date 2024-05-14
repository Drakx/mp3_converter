import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tqdm import tqdm

def convert_to_ogg_flac(mp3_file):
    # Define directories for output files
    mp3_dir = mp3_file.parent
    flac_dir = mp3_dir / "flac"
    ogg_dir = mp3_dir / "ogg"
    mp3_output_dir = mp3_dir / "mp3"

    # Create output directories if they don't exist
    flac_dir.mkdir(exist_ok=True)
    ogg_dir.mkdir(exist_ok=True)
    mp3_output_dir.mkdir(exist_ok=True)

    # Define paths for output files
    ogg_file = ogg_dir / mp3_file.with_suffix(".ogg").name
    flac_file = flac_dir / mp3_file.with_suffix(".flac").name
    mp3_dest_file = mp3_output_dir / mp3_file.name

    try:
        # Convert MP3 to OGG format
        subprocess.run(["ffmpeg", "-i", str(mp3_file), "-c:a", "libvorbis", "-q:a", "5", str(ogg_file)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Convert MP3 to FLAC format
        subprocess.run(["ffmpeg", "-i", str(mp3_file), "-c:a", "flac", str(flac_file)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Move original MP3 file to mp3_output_dir
        mp3_file.rename(mp3_dest_file)

        return None  # Return None for successful conversion
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error converting {mp3_file}: {e}")
        return mp3_file  # Return mp3_file for failed conversion

def main(root_dir):
    # Check if the root directory exists
    mp3_root_path = Path(root_dir)
    if not mp3_root_path.is_dir():
        print("Invalid directory.")
        return

    # Find all MP3 files recursively
    mp3_files = [file for file in mp3_root_path.rglob("*.mp3")]

    # List to store paths of failed conversions
    failed_files = []

    # Convert MP3 files to OGG and FLAC formats in parallel
    with ThreadPoolExecutor() as executor:
        # Use tqdm for progress bar
        results = list(tqdm(executor.map(convert_to_ogg_flac, mp3_files), total=len(mp3_files), desc="Converting MP3 files"))

    # Check for failed conversions
    for result in results:
        if result is not None:
            failed_files.append(result)

    # Print list of failed conversions, if any
    if failed_files:
        print("\nFailed to convert the following files:")
        for failed_file in failed_files:
            print(f"- {failed_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert MP3 files to OGG and FLAC formats.")
    parser.add_argument("-r", "--root-dir", help="Root directory containing MP3 files", required=True)
    args = parser.parse_args()

    # Call main function with root directory argument
    main(args.root_dir)
