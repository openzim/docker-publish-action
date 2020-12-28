#!/usr/bin/env/python3

import os
import re
import sys

perl_re = re.compile(r"^/(.+)/$")

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
exp = os.getenv("TAG_PATTERN", "")
if is_tag and exp:
    # convert from perl syntax (/pattern/) to python one
    if perl_re.match(exp):
        exp = perl_re.match(exp).groups()[-1]
    res = re.match(exp, ref)
    if res:
        if res.groups():
            # we have a matching tag with a group, use the group part
            version_tags.append(res.groups()[0])
        else:
            # we have a matching tag without a group, use git tag
            version_tags.append(ref)

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
