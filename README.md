# PDF Optimizer

A simple Python tool that rebuilds a PDF page-by-page as image-backed pages in a new output PDF.

This project is most useful for scanned PDFs and image-heavy documents where reducing size or simplifying rendering matters more than preserving vector text and original PDF structure.

## What It Does

- Rebuilds each PDF page as a rendered image inside a new PDF
- Supports both command-line and GUI usage
- Shows progress in the terminal during compression
- Shows progress in the GUI when running in GUI mode
- Supports `low`, `medium`, and `high` optimization presets
- Displays the output file path and size summary when GUI optimization finishes

## How It Works

The optimizer opens the input PDF, renders each page at a chosen DPI, converts the rendered page to JPEG in memory, and inserts that JPEG into a new PDF.

This can reduce file size for scanned and image-heavy PDFs. It can also increase file size for vector-heavy or text-heavy PDFs, because those documents may originally store text and graphics more efficiently than a rasterized page image.

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
.\.venv\Scripts\python.exe .\pdf-optimizer.py
```

You can also launch the GUI explicitly with:

```powershell
.\.venv\Scripts\python.exe .\pdf-optimizer.py --gui
```

In GUI mode:
- Click `Browse...` to select a PDF
- Choose a preset from the dropdown
- Click `Compress` to start optimization
- Watch progress in the GUI
- If a terminal is present, progress also continues to print there
- When optimization finishes, the GUI shows:
  - output file location
  - original file size
  - optimized file size
  - either reduction percentage or size increase percentage
- The completion summary stays visible for about 10 seconds, then the window closes automatically

### CLI Mode

Run the script with an input PDF path to use the command-line workflow:

```powershell
.\.venv\Scripts\python.exe .\pdf-optimizer.py .\input.pdf
```

To choose a preset:

```powershell
.\.venv\Scripts\python.exe .\pdf-optimizer.py .\input.pdf --preset high
```

To choose a custom output path:

```powershell
.\.venv\Scripts\python.exe .\pdf-optimizer.py .\input.pdf --preset high --output .\out.pdf
```

In CLI mode:
- The script prints the output location before optimization starts
- The selected preset is shown in the terminal
- Progress is shown in the terminal during processing
- When optimization finishes, the script prints the output path, original size, output size, and either a reduction or size increase percentage

## Presets

- `low`: better visual quality, less aggressive size reduction
- `medium`: balanced default behavior
- `high`: more aggressive size reduction, smaller output for image-heavy PDFs

The preset names describe compression strength, not output quality. `high` means higher compression.

## Output File Naming

If you do not pass `--output`, the script saves the optimized PDF next to the input file using this naming pattern:

```text
original_name_compressed.pdf
```

For example:

```text
report.pdf -> report_compressed.pdf
```

## Important Notes

- This tool is best suited to scanned PDFs and image-heavy files
- It may increase file size for vector-heavy or text-heavy PDFs
- Text may no longer be selectable or searchable after optimization because pages are rebuilt as images
- Current preset mappings are:
  - `low`: `dpi=150`, `jpeg_quality=65`
  - `medium`: `dpi=120`, `jpeg_quality=50`
  - `high`: `dpi=96`, `jpeg_quality=35`
- If the output file already exists, the script warns you before continuing
- Input files must have a `.pdf` extension

## Project Files

- [pdf-optimizer.py](C:\Visual%20Studio%20Code%20Work\New\leargit\Real%20Life%20Projects\pdf-compressor\pdf-optimizer.py): main script with both CLI and GUI entry paths
- [requirements.txt](C:\Visual%20Studio%20Code%20Work\New\leargit\Real%20Life%20Projects\pdf-compressor\requirements.txt): Python dependencies
- [CHANGELOG.md](C:\Visual%20Studio%20Code%20Work\New\leargit\Real%20Life%20Projects\pdf-compressor\CHANGELOG.md): project change history
