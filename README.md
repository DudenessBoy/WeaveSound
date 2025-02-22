# WeaveSound

WeaveSound is a lightweight, offline music player that allows users to listen to their downloaded tracks. It offers a queue feature to play songs in order, shuffle the queue, remove or reorder items, and save/load the queue to/from a file. For best functionality, FFmpeg is required, but it is not needed for the basic operation of the app. This is mostly a hobby project, and isn't meant to be extremely good compared to, say, VLC, but feel free to try out and tweak this project.

## Features
- Play downloaded tracks offline
- Add songs to a queue and play them in order
- Shuffle, reorder, duplicate, and remove items in the queue
- Save and load queues from files

## Requirements
1. **FFmpeg** (required for best functionality, especially for audio encoding/decoding)
    - For Linux:
      - For **Debian-based distributions** (e.g., Ubuntu):
        ```bash
        sudo apt install ffmpeg
      - For **Red Hat-based distributions** (e.g., Fedora, CentOS):
          ```bash
          sudo dnf install ffmpeg
      - For **Arch Linux**:
          ```bash
          sudo pacman -S ffmpeg
      - For other Linux distributions, you can search for FFmpeg in your package manager. Alternatively, you can check your distribution’s documentation for installation instructions specific to FFmpeg.
      - Installing from **snap**:
          ```bash
          sudo snap install ffmpeg
    - For Windows
      - Installing from **Winget**:
          ```bash
          winget install ffmpeg
      - Installing from **Chocolaty**:
          ```bash
          choco install ffmpeg
      - Manual installation:  
          https://www.gyan.dev/ffmpeg/builds/
    - Other download options:  
          https://ffmpeg.org/download.html

## Installing Dependencies (for running from source):
If you plan to run WeaveSound from the source code, you will need to install the following dependencies:

1. **PyGame**:
   ```bash
   pip install pygame
2. **Python** 3.8 or above
   - For Linux (note: most Linux distributions come with Python preinstalled):
     - For **Debian-based distributions** (e.g., Ubuntu):
       ```bash
       sudo apt install python3
      - For **Red Hat-based distributions** (e.g., Fedora, CentOS):
         ```bash
         sudo dnf install python3
     - For **Arch Linux**:
         ```bash
         sudo pacman -S python
     - For other Linux distributions, you can search for Python in your package manager. Alternatively, you can check your distribution’s documentation for installation instructions specific to Python.
   - For Windows
     - Installing from **Winget**:
         ```bash
         winget install Python.Python3.12
     - Windows installer:  
         https://www.python.org/downloads/windows/
   - Other download options:  
         https://python.org/downloads

## Platform Compatibility
WeaveSound has been tested on Linux and Windows. It has not been tested on macOS, so compatibility on macOS is not guaranteed.

## Usage
Run the executable for a hassle-free experience.
If running from source, use the following command:
```bash
python WeaveSound.pyw
```
## License
WeaveSound is released under the GPL License. See the [LICENSE.txt](https://github.com/DudenessBoy/WeaveSound/blob/main/LICENSE.txt) file for more details.
