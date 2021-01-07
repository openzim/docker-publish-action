# v4

- added support for any registries (still defaults to docker.io + ghcr.io)
- replaced `dockerhub-*` and `ghcr-*` inputs with more flexible `credentials` one
- renamed `image-path` to `image-name`
- added `platforms` to support multiarch using `buildx`.
- refactored and simplified action and scripts
- now internally using two main info:
 - `DOCKER_TAG` with the version-only
 - `DOCKER_TAG_LATEST` `true` or `false`.

# v3

- added support for build-args

# v2

- Fixed tag applied to images on tag event while having not set any tag-pattern

# v1

- initial version
