#!/usr/bin/env/python3

import os
import re
import sys

if os.getenv("RESTRICT_TO") and os.getenv("GITHUB_REPOSITORY") != os.getenv(
    "RESTRICT_TO"
):
    print("not triggered on restricted-to repo, skipping.", os.getenv("RESTRICT_TO"))
    sys.exit(1)

if os.getenv("GITHUB_EVENT_NAME") != "push":
    print("not push event, skipping.", os.getenv("GITHUB_EVENT_NAME"))
    sys.exit(0)

print("Computing Image Tags…")

version_tags = []
image_path = os.getenv("IMAGE_PATH")

ref = os.getenv("GITHUB_REF").split("/", 2)[-1]
is_tag = os.getenv("GITHUB_REF").startswith("refs/tags/")
if is_tag:
    exp = os.getenv("TAG_PATTERN", "").replace("*", "(.+)")
    res = re.match(exp, ref)
    if res:
        version_tags.append(res.groups()[0])

        if os.getenv("LATEST_ON_TAG", "").lower() == "true":
            version_tags.append("latest")

# commit on default branch
elif ref == os.getenv("DEFAULT_BRANCH"):
    if os.getenv("ON_MASTER"):
        version_tags.append(os.getenv("ON_MASTER"))

image_tags = []
for t in set(version_tags):
    image_tags.append(f"{image_path}:{t}")
    image_tags.append(f"ghcr.io/{image_path}:{t}")

# write image_tags to env so it's available to future steps
with open(os.getenv("GITHUB_ENV"), "a") as fh:
    fh.write("IMAGE_TAGS={}\n".format(",".join(image_tags)))
