import argparse
import subprocess
import signal
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm
import logging

def sigint_handler(sig, frame):
    # Handle KeyboardInterrupt (Ctrl+C)
    print("\nConversion interrupted by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_file(input_file, output_format, pbar):
    """
    Convert a file to the specified output format.

    Parameters:
        input_file (Path): Path to the input file.
        output_format (str): Output format to convert to.
        pbar (tqdm): Progress bar instance to update.
    """
    # Define directories for output files
    output_dir = input_file.parent / output_format
    output_dir.mkdir(exist_ok=True)

    # Check if the input file has the same extension as the output format
    if input_file.suffix.lower() == "." + output_format.lower():
        pbar.update(1)
        return None

    # Define path for the output file
    output_file = output_dir / input_file.with_suffix("." + output_format).name

    try:
        # Convert the file to the specified output format
        subprocess.run(["ffmpeg", "-i", str(input_file), str(output_file)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pbar.update(1)
        return input_file, output_file  # Return both input and output files for further processing
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting {input_file}: {e}")
        pbar.update(1)
        return None

def move_file(input_file, input_format):
    """
    Move the input file to the directory corresponding to the input format.

    Parameters:
        input_file (Path): Path to the input file.
        input_format (str): Input format to convert from.
    """
    # Define the destination directory based on the input format
    dest_dir = input_file.parent / input_format
    dest_dir.mkdir(exist_ok=True)

    # Define the destination file path
    dest_file = dest_dir / input_file.name

    # If the destination file already exists, skip the move operation
    if dest_file.exists():
        return

    # Move the file to the destination directory
    shutil.move(str(input_file), str(dest_file))

def main(root_dir, input_format, output_formats):
    """
    Main function to convert files in the specified directory from input_format to output_formats.

    Parameters:
        root_dir (str): Root directory containing files to convert.
        input_format (str): Input format to convert from.
        output_formats (list): List of output formats to convert to.
    """
    setup_logging()

    # Check if the root directory exists
    root_path = Path(root_dir)
    if not root_path.is_dir():
        logging.error("Invalid directory.")
        return

    # Find all files with the input format recursively
    input_files = [file for file in root_path.rglob("*." + input_format)]
    if not input_files:
        logging.info(f"No files with {input_format} format found.")
        return

    # List to store paths of failed conversions
    failed_files = []

    # Convert files to the specified output formats in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        with tqdm(total=len(input_files) * len(output_formats), desc=f"Converting files to {', '.join(output_formats)}") as pbar:
            for file in input_files:
                for output_format in output_formats:
                    futures.append(executor.submit(convert_file, file, output_format, pbar))

            for future in as_completed(futures):
                result = future.result()
                if result is None:
                    continue  # Skip failed or unnecessary conversions
                if isinstance(result, tuple):
                    input_file, _ = result  # Get the input file path
                    move_file(input_file, input_format)  # Move the file to its respective folder
                else:
                    failed_files.append(result)  # Collect failed conversions

    # Print list of failed conversions, if any
    if failed_files:
        logging.error("\nFailed to convert the following files:")
        for failed_file in failed_files:
            logging.error(f"- {failed_file}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert files from one format to another.")
    parser.add_argument("-r", "--root-dir", help="Root directory containing files to convert", required=True)
    parser.add_argument("-i", "--input-format", help="Input format to convert from")
    parser.add_argument("-o", "--output-formats", nargs="+", help="Output formats to convert to")
    args = parser.parse_args()

    # If no input format is specified, default to "mp3"
    input_format = args.input_format if args.input_format else "mp3"

    # If no output formats are specified, default to converting to both MP3 and OGG
    output_formats = args.output_formats if args.output_formats else ["mp3", "ogg", "flac"]

    # Call main function with provided arguments
    main(args.root_dir, input_format, output_formats)
