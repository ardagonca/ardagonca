"""Rewrites the 'recently shipped' block in README.md with the latest pushed public repos."""
import datetime, json, os, re, urllib.request

USER = os.environ.get("GH_USER", "ardagonca")
SKIP = {USER.lower()}  # the profile repo itself

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30&type=owner",
    headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"},
)
repos = json.load(urllib.request.urlopen(req))

def ago(ts):
    d = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))).days
    return "today" if d == 0 else "yesterday" if d == 1 else f"{d} days ago" if d < 30 else f"{d // 30} mo ago"

rows = []
for r in repos:
    if r["fork"] or r["private"] or r["name"].lower() in SKIP:
        continue
    desc = (r["description"] or "").replace("|", "/").strip()
    lang = r["language"] or ""
    rows.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} | {ago(r['pushed_at'])} |")
    if len(rows) == 5:
        break

block = "| Repository | What it is | Language | Last push |\n|---|---|---|---|\n" + "\n".join(rows)
readme = open("README.md", encoding="utf-8").read()
new = re.sub(r"(<!-- activity:start -->\n).*?(\n<!-- activity:end -->)", lambda m: m.group(1) + block + m.group(2), readme, flags=re.S)
open("README.md", "w", encoding="utf-8").write(new)
print(block)
