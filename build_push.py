#!/usr/bin/env/python3

import os
import sys
import json
import subprocess

tags = [t for t in os.getenv("VERSION_TAGS", "").strip().split(",") if t]

if not tags:
    print("No tags to push to, skipping.")
    sys.exit(0)

context = os.getenv("CONTEXT", ".")
dockerfile = os.path.join(context, os.getenv("DOCKERFILE", "Dockerfile"))
build_args = json.loads(os.getenv("BUILD_ARGS", "{}"))
image_path = os.getenv("IMAGE_PATH")

if not image_path:
    print("missing image_path, exiting.")
    sys.exit(1)

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

all_tags = []

# looping over tags so we can create tag-aware build-arg.
for tag in tags:
    # build list of --build-arg
    build_args_arg = []
    for arg, value in build_args.items():
        if value == "{version}":
            value = tag
        build_args_arg += ["--build-arg", f"{arg}={value}"]

    # tag it for both registries
    tags_args = ["--tag", f"{image_path}:{tag}", "--tag", f"ghcr.io/{image_path}:{tag}"]

    # build image
    cmd = ["docker", "build", context, "-f", dockerfile] + build_args_arg + tags_args
    print(cmd)
    build = subprocess.run(cmd)
    if build.returncode != 0:
        print(f"Unable to build image: {build.returncode}")
        sys.exit(build.returncode)
    all_tags += tags_args

# push image
has_failure = False
for tag in all_tags:
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
