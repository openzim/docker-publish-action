# docker-publish-action

[![GitHub release](https://img.shields.io/github/release/openzim/docker-publish-action.svg)](https://github.com/openzim/docker-publish-action/releases/latest)
[![GitHub marketplace](https://img.shields.io/badge/marketplace-docker--publish--action-blue?logo=github)](https://github.com/marketplace/actions/openzim-docker-publish-action)
[![CI workflow](https://img.shields.io/github/workflow/status/openzim/docker-publish-action/CI?label=CI&logo=github)](https://github.com/openzim/docker-publish-action/actions?workflow=CI)

A Github Action to automatically build and publish Openzim's images to **Both Docker Hub and Github Container Regisry**.


## Requirements

On ghcr.io, as for Docker Hub, first part of image name is the *user* owning the image. The user or organization must have enabled *Improved container support* first. Users do that in Settings > Feature preview and Organizations in Settings > Packages.

⚠️ this action is tailored for Openzim's workflow only. Use at your own risk.

## Usage

### Minimal

```yaml
jobs:
  build-and-push:
    name: Deploy Docker Image
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v2
      - name: Build and push
        uses: openzim/docker-publish-action@v4
        with:
          image-name: openzim/zimit
            DOCKERIO_USERNAME=${{ secrets.DOCKERHUB_USERNAME }}
            DOCKERIO_TOKEN=${{ secrets.DOCKERHUB_PASSWORD }}
            GHCR_IO_USERNAME=${{ secrets.GHCR_USERNAME }}
            GHCR_IO_TOKEN=${{ secrets.GHCR_TOKEN }}
          on-master: latest
```

### Complete

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
        uses: openzim/docker-publish-action@v4
        with:
          image-name: openzim/zimit
          registries: |
            docker.io
            gcr.io
          credentials: |
            DOCKERIO_USERNAME=${{ secrets.DOCKERHUB_USERNAME }}
            DOCKERIO_TOKEN=${{ secrets.DOCKERHUB_PASSWORD }}
            GCR_IO_USERNAME=${{ secrets.GOOGLE_USERNAME }}
            GCR_IO_TOKEN=${{ secrets.GOOGLE_TOKEN }}
          context: sub-folder
          on-master: dev
          tag-pattern: /^v*([0-9.]+)$/
          latest-on-tag: true
          restrict-to: openzim/zimit
          build-args:
            VERSION={tag}
```

**Note**: th top-part `on` is just a filter on running that workflow. You can omit it but it's safer to not run it on refs that you know won't trigger anything. See [documentation](https://docs.github.com/en/free-pro-team@latest/actions/reference/workflow-syntax-for-github-actions#on).

| Input | Usage |
| :--- | :--- |
| `image-name`<font color=red>\*</font> | **Name of your image on the registry** (without the version part).<br />Ex.: `openzim/zimit` would refer to [this image](https://hub.docker.com/r/openzim/zimit).<br />The same name is pushed to **all registries**. |
| `registries` | **List of registries to push images to** (domain name only).<br />Ex.: `docker.io` for Docker Hub, `ghcr.io`, `gcr.io`, etc.<br />Defaults to `docker.io ghcr.io`. |
| `credentials`<font color=red>\*</font> | **List of credentials for all registries**<br />Use the `REGISTRY_USERNAME=xxx` and `REGISTRY_TOKEN=xxx` formats to specify.<br />`REGISTRY` refers to the uppercase registry domain name without `.`.<br />Ex: `GHCRIO_USERNAME=xxx` for `ghcr.io`.<br />_Notes_: Github token is a [PAT](https://github.com/settings/tokens) with `repo, workflow, write:packages` permissions.<br />Docker hub token is account password.|
| `context` | **Path in the repository to use as build context**<br />Relative to repository root.  Ex: `dnscache` or `workers/slave`.<br />Defaults to `.`. |
| `dockerfile` | **Path to the Dockerfile recipe, relative to context**<br />Use `../` syntax if dockerfile is outside context.<br />Defaults to `Dockerfile`. |
| `build-args` | **Arguments for `docker build --build-arg`**<br />Special value `{tag}` will be replaced with the tag to set.<br />Use the `name=value` format and separate each by a space or new line.|
| `platforms` | **List of platforms to build-for**.<br />Ex.: `linux/armv/v7 linux/amd64`.<br />Defaults to `linux/amd64`. |
| `on-master` | **Tag to apply for every commit on default branch**.<br />Omit it if you don't want to push an image for non-tagged commits.<br />Only applies to commits on your default branch (`master` or `main`) |
| `tag-pattern` | **Regular expression to match tags with**.<br />Only git tags matching this regexp will trigger a build+push to the corresponding docker tag.<br />If not specifying a group, whole git tag is used as is on docker. |
| `latest-on-tag` | **Whether to push to docker tag `:latest` on every matched tag** (see `tag-pattern`)<br />Also applies to `manual-tag`.<br />Value must be `true` or `false`. Defaults to `false`. |
| `restrict-to` | **Don't push if action is run for a different repository**<br />Specify as `{owner}/{repository}`. |



⚠️ After your initial run creating your image, you need to manually **make it public** via Github's UI (see packages) if you intend to pull images without authenticating.
