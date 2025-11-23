import requests

from flask_monitoringdashboard.core.alert.alert_content import AlertContent


def send_message(alert_content: AlertContent):
    from flask_monitoringdashboard import config

    payload_creators = {
        "SLACK": create_slack_payload,
        "ROCKET_CHAT": create_rocket_chat_payload,
        "TEAMS": create_teams_payload,
    }

    creator = payload_creators.get(config.chat_platform)
    if not creator:
        print("Invalid chat platform.")
        return

    payload = creator(alert_content)

    try:
        resp = requests.post(config.chat_webhook_url, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print("Alert delivery failed:", e)



def create_slack_payload(alert_content: AlertContent):
    return {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": alert_content.body_markdown}
            }
        ]
    }


def create_rocket_chat_payload(alert_content: AlertContent):
    return {
        "text": alert_content.body_markdown,
    }


def create_teams_payload(alert_content: AlertContent):
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "Exception Alert",
                            "weight": "Bolder",
                            "size": "Large",
                            "color": "Attention"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "title": "Type:",
                                    "value": f"{alert_content.exception_type}"
                                },
                                {
                                    "title": "Timestamp:",
                                    "value": f"{alert_content.created_at_str}"
                                }
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": "Stack Trace (click to expand):",
                            "weight": "Bolder",
                            "wrap": True
                        },
                        {
                            "type": "Container",
                            "id": "stackContainer",
                            "isVisible": False,
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"{alert_content.stack_trace}",
                                    "wrap": True,
                                    "fontType": "Monospace"
                                }
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.ToggleVisibility",
                            "title": "Show/Hide Stack Trace",
                            "targetElements": ["stackContainer"]
                        }
                    ]
                }
            }
        ]
    }
