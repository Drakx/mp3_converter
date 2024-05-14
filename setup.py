from setuptools import setup, find_packages

setup(
    name='mp3_converter',
    version='1.0',
    packages=find_packages(),
    scripts=['converter.py'],
    install_requires=['ffmpeg-python', 'tqdm'],
    entry_points={
        'console_scripts': [
            'mp3_converter=converter:main',
        ],
    },
    author='Kai Windle',
    author_email='kaiwindle@gmail.com',
    description='Convert MP3 files to OGG and FLAC formats.',
    url='https://github.com/Drakx/mp3_converter',
)
