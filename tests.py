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
    # environment
    github_env,
    repo_name,
    # user configuration
    image_name,
    on_master=None,
    tag_pattern=None,
    latest_on_tag=False,
    # event config
    is_on_main_branch=False,
    is_tag=None,
):
    if is_on_main_branch:
        ref = "refs/heads/main"
    else:
        ref = "refs/heads/abranch"
    if is_tag:
        ref = f"refs/tags/{is_tag}"
    return {
        "GITHUB_EVENT_NAME": "push",
        "GITHUB_REPOSITORY": repo_name,
        "GITHUB_ENV": github_env,
        "DEFAULT_BRANCH": "main",
        "GITHUB_REF": ref,
        "IMAGE_NAME": image_name,
        "ON_MASTER": on_master or "",
        "TAG_PATTERN": tag_pattern or "",
        "LATEST_ON_TAG": "true" if latest_on_tag else "false",
    }


def extract_result(fpath):
    tag = latest = None
    with open(fpath, "r") as fh:
        for line in fh.readlines():
            print("line", line)
            if line.startswith("DOCKER_TAG="):
                tag = line.strip().split("=", 1)[-1]
            if line.startswith("DOCKER_TAG_LATEST="):
                latest = line.strip().split("=", 1)[-1] == "true"
    return tag, latest


def launch_and_retrieve(**kwargs):
    import pprint

    pprint.pprint(kwargs)
    subprocess.run([sys.executable, "./find_tag.py"], env=kwargs)
    try:
        return extract_result(kwargs.get("GITHUB_ENV", "-"))
    except Exception:
        return None, None


def test_dnscache_main(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimfarm",
            image_name="openzim/dnscache",
            on_master="latest",
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            is_on_main_branch=True,
        )
    )
    assert tag == "latest"
    assert latest is False


def test_dnscache_tag(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimfarm",
            image_name="openzim/dnscache",
            on_master="latest",
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            is_on_main_branch=True,
            is_tag="dnscache-v1.1",
        )
    )
    assert tag == "1.1"
    assert not latest


def test_dnscache_tag_and_latest(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimfarm",
            image_name="openzim/dnscache",
            on_master="latest",
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            is_on_main_branch=True,
            is_tag="dnscache-v1.1",
            latest_on_tag=True,
        )
    )
    assert tag == "1.1"
    assert latest


def test_not_is_on_main_branch(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_name="owner/image",
            on_master="latest",
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            is_on_main_branch=False,
        )
    )
    assert not tag
    assert not latest


def test_tag(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_name="owner/image",
            on_master="latest",
            tag_pattern="v*",
            is_on_main_branch=False,
            is_tag="v1.2",
        )
    )
    assert tag == "v1.2"
    assert not latest


def test_zimit_main(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimit",
            image_name="openzim/zimit",
            on_master="dev",
            tag_pattern="v([0-9.]+)",
            is_on_main_branch=True,
        )
    )
    assert tag == "dev"
    assert not latest


def test_zimit_tag(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name="openzim/zimit",
            image_name="openzim/zimit",
            on_master="dev",
            tag_pattern="v([0-9.]+)",
            is_on_main_branch=True,
            is_tag="v1.1",
            latest_on_tag=True,
        )
    )
    assert tag == "1.1"
    assert latest


def test_no_tag_on_master(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_name="openzim/test",
            tag_pattern="v*",
            is_on_main_branch=True,
        )
    )
    assert not tag
    assert not latest


@pytest.mark.parametrize(
    "tag_pattern, tag, expected",
    [
        # no group
        ("v.+", "v1", "v1"),
        ("v.+", "v1.1", "v1.1"),
        # group
        ("v([0-9.]+)", "v1", "1"),
        ("v([0-9.]+)", "v1.1", "1.1"),
        # caret for start
        ("^v([0-9.]+)", "v1", "1"),
        ("^v([0-9.]+)", "v1.1", "1.1"),
        # dollar for end
        ("^v([0-9.]+)$", "v1", "1"),
        ("^v([0-9.]+)$", "v1.1", "1.1"),
        # perl syntax
        ("/v([0-9.]+)/", "v1", "1"),
        ("/v([0-9.]+)/", "v1.1", "1.1"),
        # perl with caret and dollar
        ("/^v([0-9.]+)$/", "v1", "1"),
        ("/^v([0-9.]+)$/", "v1.1", "1.1"),
    ],
)
def test_tag_patterns(github_env, repo_name, tag_pattern, tag, expected):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_name=repo_name,
            tag_pattern=tag_pattern,
            is_tag=tag,
        )
    )
    assert tag == expected
    assert not latest


def test_tag_without_tag_pattern(github_env, repo_name):
    tag, latest = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_name="openzim/zimfarm-task-worker",
            is_tag="uploader-v1.1.1",
        )
    )
    assert not tag
    assert not latest
