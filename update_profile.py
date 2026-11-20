import html
import json
import os
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


OWNER = "b1swa25"
README_PATH = Path(__file__).with_name("README.md")
START_MARKER = "<!-- REPOSITORIES:START -->"
END_MARKER = "<!-- REPOSITORIES:END -->"
API_URL = "https://api.github.com/users/{}/repos".format(OWNER)


def fetch_repositories(token):
    repositories = []
    page = 1

    while True:
        query = urlencode({
            "type": "owner",
            "sort": "updated",
            "direction": "desc",
            "per_page": 100,
            "page": page,
        })
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "b1swa25-profile-updater",
        }
        if token:
            headers["Authorization"] = "Bearer {}".format(token)
        request = Request("{}?{}".format(API_URL, query), headers=headers)
        with urlopen(request, timeout=30) as response:
            page_repositories = json.load(response)

        if not isinstance(page_repositories, list):
            raise RuntimeError("GitHub repository API returned an unexpected response.")

        repositories.extend(
            repository
            for repository in page_repositories
            if not repository.get("private", False)
        )
        if len(page_repositories) < 100:
            return repositories
        page += 1


def table_cell(value):
    value = " ".join(str(value or "").split())
    value = html.escape(value, quote=False)
    for character in r"\`*_{}[]()#+-.!|":
        value = value.replace(character, "\\" + character)
    return value


def render_repositories(repositories):
    rows = [
        "| Repository | Description | Language | Stars | Updated |",
        "|---|---|---|---:|---|",
    ]

    for repository in repositories:
        name = table_cell(repository.get("name", ""))
        url = "https://github.com/{}/{}".format(
            OWNER, quote(repository.get("name", ""), safe="")
        )
        description = table_cell(repository.get("description") or "—")
        language = table_cell(repository.get("language") or "—")
        stars = repository.get("stargazers_count", 0)
        updated = str(repository.get("updated_at", ""))[:10] or "—"
        rows.append(
            "| [{}]({}) | {} | {} | {} | {} |".format(
                name, url, description, language, stars, updated
            )
        )

    if not repositories:
        rows.append("| No public repositories found | — | — | 0 | — |")

    return (
        "<details>\n"
        "<summary>Browse all {} public repositories</summary>\n\n"
        "{}\n\n"
        "</details>"
    ).format(len(repositories), "\n".join(rows))


def update_readme(repositories, path=README_PATH):
    content = path.read_text(encoding="utf-8")
    if content.count(START_MARKER) != 1 or content.count(END_MARKER) != 1:
        raise ValueError("README must contain exactly one repository-list marker pair.")

    before, remaining = content.split(START_MARKER, 1)
    _, after = remaining.split(END_MARKER, 1)
    updated = "{}{}\n{}{}".format(
        before, START_MARKER, render_repositories(repositories) + "\n", END_MARKER + after
    )
    if updated != content:
        path.write_text(updated, encoding="utf-8")


def main():
    token = os.environ.get("GITHUB_TOKEN")
    update_readme(fetch_repositories(token))


if __name__ == "__main__":
    main()
