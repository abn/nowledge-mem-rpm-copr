#!/usr/bin/env python3
"""
Dynamic Version Resolver and Packager for Nowledge Mem.
Fetches the latest version from https://nowled.ge/download-mem-rpm,
updates nowledge-mem.spec if needed, downloads the binary RPM,
and prepares the project for SRPM / Tito / COPR builds.
"""

import argparse
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

VERSION_REDIRECT_URL = "https://nowled.ge/download-mem-rpm"
SPEC_FILE_PATH = Path("nowledge-mem.spec")


def resolve_latest_version_and_url():
    print(f"Resolving latest version from {VERSION_REDIRECT_URL}...")
    req = urllib.request.Request(
        VERSION_REDIRECT_URL,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
    )
    with urllib.request.urlopen(req) as resp:
        final_url = resp.geturl()

    match = re.search(r"/app/([^/]+)/", final_url)
    if not match:
        raise RuntimeError(f"Could not extract version from URL: {final_url}")

    version = match.group(1)
    print(f"Resolved latest version: {version}")
    print(f"Direct download URL: {final_url}")
    return version, final_url


def get_current_spec_version():
    if not SPEC_FILE_PATH.exists():
        return None
    content = SPEC_FILE_PATH.read_text()
    match = re.search(r"^Version:\s*([^\s]+)", content, re.MULTILINE)
    return match.group(1) if match else None


def update_spec_version(new_version):
    content = SPEC_FILE_PATH.read_text()
    updated_content = re.sub(
        r"^(Version:\s*)[^\s]+",
        f"\\g<1>{new_version}",
        content,
        flags=re.MULTILINE,
    )
    # Reset release to 1 for new version
    updated_content = re.sub(
        r"^(Release:\s*)[^\s]+",
        r"\g<1>1%{?dist}",
        updated_content,
        flags=re.MULTILINE,
    )
    SPEC_FILE_PATH.write_text(updated_content)
    print(f"Updated {SPEC_FILE_PATH} Version to {new_version}")


def download_upstream_rpm(url, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # The source file expected by rpmbuild from Source0 URL is x86_64-unknown-linux-gnu.rpm
    target_file = output_dir / "x86_64-unknown-linux-gnu.rpm"
    print(f"Downloading {url} -> {target_file}...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
    )
    with urllib.request.urlopen(req) as resp, open(target_file, "wb") as f:
        while chunk := resp.read(8192):
            f.write(chunk)
    print(f"Successfully downloaded {target_file} ({target_file.stat().st_size} bytes)")
    return target_file


def main():
    parser = argparse.ArgumentParser(
        description="Check and update Nowledge Mem package version dynamically."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download and spec update even if version has not changed",
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        help="Directory to save downloaded RPM and build artifacts",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for new version without making changes",
    )

    args = parser.parse_args()

    latest_version, download_url = resolve_latest_version_and_url()
    current_version = get_current_spec_version()

    print(f"Current spec version: {current_version}")
    print(f"Latest online version: {latest_version}")

    is_new = current_version != latest_version

    if args.check_only:
        if is_new:
            print(f"New version available: {latest_version}")
            sys.exit(0)
        else:
            print("Already at latest version.")
            sys.exit(0)

    if is_new or args.force:
        if is_new:
            print(f"Updating package from {current_version} to {latest_version}...")
        else:
            print("Force re-fetching and updating package...")

        update_spec_version(latest_version)
        download_upstream_rpm(download_url, args.build_dir)
        print("Version update complete.")
    else:
        print("Package is up-to-date. Downloading upstream source if missing...")
        download_upstream_rpm(download_url, args.build_dir)


if __name__ == "__main__":
    main()
