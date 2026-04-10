import argparse
import io
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Optional

import fitz  # PyMuPDF
from PIL import Image


ProgressCallback = Callable[[int, int], None]

DEFAULT_DPI = 120
DEFAULT_JPEG_QUALITY = 50
AUTO_CLOSE_DELAY_MS = 10_000
DEFAULT_PRESET = "medium"

PRESET_SETTINGS = {
    "low": {"dpi": 96, "jpeg_quality": 35},
    "medium": {"dpi": 120, "jpeg_quality": 50},
    "high": {"dpi": 150, "jpeg_quality": 65},
}


def print_progress_bar(current: int, total: int, bar_length: int = 30) -> None:
    if total <= 0:
        return

    percent = current / total
    filled_length = int(bar_length * percent)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)

    print(f"\rCompression: |{bar}| {percent:.0%} ({current}/{total})", end="", flush=True)


def default_output_path(input_pdf: str) -> Path:
    input_path = Path(input_pdf)
    return input_path.with_name(f"{input_path.stem}_compressed{input_path.suffix}")


def settings_for_preset(preset: str) -> dict:
    try:
        return PRESET_SETTINGS[preset]
    except KeyError as exc:
        raise ValueError(f"Unknown preset: {preset}") from exc


def compress_pdf_for_remarkable(
    input_pdf: str,
    output_pdf: str,
    dpi: int = DEFAULT_DPI,
    jpeg_quality: int = DEFAULT_JPEG_QUALITY,
    progress_callback: Optional[ProgressCallback] = None,
) -> dict:
    """
    Compress a PDF by rendering each page to a JPEG image and rebuilding a new PDF.

    Best for:
    - scanned PDFs
    - image-heavy books
    - PDFs that feel slow on e-ink devices

    Trade-offs:
    - text may no longer be selectable/searchable
    - too low DPI or quality may reduce readability
    """

    input_path = Path(input_pdf)
    output_path = Path(output_pdf)

    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    if input_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    src_doc = fitz.open(str(input_path))
    out_doc = fitz.open()

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    try:
        total_pages = len(src_doc)
        print(f"Opened: {input_path}")
        print(f"Total pages: {total_pages}")
        print(f"Using DPI={dpi}, JPEG quality={jpeg_quality}")

        for page_index in range(total_pages):
            page_number = page_index + 1
            page = src_doc.load_page(page_index)
            pix = page.get_pixmap(matrix=matrix, alpha=False)

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=jpeg_quality, optimize=True)
            img_bytes.seek(0)

            rect = page.rect
            new_page = out_doc.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(new_page.rect, stream=img_bytes.getvalue())

            print_progress_bar(page_number, total_pages)
            if progress_callback is not None:
                progress_callback(page_number, total_pages)

        print()

        out_doc.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True,
        )

        print("\nDone.")
        print(f"Compressed PDF saved to: {output_path}")

        original_size = input_path.stat().st_size / (1024 * 1024)
        new_size = output_path.stat().st_size / (1024 * 1024)

        print(f"Original size:  {original_size:.2f} MB")
        print(f"New size:       {new_size:.2f} MB")

        reduction = 0.0
        if original_size > 0:
            reduction = ((original_size - new_size) / original_size) * 100
            print(f"Reduction:      {reduction:.1f}%")

        return {
            "input_path": str(input_path),
            "output_path": str(output_path),
            "total_pages": total_pages,
            "original_size_mb": original_size,
            "new_size_mb": new_size,
            "reduction_percent": reduction,
        }
    finally:
        src_doc.close()
        out_doc.close()


def run_cli(
    input_pdf: str,
    output_pdf: Optional[str] = None,
    preset: str = DEFAULT_PRESET,
) -> int:
    output_path = Path(output_pdf) if output_pdf else default_output_path(input_pdf)
    settings = settings_for_preset(preset)

    print(f"Output will be saved as: {output_path}")
    print(f"Using preset: {preset}")
    if output_path.exists():
        print("Output file already exists.")

    try:
        compress_pdf_for_remarkable(
            input_pdf=input_pdf,
            output_pdf=str(output_path),
            dpi=settings["dpi"],
            jpeg_quality=settings["jpeg_quality"],
        )
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    return 0


def format_completion_details(result: dict) -> str:
    return (
        f"Output file: {result['output_path']}\n"
        f"Original size: {result['original_size_mb']:.2f} MB\n"
        f"Compressed size: {result['new_size_mb']:.2f} MB\n"
        f"Reduction: {result['reduction_percent']:.1f}%"
    )


class PdfCompressorGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF Compressor")
        self.root.resizable(False, False)

        self.events: "queue.Queue[tuple]" = queue.Queue()
        self.worker_thread: Optional[threading.Thread] = None
        self.close_timer_id: Optional[str] = None

        self.input_path_var = tk.StringVar()
        self.preset_var = tk.StringVar(value=DEFAULT_PRESET)
        self.output_path_var = tk.StringVar(value="Output path will appear here.")
        self.status_var = tk.StringVar(value="Select a PDF file to begin.")
        self.progress_var = tk.DoubleVar(value=0.0)

        self._build_widgets()
        self.root.after(100, self._process_events)

    def _build_widgets(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Input PDF").grid(row=0, column=0, sticky="w")
        input_entry = ttk.Entry(
            frame,
            textvariable=self.input_path_var,
            width=52,
            state="readonly",
        )
        input_entry.grid(row=1, column=0, padx=(0, 8), pady=(4, 12), sticky="ew")

        self.browse_button = ttk.Button(
            frame,
            text="Browse...",
            command=self._select_file,
        )
        self.browse_button.grid(row=1, column=1, pady=(4, 12), sticky="ew")

        ttk.Label(frame, text="Preset").grid(row=2, column=0, sticky="w")
        self.preset_dropdown = ttk.Combobox(
            frame,
            textvariable=self.preset_var,
            values=tuple(PRESET_SETTINGS),
            state="readonly",
            width=20,
        )
        self.preset_dropdown.grid(row=3, column=0, columnspan=2, pady=(4, 12), sticky="ew")

        self.compress_button = ttk.Button(
            frame,
            text="Compress",
            command=self._start_compression,
        )
        self.compress_button.grid(row=4, column=0, columnspan=2, pady=(0, 12), sticky="ew")

        self.progress_bar = ttk.Progressbar(
            frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            variable=self.progress_var,
            length=420,
        )
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky="ew")

        ttk.Label(frame, textvariable=self.status_var, wraplength=420).grid(
            row=6,
            column=0,
            columnspan=2,
            pady=(12, 8),
            sticky="w",
        )

        ttk.Label(frame, text="Output").grid(row=7, column=0, columnspan=2, sticky="w")
        ttk.Label(
            frame,
            textvariable=self.output_path_var,
            wraplength=420,
            justify="left",
        ).grid(row=8, column=0, columnspan=2, pady=(4, 0), sticky="w")

        frame.columnconfigure(0, weight=1)

    def _select_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select a PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not selected:
            return

        self._cancel_auto_close()
        self.input_path_var.set(selected)
        self.output_path_var.set(str(default_output_path(selected)))
        self.status_var.set("Ready to compress.")
        self.progress_var.set(0.0)

    def _start_compression(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            return

        input_path = self.input_path_var.get().strip()
        if not input_path:
            messagebox.showerror("No file selected", "Select a PDF file before compressing.")
            return

        preset = self.preset_var.get()
        output_path = str(default_output_path(input_path))
        self.output_path_var.set(output_path)
        self.status_var.set(
            f"Compressing with the {preset} preset... Progress is also shown in the terminal."
        )
        self.progress_var.set(0.0)
        self._cancel_auto_close()
        self._set_controls_enabled(False)

        self.worker_thread = threading.Thread(
            target=self._compress_worker,
            args=(input_path, output_path, preset),
            daemon=True,
        )
        self.worker_thread.start()

    def _compress_worker(self, input_path: str, output_path: str, preset: str) -> None:
        settings = settings_for_preset(preset)
        try:
            result = compress_pdf_for_remarkable(
                input_pdf=input_path,
                output_pdf=output_path,
                dpi=settings["dpi"],
                jpeg_quality=settings["jpeg_quality"],
                progress_callback=lambda current, total: self.events.put(
                    ("progress", current, total)
                ),
            )
            self.events.put(("success", result))
        except Exception as exc:
            self.events.put(("error", str(exc)))

    def _process_events(self) -> None:
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break

            event_type = event[0]
            if event_type == "progress":
                _, current, total = event
                percent = (current / total) * 100 if total else 0
                self.progress_var.set(percent)
                self.status_var.set(f"Compressing page {current} of {total}...")
            elif event_type == "success":
                _, result = event
                self.progress_var.set(100.0)
                self.output_path_var.set(format_completion_details(result))
                self.status_var.set(
                    "Compression complete. This window will close automatically in about 10 seconds."
                )
                self._set_controls_enabled(True)
                self.close_timer_id = self.root.after(AUTO_CLOSE_DELAY_MS, self.root.destroy)
            elif event_type == "error":
                _, message = event
                self.status_var.set(f"Compression failed: {message}")
                self._set_controls_enabled(True)
                messagebox.showerror("Compression failed", message)

        self.root.after(100, self._process_events)

    def _cancel_auto_close(self) -> None:
        if self.close_timer_id is not None:
            self.root.after_cancel(self.close_timer_id)
            self.close_timer_id = None

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.browse_button.config(state=state)
        self.compress_button.config(state=state)
        self.preset_dropdown.config(state="readonly" if enabled else "disabled")


def run_gui() -> int:
    root = tk.Tk()
    PdfCompressorGui(root)
    root.mainloop()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compress a PDF for e-ink or low-storage use.",
    )
    parser.add_argument("input_pdf", nargs="?", help="Path to the input PDF file.")
    parser.add_argument(
        "--output",
        help="Optional output path. Defaults to <input>_compressed.pdf.",
    )
    parser.add_argument(
        "--preset",
        choices=tuple(PRESET_SETTINGS),
        default=DEFAULT_PRESET,
        help="Compression preset for CLI mode.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the Tkinter GUI frontend.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui or not argv:
        return run_gui()

    if not args.input_pdf:
        parser.error("input_pdf is required unless running with no arguments or --gui")

    return run_cli(args.input_pdf, args.output, args.preset)


if __name__ == "__main__":
    sys.exit(main())
