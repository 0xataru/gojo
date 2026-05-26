import os
from datetime import date, timedelta

import requests
from requests.auth import HTTPBasicAuth

# === SETTINGS FROM ENV ===
JIRA_URL = os.environ["JIRA_URL"]
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
JIRA_PROJECT = os.environ["JIRA_PROJECT"]
JIRA_BOARD_ID = os.environ["JIRA_BOARD_ID"]
JIRA_BOARD_URL = f"{JIRA_URL}/jira/software/projects/{JIRA_PROJECT}/boards/{JIRA_BOARD_ID}"

SLACK_TOKEN = os.environ["SLACK_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}


def get_active_incidents():
    """Active incidents by priority (status not Done)"""
    counts = {"High": 0, "Medium": 0, "Low": 0}

    for priority in counts:
        jql = (
            f"project = {JIRA_PROJECT} "
            f'AND priority = "{priority}" '
            f"AND statusCategory != Done"
        )
        resp = requests.post(
            f"{JIRA_URL}/rest/api/3/search/jql",
            headers={**headers, "Content-Type": "application/json"},
            auth=auth,
            json={"jql": jql, "maxResults": 500, "fields": ["id"]},
        )
        if not resp.ok:
            print(f"Jira error {resp.status_code}: {resp.text}")
        resp.raise_for_status()
        counts[priority] = len(resp.json().get("issues", []))

    return counts


def get_resolved_yesterday():
    """Incidents resolved yesterday (status changed to Done)"""
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = date.today().strftime("%Y-%m-%d")
    jql = (
        f"project = {JIRA_PROJECT} "
        f"AND statusCategory = Done "
        f'AND updated >= "{yesterday}" '
        f'AND updated < "{today}"'
    )
    resp = requests.post(
        f"{JIRA_URL}/rest/api/3/search/jql",
        headers={**headers, "Content-Type": "application/json"},
        auth=auth,
        json={"jql": jql, "maxResults": 500, "fields": ["id"]},
    )
    if not resp.ok:
        print(f"Jira error {resp.status_code}: {resp.text}")
    resp.raise_for_status()
    return len(resp.json().get("issues", []))


def build_slack_message(active, resolved_yesterday):
    total = sum(active.values())
    today = date.today().strftime("%B %d, %Y")
    weekday = date.today().strftime("%A")

    resolved_text = (
        f"{resolved_yesterday} resolved"
        if resolved_yesterday > 0
        else "0 resolved (none)"
    )

    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 PS Incident Status — {weekday}, {today}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"🔴 *High*   › Active: `{active['High']}`\n"
                        f"🟠 *Medium* › Active: `{active['Medium']}`\n"
                        f"🟡 *Low*    › Active: `{active['Low']}`"
                    ),
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"📊 *Total Active: {total}*\n" f"📅 Yesterday: {resolved_text}"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📋 <{JIRA_BOARD_URL}|View Jira Board (PS)>",
                },
            },
        ]
    }


def send_to_slack(message):
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"channel": SLACK_CHANNEL, **message},
    )
    result = resp.json()
    if not result.get("ok"):
        raise RuntimeError(f"Slack error: {result.get('error')}")
    print("✅ Message sent successfully!")


if __name__ == "__main__":
    print("Fetching Jira data...")
    active = get_active_incidents()
    print(f"Active incidents: {active}")

    resolved = get_resolved_yesterday()
    print(f"Resolved yesterday: {resolved}")

    msg = build_slack_message(active, resolved)
    send_to_slack(msg)
