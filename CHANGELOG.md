# Changelog

This changelog is based on the repository's actual commit history.

## 2026-04-09

### GUI Frontend
- Added a Tkinter-based GUI frontend for the PDF compressor.
- Added file selection and a `Compress` action in the GUI.
- Added GUI progress updates while preserving terminal progress output during compression.
- Added a completion summary in the GUI showing the output file location, original size, compressed size, and reduction percentage.
- Added automatic GUI close behavior after the completion summary remains visible for about 10 seconds.

### Launch Behavior
- Changed the default startup behavior so running the script with no arguments opens the GUI automatically.
- Kept command-line usage available when an input PDF path is provided.
- Kept the optional `--gui` flag for explicitly launching the GUI.

### Project Setup
- Added `requirements.txt` for project dependencies.
- Added `.gitignore` entries for local environment and Python cache artifacts.

## 2026-03-30

### Initial CLI Release
- Added the first working version of the PDF compression script.
- Implemented PDF compression by rendering pages to images and rebuilding a compressed PDF.

### CLI Progress and Output Improvements
- Improved terminal status output during compression.
- Added a visible progress bar for multi-page compression jobs.
- Fixed output file path handling for the generated compressed PDF.
