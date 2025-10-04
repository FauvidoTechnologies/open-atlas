import json
import re

import pandas as pd
from bs4 import BeautifulSoup

# Load your saved HTML
with open(
    "/home/purge/Desktop/Atlas/atlas/tools/reverse_instagram_lookup/utils/output.html",
    "r",
    encoding="utf-8",
) as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Find the script with JSON data
script = soup.find("script", text=re.compile("window._sharedData"))
if not script:
    script = soup.find("script", text=re.compile("__additionalData"))

if not script:
    raise ValueError("Could not find Instagram data script in HTML.")

# Extract JSON from script
json_text = re.search(r"{.*}", script.string, re.DOTALL).group()
data = json.loads(json_text)

# Navigate into posts data (structure may vary!)
user = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
edges = user["edge_owner_to_timeline_media"]["edges"]

# Collect first 12 posts
posts = []
for edge in edges[:12]:
    node = edge["node"]
    posts.append(
        {
            "post_url": f"https://instagram.com/p/{node['shortcode']}/",
            "thumbnail": node["display_url"],
            "likes": node["edge_liked_by"]["count"],
            "comments": node["edge_media_to_comment"]["count"],
            "caption": node["edge_media_to_caption"]["edges"][0]["node"]["text"]
            if node["edge_media_to_caption"]["edges"]
            else "",
        }
    )

df = pd.DataFrame(posts)
print(df)
