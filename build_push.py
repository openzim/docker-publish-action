#!/usr/bin/env/python3

import os
import sys
import itertools
import subprocess

tags = [t for t in os.getenv("IMAGE_TAGS", "").strip().split(",") if t]
tags_args = list(itertools.chain(*[["-t", tag] for tag in tags]))

if not tags:
    print("No tags to push to, skipping.")
    sys.exit(0)

context = os.getenv("CONTEXT", ".")
dockerfile = os.getenv("DOCKERFILE", "./Dockerfile")

# login to dockerhub
print("Logging into Docker hub…")
hub_login = subprocess.run(
    [
        "docker",
        "login",
        "--username",
        os.getenv("DOCKERHUB_USERNAME", ""),
        "--password-stdin",
    ],
    input=os.getenv("DOCKERHUB_PASSWORD", "").strip() + "\n",
    universal_newlines=True,
)
if hub_login.returncode != 0:
    print(f"Unable to login to Docker Hub: {hub_login.returncode}")
    sys.exit(hub_login.returncode)

print("Successfuly logged in to Hub!")

# login to ghcr.io
print("Logging into ghcr.io…")
ghcr_login = subprocess.run(
    [
        "docker",
        "login",
        "--username",
        os.getenv("GHCR_USERNAME", ""),
        "--password-stdin",
        "ghcr.io",
    ],
    input=os.getenv("GHCR_TOKEN", "").strip() + "\n",
    universal_newlines=True,
)
if ghcr_login.returncode != 0:
    print(f"Unable to login to GHCR: {ghcr_login.returncode}")
    sys.exit(ghcr_login.returncode)

print("Successfuly logged in to GHCR!")

# sys.exit(0)

# build image
build = subprocess.run(["docker", "build", context, "-f", dockerfile] + tags_args)
if build.returncode != 0:
    print(f"Unable to build image: {build.returncode}")
    sys.exit(build.returncode)

# push image
has_failure = False
for tag in tags:
    print(f"Pushing to {tag}")
    push = subprocess.run(["docker", "push", tag])
    if push.returncode != 0:
        print(f"Unable to push image to {tag}: {push.returncode}")
        has_failure = True


# logout from registries
subprocess.run(["docker", "logout", "ghcr.io"])
subprocess.run(["docker", "logout"])


if has_failure:
    sys.exit(push.returncode)
