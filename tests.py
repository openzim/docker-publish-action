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
    image_path,
    on_master=None,
    tag_pattern=None,
    restrict_to=None,
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
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            restrict_to="openzim/zimfarm",
            is_on_main_branch=True,
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
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            restrict_to="openzim/zimfarm",
            is_on_main_branch=True,
            is_tag="dnscache-v1.1",
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
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            restrict_to="openzim/zimfarm",
            is_on_main_branch=True,
            is_tag="dnscache-v1.1",
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
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            restrict_to="openzim/zimfarm",
            is_on_main_branch=True,
        )
    )
    assert len(res) == 0


def test_not_is_on_main_branch(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_path="owner/image",
            on_master="latest",
            tag_pattern="/^dnscache-v([0-9.]+)$/",
            is_on_main_branch=False,
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
            is_on_main_branch=False,
            is_tag="v1.2",
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
            tag_pattern="v([0-9.]+)",
            restrict_to="openzim/zimit",
            is_on_main_branch=True,
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
            tag_pattern="v([0-9.]+)",
            restrict_to="openzim/zimit",
            is_on_main_branch=True,
            is_tag="v1.1",
            latest_on_tag=True,
        )
    )
    assert len(res) == 4
    assert "openzim/zimit:1.1" in res
    assert "ghcr.io/openzim/zimit:1.1" in res
    assert "openzim/zimit:latest" in res
    assert "ghcr.io/openzim/zimit:latest" in res


def test_no_tag_on_master(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_path="openzim/test",
            tag_pattern="v*",
            is_on_main_branch=True,
        )
    )
    assert len(res) == 0


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
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_path=repo_name,
            tag_pattern=tag_pattern,
            is_tag=tag,
        )
    )
    assert len(res) == 2
    assert f"{repo_name}:{expected}" in res
    assert f"ghcr.io/{repo_name}:{expected}" in res


def test_tag_without_tag_pattern(github_env, repo_name):
    res = launch_and_retrieve(
        **get_env(
            github_env=github_env,
            repo_name=repo_name,
            image_path="openzim/zimfarm-task-worker",
            is_tag="uploader-v1.1.1",
        )
    )
    assert len(res) == 0
