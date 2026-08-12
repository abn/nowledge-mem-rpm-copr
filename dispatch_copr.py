#!/usr/bin/env python3
"""
Dispatch Nowledge Mem SRPM build to Fedora COPR.
"""

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path


def check_copr_config():
    config_file = Path.home() / ".config" / "copr"
    if not config_file.exists():
        print("=" * 70)
        print("WARNING: COPR configuration file ~/.config/copr was not found.")
        print("To authenticate with COPR, follow these steps:")
        print("1. Visit https://copr.fedorainfracloud.org/api/")
        print("2. Copy the API configuration snippet.")
        print("3. Save it to ~/.config/copr")
        print("=" * 70)
        return False
    return True


def find_latest_srpm(build_dir):
    pattern = os.path.join(build_dir, "*.src.rpm")
    srpms = glob.glob(pattern)
    if not srpms:
        return None
    # Sort by modification time, latest first
    srpms.sort(key=os.path.getmtime, reverse=True)
    return srpms[0]


def main():
    parser = argparse.ArgumentParser(description="Dispatch build to Fedora COPR")
    parser.add_argument(
        "--repo",
        default="abn/nowledge-mem",
        help="COPR repository in owner/project format (default: abn/nowledge-mem)",
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        help="Path to build directory containing SRPMs (default: build)",
    )
    parser.add_argument(
        "--nowait",
        action="store_true",
        help="Do not wait for COPR build completion",
    )

    args = parser.parse_args()

    # Locate SRPM
    srpm_path = find_latest_srpm(args.build_dir)
    if not srpm_path:
        print(f"Error: No .src.rpm file found in {args.build_dir}/.")
        print("Run 'make srpm' first to generate the Source RPM.")
        sys.exit(1)

    print(f"Found SRPM: {srpm_path}")

    # Verify COPR config
    has_config = check_copr_config()

    # Determine copr-cli binary executable path
    venv_copr = os.path.join(os.path.dirname(__file__), ".venv", "bin", "copr-cli")
    copr_cmd = venv_copr if os.path.exists(venv_copr) else "copr-cli"

    cmd = [copr_cmd, "build", args.repo, srpm_path]
    if args.nowait:
        cmd.append("--nowait")

    print(f"Executing: {' '.join(cmd)}")

    if not has_config:
        print("\nNote: Command is ready to dispatch once ~/.config/copr is present.")
        print(f"Direct command string: {' '.join(cmd)}")
        sys.exit(1)

    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("\nCOPR build dispatched successfully!")
    else:
        print(f"\nCOPR build dispatch failed with exit code {result.returncode}.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
