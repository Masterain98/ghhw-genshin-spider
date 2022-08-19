# ghhw-genshin-spider

Web crawler based on selenium for [https://genshin.honeyhunterworld.com](https://genshin.honeyhunterworld.com) after its 2022 redesigning.

## Features

- Capture all characters' data to meet [Snap.Genshin](https://github.com/DGP-Studio/Snap.Genshin)'s metadata requirements
  - Replace Webp links to PNG version
  - Delete picture quality parameter
  - Fill unfinished translation work
  - Fill city data for talent materials, characters, and weekly item materials

## Usage

- Run `python main.py`
  - Required library: `selenium`