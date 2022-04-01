import os
import requests
from greynoise import GreyNoise

# get os env vars
GREYNOISE_API_KEY = os.environ.get('GREYNOISE_API_KEY')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

if not GREYNOISE_API_KEY or not SLACK_WEBHOOK_URL:
    exit(1)

session = GreyNoise(api_key=GREYNOISE_API_KEY, integration_name='greynoise-trends-bot')

metadata = session.metadata()

tags_list = metadata["metadata"]

tags_with_cves = []

for item in tags_list:
    if item["cves"]:
        tags_with_cves.append({"tag_name": item["name"], "tag_slug": item["slug"]})

list_of_tags_plus_data = []

for tag in tags_with_cves:
    stats = session.stats(f"tags:{tag['tag_name']} last_seen:7d")
    if stats["count"] > 0:
        tag_data = {"tag_name": tag['tag_name'], "count_of_ips": stats["count"], "tag_slug": tag["tag_slug"]}
        list_of_tags_plus_data.append(tag_data)

sorted_list = sorted(list_of_tags_plus_data, key=lambda i: i['count_of_ips'], reverse=True)

blocks = [{
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "List of top 10 CVEs being scanned for in the last 7 Days"
    }
},
    {
        "type": "divider"
    }]
for item in sorted_list[:10]:
    slack_object = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Tag Name:* {item['tag_name']}\nIP Count: {item['count_of_ips']}"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Tag Details"
            },
            "url": f"https://www.greynoise.io/viz/tag/{item['tag_slug']}"
        }
    }
    blocks.append(slack_object)

slack_json = {"blocks": blocks}

requests.post(SLACK_WEBHOOK_URL, json=slack_json)
