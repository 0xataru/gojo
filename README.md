# Incident Bot

A GitHub Actions bot that sends a daily Jira incident summary to Slack every weekday at 9:00 AM Kyiv time.

## What it reports

- Active incidents by priority (High / Medium / Low)
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

Go to **Actions → Daily PRofiCRM Incident Report → Run workflow** to test before the scheduled run.

## Schedule

Runs automatically Monday–Friday at 07:00 UTC (10:00 Kyiv, EEST).

