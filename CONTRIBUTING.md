# Contributing

Suggest a resource through an issue or pull request. Include:

1. Its name and official URL.
2. One sentence explaining what it does and who it is for.
3. Its required account, data, device or payment permissions.
4. A public source for the description.
5. Any relationship you have with the project.

Keep descriptions factual. Do not copy marketing claims about guaranteed outcomes, security or comparative performance without evidence. A documentation review is different from an installation test or a security audit.

Edit `resources.json`, then run `python3 build.py` to regenerate the indexes. Each entry needs a unique ID and URL, a source URL, the source check date and access notes. Maintainers check the source before merging. Request corrections when a product changes or a link stops working.

Only submit public information. Do not paste group conversations, member names, personal contact details, access tokens or private client material. Report a sensitive disclosure privately to the maintainers rather than opening a public issue.

A GitHub star is not an entry. If you want a starred repo added, open an issue and point at the row in `stars-queue.json`.
