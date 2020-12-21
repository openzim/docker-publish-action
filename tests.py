#!/usr/bin/env python3

import sys
import tempfile
import subprocess

import pytest


@pytest.fixture
def github_env():
    return tempfile.NamedTemporaryFile().name


@pytest.fixture
def repo_name():
    return "openzim/some-repo"


def get_env(
    github_env,
    repo_name,
    image_path,
    on_master=None,
    tag_pattern=None,
    restrict_to=None,
    latest_on_tag=False,
    on_main=False,
    tag=None,
):
    if on_main:
        ref = "refs/heads/main"
    else:
        ref = "refs/heads/abranch"
    if tag:
        ref = f"refs/tags/{tag}"
    return {
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REPOSITORY": repo_name,
        "GITHUB_ENV": github_env,
        "DEFAULT_BRANCH": "main",
        "GITHUB_REF": ref,
        "IMAGE_PATH": image_path,
        "ON_MASTER": on_master or "",
        "TAG_PATTERN": tag_pattern or "",
        "RESTRICT_TO": restrict_to or "",
        "LATEST_ON_TAG": "true" if latest_on_tag else "false",
    }


def extract_result(fpath):
    with open(fpath, "r") as fh:
        return [a for a in fh.read().strip().split("=", 1)[-1].split(",") if a.strip()]


def launch_and_retrieve(**kwargs):
    import pprint

    pprint.pprint(kwargs)
    subprocess.run([sys.executable, "./compute_tags.py"], env=kwargs)
    try:
        return extract_result(kwargs.get("GITHUB_ENV", "-"))
    except Exception:
        return []


def test_dnscache_main(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimfarm",
            image_path="openzim/dnscache",
            on_master="latest",
            tag_pattern="dnscache-v*",
            restrict_to="openzim/zimfarm",
            on_main=True,
        )
    )
    assert len(res) == 2
    assert "openzim/dnscache:latest" in res


def test_dnscache_tag(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimfarm",
            image_path="openzim/dnscache",
            on_master="latest",
            tag_pattern="dnscache-v*",
            restrict_to="openzim/zimfarm",
            on_main=True,
            tag="dnscache-v1.1",
        )
    )
    assert len(res) == 2
    assert "openzim/dnscache:1.1" in res


def test_dnscache_tag_and_latest(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimfarm",
            image_path="openzim/dnscache",
            on_master="latest",
            tag_pattern="dnscache-v*",
            restrict_to="openzim/zimfarm",
            on_main=True,
            tag="dnscache-v1.1",
            latest_on_tag=True,
        )
    )
    assert len(res) == 4
    assert "openzim/dnscache:latest" in res
    assert "openzim/dnscache:1.1" in res


def test_restrict_to(github_env):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="rgaudin/test",
            image_path="openzim/dnscache",
            on_master="latest",
            tag_pattern="dnscache-v*",
            restrict_to="openzim/zimfarm",
            on_main=True,
        )
    )
    assert len(res) == 0


def test_not_on_main(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_path="owner/image",
            on_master="latest",
            tag_pattern="dnscache-v*",
            on_main=False,
        )
    )
    assert len(res) == 0


def test_tag(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_path="owner/image",
            on_master="latest",
            tag_pattern="v*",
            on_main=False,
            tag="v1.2",
        )
    )
    assert len(res) == 2


def test_zimit_main(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimit",
            image_path="openzim/zimit",
            on_master="dev",
            tag_pattern="v*",
            restrict_to="openzim/zimit",
            on_main=True,
        )
    )
    assert len(res) == 2
    assert "openzim/zimit:dev" in res
    assert "ghcr.io/openzim/zimit:dev" in res


def test_zimit_tag(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimit",
            image_path="openzim/zimit",
            on_master="dev",
            tag_pattern="v*",
            restrict_to="openzim/zimit",
            on_main=True,
            tag="v1.1",
            latest_on_tag=True,
        )
    )
    assert len(res) == 4
    assert "openzim/zimit:1.1" in res
    assert "ghcr.io/openzim/zimit:1.1" in res
    assert "openzim/zimit:latest" in res
    assert "ghcr.io/openzim/zimit:latest" in res
