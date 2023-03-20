#!/usr/bin/env/python3

import os
import sys
import subprocess


def docker_logout_from_env():
    for registry in os.getenv("REGISTRIES", "").split():
        print(f"Logging out of {registry}…")
        logout = subprocess.run(["docker", "logout", registry])
        if logout.returncode != 0:
            print(f"Unable to login to {registry}: {logout.returncode}")
        print(f"Successfuly logged out of {registry}!")


if __name__ == "__main__":
    if not os.getenv("DOCKER_TAG"):
        print("no tag to build, skipping.")
        sys.exit(0)

    docker_logout_from_env()
