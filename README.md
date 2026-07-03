<p align="center">
  <img src="gojo.png" alt="Gojo" width="180" />
</p>

<h1 align="center">Gojo</h1>

<p align="center">
  <strong>Slack incident bot</strong> — daily Jira summary to your channel
</p>

<p align="center">
  <a href="https://github.com/0xataru/incident-bot/actions/workflows/daily-report.yml">
    <img src="https://github.com/0xataru/incident-bot/actions/workflows/daily-report.yml/badge.svg" alt="Daily Incident Report" />
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white" alt="Python 3.11" />
  </a>
  <a href="https://slack.com/">
    <img src="https://img.shields.io/badge/Slack-integration-4A154B?logo=slack&logoColor=white" alt="Slack" />
  </a>
  <a href="https://www.atlassian.com/software/jira">
    <img src="https://img.shields.io/badge/Jira-integration-0052CC?logo=jira&logoColor=white" alt="Jira" />
  </a>
  <img src="https://img.shields.io/badge/schedule-weekdays%2007%3A00%20UTC-555" alt="Schedule" />
</p>

---

A GitHub Actions bot that sends a daily Jira incident summary to Slack every weekday at 07:00 UTC.

## What it reports

- Active incidents by priority (Highest / High / Medium / Low / Lowest)
- Total active count
- Number of incidents resolved yesterday
- Link to the Jira board

## Setup

### 1. Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret           | Description                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| `JIRA_URL`       | Your Atlassian domain, e.g. `https://your-domain.atlassian.net`                                |
| `JIRA_EMAIL`     | Email used to log in to Jira                                                                   |
| `JIRA_API_TOKEN` | API token from [id.atlassian.com](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_PROJECT`   | Jira project key, e.g. `PS`                                                                    |
| `SLACK_TOKEN`    | Slack Bot OAuth Token (`xoxb-...`)                                                             |
| `SLACK_CHANNEL`  | Slack channel ID, e.g. `C01234567`                                                             |

### 2. Run manually (optional)

Go to **Actions → Daily Incident Report → Run workflow** to test before the scheduled run.

## Schedule

Runs automatically Monday–Friday at 07:00 UTC via `cron-job.org`.
