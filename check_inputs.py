#!/usr/bin/env python3

import os
import sys


def main():
    required_inputs = [
        "IMAGE_NAME",
        "REGISTRIES",
        "CREDENTIALS",
        "CONTEXT",
        "DOCKERFILE",
        "PLATFORMS",
        "LATEST_ON_TAG",
        "DEFAULT_BRANCH",
        "GITHUB_ENV",
        "GITHUB_REF",
        "GITHUB_ACTION_PATH",
        "GITHUB_REPOSITORY",
    ]
    optional_inputs = [
        "ON_MASTER",
        "BUILD_ARGS",
        "TAG_PATTERN",
        "MANUAL_TAG",
        "RESTRICT_TO",
        "DOCKER_BUILDX_VERSION",
    ]

    # fail early if missing this required info
    for env in required_inputs:
        if not os.getenv(env):
            print(f"missing param `{env}`, exiting.")
            return 1

    # `RESTRICT_TO` env prevents this from running from forked repositories
    if os.getenv("RESTRICT_TO") and os.getenv("GITHUB_REPOSITORY") != os.getenv(
        "RESTRICT_TO"
    ):
        print(
            "not triggered on restricted-to repo, skipping.", os.getenv("RESTRICT_TO")
        )
        return 1

    with open(os.getenv("GITHUB_ENV"), "a") as fh:
        for env in required_inputs + optional_inputs:
            # don't write credentials to shared env! nor don't overwrite GH ones
            if env == "CREDENTIALS" or env.startswith("GITHUB_"):
                continue
            fh.write(
                "{env}={value}\n".format(
                    env=env, value=" ".join(os.getenv(env, "").strip().split("\n"))
                )
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
