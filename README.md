# PDF Compressor

A simple Python tool for compressing PDF files by rendering each page to an image and rebuilding the document as a new PDF.

This project is useful for scanned PDFs, image-heavy documents, and files that feel slow or bulky on devices with limited storage or slower PDF rendering.

## What It Does

- Compresses PDFs by converting each page into a JPEG-backed page in a new PDF
- Supports both command-line and GUI usage
- Shows compression progress in the terminal
- Shows compression progress in the GUI when running in GUI mode
- Displays the output file path and compression summary when GUI compression finishes

## How It Works

The compressor opens the input PDF, renders each page at a fixed DPI, converts each rendered page to JPEG in memory, and inserts those images into a newly generated PDF.

This approach can reduce file size for scanned or image-based PDFs, but it may also remove selectable/searchable text because pages are rebuilt as images.

## Requirements

- Python virtual environment at `.venv`
- Dependencies listed in [requirements.txt](C:\Visual%20Studio%20Code%20Work\New\leargit\Real%20Life%20Projects\pdf-compressor\requirements.txt)

Install dependencies into the project virtual environment with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Usage

### GUI Mode

Run the script with no arguments to open the GUI:

```powershell
.\.venv\Scripts\python.exe .\pdf-compressor.py
```

You can also launch the GUI explicitly with:

```powershell
.\.venv\Scripts\python.exe .\pdf-compressor.py --gui
```

In GUI mode:
- Click `Browse...` to select a PDF
- Click `Compress` to start compression
- Watch progress in the GUI
- If a terminal is present, progress also continues to print there
- When compression finishes, the GUI shows:
  - output file location
  - original file size
  - compressed file size
  - reduction percentage
- The completion summary stays visible for about 10 seconds, then the window closes automatically

### CLI Mode

Run the script with an input PDF path to use the command-line workflow:

```powershell
.\.venv\Scripts\python.exe .\pdf-compressor.py .\input.pdf
```

To choose a custom output path:

```powershell
.\.venv\Scripts\python.exe .\pdf-compressor.py .\input.pdf --output .\out.pdf
```

In CLI mode:
- The script prints the output location before compression starts
- Compression progress is shown in the terminal
- When compression finishes, the script prints the output path, original size, compressed size, and reduction percentage

## Output File Naming

If you do not pass `--output`, the script saves the compressed PDF next to the input file using this naming pattern:

```text
original_name_compressed.pdf
```

For example:

```text
report.pdf -> report_compressed.pdf
```

## Important Notes

- This tool is best suited to scanned PDFs and image-heavy files
- Text may no longer be selectable or searchable after compression
- The script currently uses:
  - `dpi=120`
  - `jpeg_quality=50`
- If the output file already exists, the script warns you before continuing
- Input files must have a `.pdf` extension

## Project Files

- [pdf-compressor.py](C:\Visual%20Studio%20Code%20Work\New\leargit\Real%20Life%20Projects\pdf-compressor\pdf-compressor.py): main script with both CLI and GUI entry paths
- [requirements.txt](C:\Visual%20Studio%20Code%20Work\New\leargit\Real%20Life%20Projects\pdf-compressor\requirements.txt): Python dependencies
- [CHANGELOG.md](C:\Visual%20Studio%20Code%20Work\New\leargit\Real%20Life%20Projects\pdf-compressor\CHANGELOG.md): project change history
