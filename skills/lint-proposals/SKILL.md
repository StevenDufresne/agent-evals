---
name: lint-proposals
description: Use when asked to find team conventions that should become ESLint rules, to run the weekly lint-proposals review, or to update the lint-proposals tracking issue. Mines merged PRs and review comments for repeated corrections and keeps one rolling GitHub issue of proposals.
---

# Lint proposals

Find conventions the team keeps correcting by hand and propose turning them into ESLint rules. All state lives in one rolling GitHub issue. The skill never opens rule PRs itself.

## Inputs

Read these from the user's request, falling back to the defaults:

| Input | Default |
|---|---|
| Source repo | `Automattic/wp-calypso`, local checkout `~/dev/wp-calypso` |
| Path | `client/dashboard` |
| People (authors and reviewers) | `people` in `~/.config/agent-evals/lint-proposals.json`, a list of `{ "name": "<git author name>", "login": "<github login>" }`. If the file is missing, use everyone. |
| Window | Since the issue's `Last run` date, or the last 12 months on a first run |
| Tracking issue | The open issue labelled `lint-proposals` in `StevenDufresne/agent-evals` |
| Mode | `dry-run`: write the draft to a local file. Post only when the user says `post`. |

## Steps

### 1. Load the current state

Read the tracking issue body and every comment with `gh issue view <n> --repo StevenDufresne/agent-evals --json body,comments`. Parse each `## LP-<n>:` section. Then apply decision comments in order:

- `agree LP-<n>` makes the status `agreed` once it has 2 or more distinct agreeing people.
- `reject LP-<n>: <reason>` makes the status `rejected`, and the reason is recorded.

For each proposal, look for PRs that mention `LP-<n>` and the issue: use `gh api repos/StevenDufresne/agent-evals/issues/<n>/timeline` for cross-references, and `gh search prs "LP-<n>" --repo Automattic/wp-calypso`. An open PR sets the status to `rule PR open`, a merged one to `enforced`.

### 2. Find candidate PRs

Use the local checkout. It's cheaper than the API.

```sh
git -C ~/dev/wp-calypso fetch --quiet origin trunk
git -C ~/dev/wp-calypso log origin/trunk --since=<window-start> --no-merges \
  --format='%h|%an|%s' -- client/dashboard
```

Take the PR number from each `(#NNNNN)` subject. Keep a PR if one of the people authored it, or if it has review activity from them (checked in step 3).

### 3. Collect corrections

For each candidate PR, fetch inline review comments and review bodies:

```sh
gh api --paginate repos/Automattic/wp-calypso/pulls/<pr>/comments \
  --jq '.[] | {user: .user.login, path, body, url: .html_url}'
gh api --paginate repos/Automattic/wp-calypso/pulls/<pr>/reviews \
  --jq '.[] | select(.body != "") | {user: .user.login, body, url: .html_url}'
```

Keep comments where a reviewer asks for a code change that would apply anywhere, not just in this PR: "use X instead of Y", "don't import Z here", "move this into the hook", "always/never ...". Drop questions, praise, bot comments and one-off logic bugs.

Also count convention sweeps: PRs by the people above that apply one convention across many files, such as renames, import migrations or replacing an API. A sweep that didn't add a lint rule is evidence by itself.

### 4. Group into conventions

Group the corrections by the underlying rule, not by wording. Write each rule as one sentence about what code must or must not do.

Propose a convention only if all of these hold:

- 3 or more independent occurrences (review comments, follow-up fixes, or a sweep counting as 1)
- from 2 or more different reviewers or authors
- not already in the issue, in any status, including `rejected`. A rejected proposal comes back only if its evidence has at least doubled since the rejection, and the note must say so.
- not already enforced. Check `client/dashboard/eslint.config.mjs`, `client/eslint.config.mjs` and the root `eslint.config.mjs` on `origin/trunk`.

### 5. Draft the rule and measure its cost

For each new proposal:

- Draft the rule using built-in options first: `no-restricted-imports`, `no-restricted-syntax` with an AST selector, `no-restricted-properties`. Propose a custom `wpcalypso/*` rule only when no built-in can express it.
- The error message must say what to do instead.
- Count current violations on trunk with `git -C ~/dev/wp-calypso grep -n <pattern> origin/trunk -- client/dashboard`. Label the count approximate.
- If the convention can't be checked statically (for example "keep components presentational"), mark it `not lintable`. Suggest it as a benchmark pattern task instead.

### 6. Update the issue

Update every existing section's status, and append the new sections. Keep IDs stable and never renumber. The next ID is the highest existing ID plus one.

Section format:

```markdown
## LP-<n>: <convention in a few words>
**Status:** proposed | agreed | rule PR open | enforced | rejected | not lintable · **First seen:** <YYYY-MM-DD> · **Evidence:** <count> from <count> people

- **Convention:** <one sentence>
- **Evidence:** <PR links and comment links, newest first, at most 8>
- **Violations on trunk:** ~<count> in <count> files (as of <date>)
- **Draft rule:**
  ```js
  <rule config>
  ```
- **Rule PR:** <link or —>
- **Decision:** <who agreed or rejected, and why>
```

Body header, above the sections:

```markdown
Rolling list of conventions in `client/dashboard` that might be worth enforcing with ESLint.
To decide, comment `agree LP-<n>` or `reject LP-<n>: <reason>`. A PR adding a rule should say `Implements LP-<n>, part of #<this issue>`.

**Last run:** <YYYY-MM-DD> · **Window:** <start> → <end> · **PRs scanned:** <count>
```

**Dry-run (default):** write the full new body to `lint-proposals-<date>.md` in the scratchpad. Show the user a summary: new proposals, status changes, and anything skipped with the reason.

**Post (only when the user says so):**

- `gh issue edit <n> --repo StevenDufresne/agent-evals --body-file <file>`.
- If any new proposals were added, also post one short comment: `New this week: LP-<a>, LP-<b>`. Quiet weeks get no comment.
- If no issue exists yet, show the user the body and title first. Create it with `gh issue create --label lint-proposals` only after they approve.

## Rules

- Never comment on, label or edit anything in `Automattic/wp-calypso`. Only read from it.
- Never open rule PRs. People do that after agreeing.
- Quote at most one line from any review comment, and link to it rather than copying more. The issue is public.
- Name people by their GitHub login only when they made the decision comment. Otherwise just link the evidence.
