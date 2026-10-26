# Contributing

Submit a pull request. Issues are off on this repository, so there is no public issue form. Include:

1. Its name and official URL.
2. One sentence explaining what it does and who it is for.
3. The access it needs (account, data, device or payment permissions).
4. Its licence.
5. The date you checked the public source, and that source URL.
6. Any relationship you have with the project.

Keep descriptions factual. Do not copy marketing claims about guaranteed outcomes, security or comparative performance without evidence. A documentation review is different from an installation test or a security audit.

Edit `resources.json`, then run `python3 build.py` to regenerate the indexes. Each entry needs a unique ID and URL, a source URL, the source check date, access notes and licence. Maintainers check the source before merging.

Only submit public information. Do not paste group conversations, member names, personal contact details, access tokens or private client material.

A GitHub star is not an entry. To promote a row from `stars-queue.json`, send a pull request with the documentation review above.
