import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request


def do_run_webhook(payload):
    req = urllib.request.Request(os.getenv("WEBHOOK_URL"))
    req.add_header("Content-Type", "application/json; charset=utf-8")
    json_payload = json.dumps(payload).encode("utf-8")
    req.add_header("Content-Length", len(json_payload))
    response = urllib.request.urlopen(req, json_payload)
    if response.code >= 300:
        print("Unexpected HTTP {}/{} response".format(response.code, response.msg))
        print(response.read().decode("UTF-8"))
        return 1


def run_webhook():
    latest = os.getenv("DOCKER_TAG_LATEST", "") == "true"
    payload = {
        "push_data": {
            "pushed_at": int(datetime.datetime.now().timestamp()),
            "images": [os.getenv("IMAGE_NAME")],
            "tag": "latest" if latest else os.getenv("DOCKER_TAG"),
            "pusher": "docker-publish-action",
        },
        "repository": {"repo_name": os.getenv("IMAGE_NAME")},
    }
    print("Calling webhook at {}".format(os.getenv("WEBHOOK_URL")))
    print("---\n{}\n---".format(json.dumps(payload, indent=4)))

    # webhook receiver might be fragile or have difficulties handling
    # concurrent requests.
    # ex: 2 close-apart requests for different apps in same sloppy project raises 409
    attempts = 0
    while attempts < 4:
        attempts += 1
        try:
            return do_run_webhook(payload)
        except urllib.error.HTTPError as exc:
            print("Unexpected {}. {} attempts remaining".format(exc, attempts))
            time.sleep(attempts * 30)
            continue
    print("Exhausted retry attempts")
    return 1


if __name__ == "__main__":
    if not os.getenv("WEBHOOK_URL"):
        sys.exit(0)

    if not os.getenv("DOCKER_TAG"):
        print("no tag pushed, skipping.")
        sys.exit(0)
    sys.exit(run_webhook())
