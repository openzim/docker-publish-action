#!/usr/bin/env/python3

import os
import sys
import subprocess


def build_and_push_from_env():
    image_name = os.getenv("IMAGE_NAME")
    platforms = os.getenv("PLATFORMS", "").split()
    registries = os.getenv("REGISTRIES", "").split()

    tag = os.getenv("DOCKER_TAG").strip()
    latest = os.getenv("DOCKER_TAG_LATEST", "") == "true"

    context = os.getenv("CONTEXT", ".")
    dockerfile = os.path.join(context, os.getenv("DOCKERFILE", "Dockerfile"))
    build_args = build_args = dict(
        [
            [x.strip() for x in item.split("=")] if "=" in item else (item.strip(), "")
            for item in os.getenv("BUILD_ARGS", "").split()
        ]
    )

    if len(platforms) > 1:
        print("Create and use a new builder instance")
        subprocess.run(["docker", "buildx", "create", "--use"])

    build_cmd = ["docker", "buildx", "build", context, "-f", dockerfile, "--push"]

    if build_args:
        for arg, value in build_args.items():
            if value == "{version}":
                value = tag
            build_cmd += ["--build-arg", f"{arg}={value}"]

    for registry in registries:
        build_cmd += ["--tag", f"{registry}/{image_name}:{tag}"]
        if latest:
            build_cmd += ["--tag", f"{registry}/{image_name}:latest"]

    for platform in platforms:
        build_cmd += ["--platform", platform]

    print(f"Running: {' '.join(build_cmd)}")
    build = subprocess.run(build_cmd)

    if build.returncode != 0:
        print(f"Unable to build image: {build.returncode}")
        return build.returncode
    return 0


if __name__ == "__main__":
    if not os.getenv("DOCKER_TAG"):
        print("no tag to build, skipping.")
        sys.exit(0)
    ret = build_and_push_from_env()
    # make sure to logout before aborting rest of worflow
    if ret != 0:
        subprocess.run(
            [
                "python3",
                os.path.join(os.getenv("GITHUB_ACTION_PATH"), "docker_logout.py"),
            ]
        )
    sys.exit(ret)
