import os
import sys


def main():
    image_name = os.getenv("IMAGE_NAME")
    tag = os.getenv("DOCKER_TAG").strip()
    latest = os.getenv("DOCKER_TAG_LATEST", "") == "true"

    print(
        "About to build and push a {platform} image to:".format(
            platform=",".join(os.getenv("PLATFORMS", "").split())
        )
    )
    for registry in os.getenv("REGISTRIES", "").split():
        print(
            "{registry}/{image_name}:{tag}".format(
                registry=registry, image_name=image_name, tag=tag
            )
        )
        if latest:
            print(
                "{registry}/{image_name}:{tag}".format(
                    registry=registry, image_name=image_name, tag="latest"
                )
            )


if __name__ == "__main__":
    if not os.getenv("DOCKER_TAG"):
        print("no tag to build, skipping.")
        sys.exit(0)
    main()
