#!/usr/bin/env/python3

import os
import re
import sys
import pathlib
import subprocess


def check_installed_version():
    version = subprocess.run(
        ["docker", "buildx", "version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    if version.returncode != 0:
        return None

    search = re.search(r"\sv?([0-9\.]+)[\-\+]", version.stdout.strip())
    if search:
        return search.groups()[-1]
    return None


def install_docker():
    req_version = os.getenv("DOCKER_BUILDX_VERSION", "0.31.1")
    inst_version = check_installed_version()

    if inst_version == req_version:
        print(f"already installed v{inst_version}")
        return 0

    print(f"Installing buildx v{req_version} (detected: {inst_version})")
    url = (
        f"https://github.com/docker/buildx/releases/download/v{req_version}/"
        f"buildx-v{req_version}.linux-amd64"
    )
    dest = pathlib.Path(os.getenv("HOME")) / ".docker" / "cli-plugins" / "docker-buildx"
    dest.parent.mkdir(parents=True, exist_ok=True)
    wget = subprocess.run(
        ["wget", "-O", str(dest), str(url)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    if wget.returncode != 0:
        print(f"Unable to download buildx binary: {wget.returncode}")
        print(wget.stdout)
        return 1
    dest.chmod(0o755)

    return 0


def install_platforms():
    if not os.getenv("PLATFORMS", "").split():
        return 0

    print("Installing qemu binaries")
    install = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--privileged",
            "tonistiigi/binfmt:latest",
            "--install",
            "all",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    if install.returncode != 0:
        print(f"Unable to download buildx binary: {install.returncode}")
        print(install.stdout)
        return 1
    return 0


if __name__ == "__main__":
    if not os.getenv("DOCKER_TAG"):
        print("no tag to build, skipping.")
        sys.exit(0)

    ret = install_docker()
    if ret != 0:
        sys.exit(ret)

    sys.exit(install_platforms())
