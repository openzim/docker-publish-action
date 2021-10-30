#!/usr/bin/env python3

import json
import os
import sys
import urllib.request


def get_main_branch(repository):
    url = "https://api.github.com/repos/{repository}".format(repository=repository)
    with urllib.request.urlopen(url) as uh:
        return json.load(uh).get("default_branch", None)


def getenv(name, default=None):
    """default branch is only available on repo-related trigger events (not schedule)"""
    if name == "DEFAULT_BRANCH":
        return os.getenv(name, get_main_branch(os.getenv("GITHUB_REPOSITORY")))
    return os.getenv(name, default)


def main():
    required_inputs = [
        "IMAGE_NAME",
        "REGISTRIES",
        "CREDENTIALS",
        "CONTEXT",
        "DOCKERFILE",
        "PLATFORMS",
        "LATEST_ON_TAG",
        "GITHUB_ENV",
        "GITHUB_REF",
        "GITHUB_ACTION_PATH",
        "GITHUB_REPOSITORY",
        "DEFAULT_BRANCH",
    ]
    optional_inputs = [
        "ON_MASTER",
        "BUILD_ARGS",
        "TAG_PATTERN",
        "MANUAL_TAG",
        "RESTRICT_TO",
        "DOCKER_BUILDX_VERSION",
        "WEBHOOK_URL",
    ]

    # fail early if missing this required info
    for env in required_inputs:
        if not getenv(env):
            print(f"missing param `{env}`, exiting.")
            return 1

    # `RESTRICT_TO` env prevents this from running from forked repositories
    if getenv("RESTRICT_TO") and getenv("GITHUB_REPOSITORY") != getenv("RESTRICT_TO"):
        print("not triggered on restricted-to repo, skipping.", getenv("RESTRICT_TO"))
        return 1

    with open(getenv("GITHUB_ENV"), "a") as fh:
        for env in required_inputs + optional_inputs:
            # don't write credentials to shared env! nor don't overwrite GH ones
            if env == "CREDENTIALS" or env.startswith("GITHUB_"):
                continue
            fh.write(
                "{env}={value}\n".format(
                    env=env, value=" ".join(getenv(env, "").strip().split("\n"))
                )
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
