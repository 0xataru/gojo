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
JIRA_BOARD_URL = (
    f"{JIRA_URL}/jira/software/projects/{JIRA_PROJECT}/boards/{JIRA_BOARD_ID}"
)

SLACK_TOKEN = os.environ["SLACK_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {"Accept": "application/json"}

# Jira priority IDs are stable; display names get renamed (e.g. "High (P1)")
PRIORITIES = (
    ("P0", "🔴", 1),
    ("P1", "🟠", 2),
    ("P2", "🟡", 3),
)


def get_active_incidents():
    """Active incidents by priority (status not Done)"""
    counts = {name: 0 for name, _, _ in PRIORITIES}

    for name, _, priority_id in PRIORITIES:
        jql = (
            f"project = {JIRA_PROJECT} "
            f"AND issuetype = Task "
            f"AND priority = {priority_id} "
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
        counts[name] = len(resp.json().get("issues", []))

    return counts


def get_resolved_yesterday():
    """P0–P2 incidents resolved yesterday (by resolution date)"""
    priority_ids = ", ".join(str(pid) for _, _, pid in PRIORITIES)
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = date.today().strftime("%Y-%m-%d")
    jql = (
        f"project = {JIRA_PROJECT} "
        f"AND issuetype = Task "
        f"AND priority in ({priority_ids}) "
        f"AND statusCategory = Done "
        f'AND resolved >= "{yesterday}" '
        f'AND resolved < "{today}"'
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
    today = date.today().strftime("%A, %B %d, %Y")

    lines = [f"🚨 *PS Incident Status — {today}*", ""]
    lines += [
        f"{emoji} *{name}* — Active: {active[name]}" for name, emoji, _ in PRIORITIES
    ]
    lines += [
        "",
        f"📊 *Total Active: {total}*",
        f"📅 Yesterday: {resolved_yesterday} resolved",
        f"📋 <{JIRA_BOARD_URL}|View Jira Board (PS)>",
    ]
    return {"text": "\n".join(lines)}


def send_to_slack(message):
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"channel": SLACK_CHANNEL, "username": "Gojo", **message},
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
