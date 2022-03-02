import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, Tuple

FULLDESC_MAX_FILE_SIZE = 25000  # 25KB
DESC_MAX_CHARS = 100


def get_credentials(registry: str) -> Tuple[str, str]:
    """Username, password for a registry reading environ"""
    credentials = dict(
        [
            [x.strip() for x in item.split("=")] if "=" in item else (item.strip(), "")
            for item in os.getenv("CREDENTIALS", "").split()
        ]
    )

    prefix = registry.upper().replace(".", "")
    return (
        credentials.get(f"{prefix}_USERNAME", ""),
        credentials.get(f"{prefix}_TOKEN", ""),
    )


def get_dockerhub_jwt(username: str, password: str) -> str:
    """docker.io's Hub API JWT from logging-in with username and password"""
    json_payload = json.dumps({"username": username, "password": password}).encode(
        "utf-8"
    )
    response = urllib.request.urlopen(
        urllib.request.Request(
            url="https://hub.docker.com/v2/users/login",
            data=json_payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Content-Length": len(json_payload),
            },
            method="POST",
        )
    )

    if not response.getcode() == 200:
        raise ValueError(
            "Unable to login to docker.io's hub API: HTTP {}: {}".format(
                response.getcode(), response.reason
            )
        )

    try:
        body = response.read()
        return json.loads(body.decode("UTF-8")).get("token")
    except Exception as exc:
        raise ValueError(
            "Unable to read hub API's response: {} -- {}".format(exc, body)
        )


def get_github_description(repository: str) -> str:
    """API-provided description of a public repository on Github"""
    response = urllib.request.urlopen(
        urllib.request.Request(
            url="https://api.github.com/repos/{}".format(
                os.getenv("GITHUB_REPOSITORY")
            ),
            headers={"Accept": "application/vnd.github.v3+json"},
        )
    )
    if not response.getcode() == 200:
        raise ValueError(
            "Unable to retrieve description from Github API HTTP {}: {}".format(
                response.getcode(), response.reason
            )
        )

    try:
        body = response.read()
        return json.loads(body.decode("UTF-8")).get("description")
    except Exception as exc:
        raise ValueError(
            "Unable to read Github's API's response: {} -- {}".format(exc, body)
        )


def do_update_dockerio_api(payload: Dict, token: str) -> int:
    json_payload = json.dumps(payload).encode("utf-8")
    response = urllib.request.urlopen(
        urllib.request.Request(
            url="https://hub.docker.com/v2/repositories/{}/".format(
                os.getenv("IMAGE_NAME")
            ),
            data=json_payload,
            headers={
                "Authorization": "JWT {}".format(token),
                "Content-Type": "application/json; charset=utf-8",
                "Content-Length": len(json_payload),
            },
            method="PATCH",
        )
    )

    if response.code >= 300:
        print("Unexpected HTTP {}/{} response".format(response.code, response.msg))
        print(response.read().decode("UTF-8"))
        return 1

    return 0


def read_overview_from(hint: str) -> str:
    """README/file content found and read from hint

    should hint be a relative path prefixed with `file`:
    or should hint be `auto`."""
    repo_root = pathlib.Path(os.getenv("GITHUB_WORKSPACE")).resolve()
    context_root = repo_root.joinpath(os.getenv("CONTEXT")).resolve()

    # relative file path
    if re.match(r"^file\:.+", hint):
        fpath = context_root.joinpath(re.sub(r"^file\:", "", hint)).resolve()
        if repo_root not in fpath.parents:
            raise ValueError("Cannot access files above repo root: {}".format(fpath))

        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                return fh.read(FULLDESC_MAX_FILE_SIZE)
        except Exception as exc:
            raise IOError(
                "Unable to read description file from {}: {}".format(fpath, exc)
            )

    # auto mode looks for README[.md|.rst] in context and parents
    if hint == "auto":
        for folder in (
            ([context_root] if context_root is not repo_root else [])
            + [p for p in context_root.parents if repo_root in p.parents]
            + [repo_root]
        ):
            for suffix in (".md", ".rst", ".txt", ""):
                fpath = folder.joinpath("README").with_suffix(suffix)
                if fpath.exists():
                    print("Using README from", fpath)
                    try:
                        with open(fpath, "r", encoding="utf-8") as fh:
                            return fh.read(FULLDESC_MAX_FILE_SIZE)
                    except Exception as exc:
                        raise IOError(
                            "Unable to read description file from {}: {}".format(
                                fpath, exc
                            )
                        )
                    break


def update_dockerio_api():
    description = os.getenv("REPO_DESCRIPTION")
    if description == "auto":
        description = get_github_description(os.getenv("GITHUB_REPOSITORY"))

    full_description = os.getenv("REPO_FULL_DESCRIPTION")
    if full_description and (
        re.match(r"^file\:.+", full_description) or full_description == "auto"
    ):
        full_description = read_overview_from(full_description)

    jwt_token = get_dockerhub_jwt(*get_credentials("docker.io"))

    payload = {}
    if description is not None:
        payload["description"] = description[:DESC_MAX_CHARS]
    if full_description is not None:
        payload["full_description"] = full_description

    print("Updating docker.io's Hub API for {}…".format(os.getenv("IMAGE_NAME")))
    print("---\n{}\n---".format(json.dumps(payload, indent=4)))

    # allow a few attempts at updating the Hub
    attempts = 0
    max_attempts = 3
    while attempts < max_attempts + 1:
        attempts += 1
        try:
            return do_update_dockerio_api(payload, jwt_token)
        except urllib.error.HTTPError as exc:
            print(
                "Unexpected Error on Attempt {}/{}: {}. ".format(
                    attempts, max_attempts, exc
                )
            )
            time.sleep(attempts * 30)
            continue
    print("Exhausted retry attempts")
    return 1


if __name__ == "__main__":
    if not os.getenv("SHOULD_UPDATE_DOCKERIO"):
        sys.exit(0)

    if not os.getenv("REPO_DESCRIPTION") and not os.getenv("REPO_FULL_DESCRIPTION"):
        print("no description, skipping.")
        sys.exit(0)
    sys.exit(update_dockerio_api())
