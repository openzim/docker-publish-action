#!/usr/bin/env/python3

import os
import sys
import subprocess


def docker_login_from_env():

    credentials = dict(
        [
            [x.strip() for x in item.split("=")] if "=" in item else (item.strip(), "")
            for item in os.getenv("CREDENTIALS", "").split()
        ]
    )

    def get_credentials(registry):
        prefix = registry.upper().replace(".", "")
        return (
            credentials.get(f"{prefix}_USERNAME", ""),
            credentials.get(f"{prefix}_TOKEN", ""),
        )

    for registry in os.getenv("REGISTRIES", "").split():
        print(f"Logging into {registry}…")
        username, token = get_credentials(registry)
        login = subprocess.run(
            ["docker", "login", "--username", username, "--password-stdin", registry],
            input=f"{token}\n",
            universal_newlines=True,
        )
        if login.returncode != 0:
            print(f"Unable to login to Docker Hub: {login.returncode}")
            sys.exit(login.returncode)
        print(f"Successfuly logged into {registry}!")


if __name__ == "__main__":
    if not os.getenv("DOCKER_TAG"):
        print("no tag to build, skipping.")
        sys.exit(0)

    docker_login_from_env()
