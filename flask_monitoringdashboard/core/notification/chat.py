import requests
from flask_monitoringdashboard.core.notification.notification_content import NotificationContent


def send_message(notification_content: NotificationContent):
    from flask_monitoringdashboard import config

    webhook_url = config.chat_webhook_url
    match config.chat_platform:
        case 'SLACK':
            payload = create_slack_payload(notification_content)
            requests.post(webhook_url, json=payload)
        case 'ROCKET_CHAT':
            payload = create_rocket_chat_payload(notification_content)
            requests.post(webhook_url, json=payload)
        case 'TEAMS':
            payload = create_teams_payload(notification_content)
            requests.post(webhook_url, json=payload)
        case _:
            print('Invalid chat platform.')


def create_slack_payload(notification_content: NotificationContent):
    return {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": notification_content.body_markdown}
            }
        ]
    }

def create_rocket_chat_payload(notification_content: NotificationContent):
    return {
        "text": notification_content.body_markdown,
    }

def create_teams_payload(notification_content: NotificationContent):
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
                                    "value": f"{notification_content.exception_type}"
                                },
                                {
                                    "title": "Timestamp:",
                                    "value": f"{notification_content.created_at}"
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
                                    "text": f"{notification_content.stack_trace}",
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
