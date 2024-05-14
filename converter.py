import argparse
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm
import signal
import sys

def sigint_handler(sig, frame):
    # Handle KeyboardInterrupt (Ctrl+C)
    print("\nConversion interrupted by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def convert_file(input_file, output_format):
    """
    Convert a file to the specified output format.

    Parameters:
        input_file (Path): Path to the input file.
        output_format (str): Output format to convert to.
    """
    # Define directories for output files
    output_dir = input_file.parent / output_format
    output_dir.mkdir(exist_ok=True)

    # Check if the input file has the same extension as the output format
    if input_file.suffix.lower() == "." + output_format.lower():
        print(f"Skipping conversion of {input_file.name} as it is already in {output_format} format.")
        return None

    # Define path for the output file
    output_file = output_dir / input_file.with_suffix("." + output_format).name

    try:
        # Convert the file to the specified output format
        subprocess.run(["ffmpeg", "-i", str(input_file), str(output_file)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return None  # Return None for successful conversion
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")
        return input_file  # Return input_file for failed conversion


def main(root_dir, input_format, output_formats):
    """
    Main function to convert files in the specified directory from input_format to output_formats.

    Parameters:
        root_dir (str): Root directory containing files to convert.
        input_format (str): Input format to convert from.
        output_formats (list): List of output formats to convert to.
    """
    # Check if the root directory exists
    root_path = Path(root_dir)
    if not root_path.is_dir():
        print("Invalid directory.")
        return

    # Find all files with the input format recursively
    input_files = [file for file in root_path.rglob("*." + input_format)]

    # List to store paths of failed conversions
    failed_files = []

    # Convert files to the specified output formats in parallel
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(convert_file, file, output_format) for file in input_files for output_format in output_formats]

        # Use tqdm for progress bar
        with tqdm(total=len(futures), desc=f"Converting files to {', '.join(output_formats)}") as pbar:
            for future in as_completed(futures):
                if future.exception() is not None:
                    failed_files.append(future.exception())
                pbar.update(1)

    # Print list of failed conversions, if any
    if failed_files:
        print("\nFailed to convert the following files:")
        for failed_file in failed_files:
            print(f"- {failed_file}")


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
    output_formats = args.output_formats if args.output_formats else ["mp3", "ogg"]

    # Call main function with provided arguments
    main(args.root_dir, input_format, output_formats)
