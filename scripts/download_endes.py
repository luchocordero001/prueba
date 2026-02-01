#!/usr/bin/env python3
"""Download ENDES survey files from INEI URLs.

Example:
  python scripts/download_endes.py \
    --url "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1873/" \
    --output-dir data/raw

Tip:
  You can pass multiple --url values or a --url-file that lists one URL per line.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

DEFAULT_USER_AGENT = "Mozilla/5.0 (compatible; ENDESDownloader/1.0)"


class DownloadError(RuntimeError):
    """Raised when a download fails."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download ENDES survey files from INEI URLs.",
    )
    parser.add_argument(
        "--url",
        action="append",
        default=[],
        help="Direct URL to a downloadable file (can be repeated).",
    )
    parser.add_argument(
        "--url-file",
        help="Text file with one URL per line (comments with # are ignored).",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Directory to save downloads (default: data/raw).",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="User-Agent header to send with requests.",
    )
    parser.add_argument(
        "--referer",
        help="Optional Referer header to send with requests.",
    )
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        help="Additional header in 'Name: Value' format (can be repeated).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30).",
    )
    return parser.parse_args()


def build_headers(
    user_agent: str,
    referer: str | None,
    extra_headers: Iterable[str],
) -> dict[str, str]:
    headers = {"User-Agent": user_agent}
    if referer:
        headers["Referer"] = referer
    for raw_header in extra_headers:
        if ":" not in raw_header:
            raise DownloadError(f"Invalid header format: {raw_header!r}")
        name, value = raw_header.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def read_url_file(path: str | None) -> list[str]:
    if not path:
        return []
    urls: list[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            urls.append(stripped)
    return urls


def infer_filename(url: str, headers: dict[str, str]) -> str:
    content_disposition = headers.get("Content-Disposition", "")
    if "filename=" in content_disposition:
        value = content_disposition.split("filename=")[-1].strip().strip('"')
        if value:
            return value

    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if name:
        return name
    return "downloaded_file"


def download_file(
    url: str,
    output_dir: Path,
    headers: dict[str, str],
    timeout: int,
) -> Path:
    logging.info("Downloading %s", url)
    request = Request(url, headers=headers)
    temp_name = None
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise DownloadError(f"HTTP {response.status} for {url}")
        headers = {key: value for key, value in response.headers.items()}
        filename = infer_filename(url, headers)
        output_path = output_dir / filename
        output_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(dir=output_dir, delete=False) as temp_file:
            temp_name = temp_file.name
            shutil.copyfileobj(response, temp_file)

    size = os.path.getsize(temp_name) if temp_name else 0
    if size == 0:
        if temp_name and os.path.exists(temp_name):
            os.remove(temp_name)
        raise DownloadError(f"Downloaded file is empty: {output_path}")

    os.replace(temp_name, output_path)
    logging.info("Saved %s (%d bytes)", output_path, size)
    return output_path


def collect_urls(args: argparse.Namespace) -> list[str]:
    urls = list(args.url)
    urls.extend(read_url_file(args.url_file))
    unique_urls = []
    seen = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        unique_urls.append(url)
    return unique_urls


def main() -> int:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    urls = collect_urls(args)
    if not urls:
        logging.error("No URLs provided. Use --url or --url-file.")
        return 2

    output_dir = Path(args.output_dir)
    headers = build_headers(args.user_agent, args.referer, args.header)
    failures: list[str] = []
    for url in urls:
        try:
            download_file(url, output_dir, headers, args.timeout)
        except Exception as exc:  # noqa: BLE001 - provide error context
            logging.error("Failed to download %s: %s", url, exc)
            failures.append(url)

    if failures:
        logging.error("Failed downloads: %s", ", ".join(failures))
        return 1

    logging.info("All downloads completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
