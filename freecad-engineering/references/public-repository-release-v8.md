# Public and Private Repository Release V8

## Contents

1. Authorization contract
2. Sanitization gate
3. Git release
4. Remote verification

## 1. Authorization contract

Record repository owner, name, requested visibility, upload scope, excluded content, and whether a license grant is authorized. Treat these as separate decisions:

- publishing a repository publicly;
- releasing user task artifacts;
- granting an open-source license.

Never infer the last two from the first.

## 2. Sanitization gate

Run `audit_public_release_v8.py` on the exact repository root. Block the release when it finds:

- high-confidence access tokens, secret keys, or private-key blocks;
- absolute user or machine paths;
- CAD, drawing, task-render, or source-evidence files outside an explicitly reviewed allowlist;
- caches, temporary files, logs, local databases, or editor state;
- a nested Skill `README.md` that violates the compact Skill-package structure.

Review all staged files manually after the automated scan. Automated scanning reduces risk but cannot prove ownership or publication rights.

## 3. Git release

1. Initialize the repository with a `main` branch.
2. Keep the reusable Skill in a folder whose name matches its frontmatter name.
3. Put installation and public-facing documentation at repository root, outside the Skill folder.
4. Configure a non-sensitive commit identity.
5. Inspect `git status --short` and `git diff --cached --stat`.
6. Commit only reviewed files.
7. Create or attach the intended remote and push.

Do not add a license unless the authorization contract permits it.

## 4. Remote verification

Query the remote through GitHub after pushing. Acceptance requires:

- the returned owner/name equals the intended repository;
- visibility equals the requested `PUBLIC` or `PRIVATE` state;
- the default branch is `main`;
- the remote head equals the reviewed local commit;
- the repository page is reachable.

Record the remote URL and commit hash in the release report.
