#!/usr/bin/env/python3


""" Find appropriate tag to build image for using inputs and store in GITHUB_ENV """

import os
import re


def find_tag_from_env():
    docker_tag_for_master = os.getenv("ON_MASTER")
    manual_tag = os.getenv("MANUAL_TAG", "")
    version_tag, latest = "", False

    ref = os.getenv("GITHUB_REF").split("/", 2)[-1]
    is_tag = os.getenv("GITHUB_REF").startswith("refs/tags/")
    tag_regexp = os.getenv("TAG_PATTERN", "")

    # manual override tag is set
    if manual_tag:
        version_tag = manual_tag
        latest = os.getenv("LATEST_ON_TAG", "").lower() == "true"
    # this is a commit on tag
    elif is_tag and tag_regexp:
        # convert from perl syntax (/pattern/) to python one
        perl_re = re.compile(r"^/(.+)/$")
        if perl_re.match(tag_regexp):
            tag_regexp = perl_re.match(tag_regexp).groups()[-1]
        res = re.match(tag_regexp, ref)
        if res:
            if res.groups():
                # we have a matching tag with a group, use the group part
                version_tag = res.groups()[0]
            else:
                # we have a matching tag without a group, use git tag
                version_tag = ref

            latest = os.getenv("LATEST_ON_TAG", "").lower() == "true"
    # this is a commit on default branch
    elif ref == os.getenv("DEFAULT_BRANCH") and docker_tag_for_master:
        version_tag = docker_tag_for_master

    # make sure we only use one tag if we requested "latest"
    if version_tag == "latest" and latest:
        latest = False

    return version_tag, latest


if __name__ == "__main__":
    version_tag, latest = find_tag_from_env()
    with open(os.getenv("GITHUB_ENV"), "a") as fh:
        fh.write(f"DOCKER_TAG={version_tag}\n")
        fh.write(f"DOCKER_TAG_LATEST={str(latest).lower()}\n")
