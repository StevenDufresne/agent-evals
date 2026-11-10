---
name: solution-fit
description: Use when checking whether a branch or pull request actually solves the problem described in its Linear issue — before opening a PR, while reviewing one, or when asked "does this fix the issue?". Invoke with a Linear issue ID, a PR number, or nothing to use the current branch.
---

# Solution fit

Judge whether a code change solves the problem its Linear issue describes. The skill reads the issue first, writes down the problem independently of the code, then hands the problem and the diff to a fresh evaluator that has not seen how or why the change was written.

The skill only reads. It never edits code, comments on Linear, or comments on the PR.

## Inputs

| Input | Where it comes from |
|---|---|
| Change | A PR number (`gh pr diff <n>`), a branch name (`git diff trunk...<branch>`), or the current branch against its base when nothing is given. Use `trunk` or `main`, whichever the repo has. |
| Linear issue | The argument if it looks like `ABC-123`. Otherwise search, in order: the PR body, the branch name, the commit messages on the branch. If none match or several do, ask the user. |

## Step 1: Check Linear access

Fetch the issue with whichever is available, in this order:

1. The Linear MCP server (`get_issue`, then `list_comments` for the discussion, since `get_issue` does not include it).
2. Any other connected tool that can read Linear issues.
3. None: tell the user the skill can't reach Linear and ask them to paste the issue title, description and key comments. Don't continue without the issue.

## Step 2: Gather the problem

Collect:

- Title, description, and every comment.
- Parent issue and linked or related issues, one level deep, for context only.
- Screenshots or recordings in the description or comments. View them if the tools allow it; they often show the real problem better than the text does.

## Step 3: Write the problem brief

Before you look at the diff, write the brief using this template. Base it only on the issue. Wording such as "fix the button" is a proposed solution, not the problem; describe what the user experiences instead.

```
Issue: <ID> — <title>

Who is affected:
What they experience today:
What they should experience instead:
Acceptance criteria:
  1. <explicit criterion from the issue>
  2. <implied criterion — mark as (implied)>
Out of scope (per the issue):
Open questions the issue leaves unanswered:
```

If the issue is too vague to fill in "What they experience today", say so in the report and stop. You can't evaluate a fix against a problem nobody wrote down.

## Step 4: Evaluate in a fresh subagent

Start a new general-purpose subagent. Don't fork the current conversation: the evaluator must not see the author's reasoning, plan, or chat history.

Give it exactly:

- The problem brief from Step 3.
- The command that produces the diff (for example `gh pr diff 1234`, or `git diff trunk...HEAD` run from `<repo path>`).
- The full text of [rubric.md](rubric.md).
- These instructions: "Read the repo as needed to understand the change. Don't edit files, commit, or post anywhere. Return the report in the format in the rubric."

Don't pass on the PR description, commit messages, or your own opinion of the change.

## Step 5: Report

Relay the evaluator's report to the user unchanged, then add one line only if needed: anything from Step 2 the brief left out that could change the verdict.

Then stop. Fixing the gaps is up to the user.
