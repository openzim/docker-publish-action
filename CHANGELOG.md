# v10

- Defaults to ghcr.io only (removed docker.io from default)
- Using buildx v0.31.1  # 2026-02-13

# v9

- Fixed schedule runs with new Actions behavior

# v8

- now supports setting description and overview on docker.io's Hub

# v7

- now supports adding a `webhook` to call on successful push

# v6

- now supports schedule runs

# v5

- now supports a manual tag override through `manual-tag`.
- special `build-arg` value `{version}` replaced with `{tag}`.

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
