# docker-publish-action

[![GitHub release](https://img.shields.io/github/release/openzim/docker-publish-action.svg)](https://github.com/openzim/docker-publish-action/releases/latest)
[![GitHub marketplace](https://img.shields.io/badge/marketplace-docker--publish--action-blue?logo=github)](https://github.com/marketplace/actions/openzim-docker-publish-action)
[![CI workflow](https://img.shields.io/github/workflow/status/openzim/docker-publish-action/CI?label=CI&logo=github)](https://github.com/openzim/docker-publish-action/actions?workflow=CI)

A Github Action to automatically build and publish Openzim's images to **Both Docker Hub and Github Container Regisry**.


## Requirements

On ghcr.io, as for Docker Hub, first part of image name is the *user* owning the image. The user or organization must have enabled *Improved container support* first. Users do that in Settings > Feature preview and Organizations in Settings > Packages.

⚠️ this action is tailored for Openzim's workflow only. Use at your own risk.

## Usage


```yaml
name: Docker

on:
  push:
    branches:
      - master
    tags:
      - v*

jobs:
  build-and-push:
    name: Deploy Docker Image
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v2
      - name: Build and push
        uses: openzim/docker-publish-action@v1
        with:
          image-path: openzim/zimit
          on-master: dev
          tag-pattern: /^v*([0-9.]+)$/
          latest-on-tag: true
          restrict-to: openzim/zimit
          hub-username: ${{ secrets.DOCKERHUB_USERNAME }}
          hub-password: ${{ secrets.DOCKERHUB_PASSWORD }}
          ghcr-username: ${{ secrets.GHCR_USERNAME }}
          ghcr-token: ${{ secrets.GHCR_TOKEN }}
          build-args:
            VERSION={version}
            ARCH=amd64
```

**Note**: th top-part `on` is just a filter on running that workflow. You can omit it but it's safer to not run it on refs that you know won't trigger anything. See [documentation](https://docs.github.com/en/free-pro-team@latest/actions/reference/workflow-syntax-for-github-actions#on).

| Input | Usage |
| :--- | :--- |
| `image-path`<font color=red>\*</font> | **Name of your image on the registry** (without the version part).<br />Ex.: `openzim/zimit` would refer to [this image](https://hub.docker.com/r/openzim/zimit).<br />The same name is pushed on **both registries**. |
| `hub-username`<font color=red>\*</font> and `hub-password`<font color=red>\*</font> | **Docker Hub user credentials to push images with** |
| `ghcr-username`<font color=red>\*</font> and `ghcr-token`<font color=red>\*</font> | **Github user credentials to push images with**<br />Token is a [PAT](https://github.com/settings/tokens) with `repo, workflow, write:packages` permissions.|
| `context` | **Path in the repository to use as build context**<br />Relative to repository root. Defaults to `.`. Ex: `dnscache` or `workers/slave`. |
| `dockerfile` | **Path to the Dockerfile recipe, relative to context**<br />Defaults to `Dockerfile`. Use `../` syntax if dockerfile is outside context. |
| `on-master` | **Tag to apply for every commit on default branch**.<br />Omit it if you don't want to push an image for non-tagged commits.<br />Only applies to commits on your default branch (`master` or `main`) |
| `tag-pattern` | **Regular expression to match tags with**.<br />Only git tags matching this regexp will trigger a build+push to the corresponding docker tag.<br />If not specifying a group, whole git tag is used as is on docker. |
| `latest-on-tag` | **Whether to push to docker tag `:latest` on every matched tag** (see `tag-pattern`)<br />Value must be `true` or `false`. Defaults to `false`. |
| `restrict-to` | **Don't push if action is run for a different repository**<br />Specify as `{owner}/{repository}`. |
| `build-args` | **Arguments for `docker build --build-arg`**<br />Special value `{version}` will be replaced with the tag to set.<br />Use the `name=value` format and separate each by a space or new line.|


⚠️ After your initial run creating your image, you need to manually **make it public** via Github's UI (see packages) if you intend to pull images without authenticating.
