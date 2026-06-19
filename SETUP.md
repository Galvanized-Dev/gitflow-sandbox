# Gitflow sandbox

Tests the 5 gitflow workflows with zero prod risk. The heavy fidesplus
publish/RC builds are stubbed (echo only); fidesinfra dispatch is omitted.

## One-time setup
1. Create a **test GitHub App** (Settings > Developer settings > GitHub Apps):
   permissions Contents: write, Pull requests: write, Checks: read.
   Install it on `galvana/gitflow-sandbox`. Note the **App ID**, generate a
   **private key**.
2. Repo secrets: `MERGE_BOT_APP_ID`, `MERGE_BOT_PRIVATE_KEY`.
3. Repo Settings > General: enable **Allow squash merging** + **Allow merge commits**
   + **Allow auto-merge**. (Public repo => merge queue is free.)
4. Apply rulesets: `APP_ID=<app id> .github/rulesets/apply.sh`
5. For the approval-gate happy path: add a **second collaborator** (alt account)
   so a non-author can approve PRs. Solo, you can only test the reject path.

## Test scenarios
- **Sprint happy path**: run Start Sprint Release -> see release/2.1.0, the
  release->main PR, and rc0 tag (+ stub RC build). Open a PR into release/2.1.0,
  merge via queue (squash). Approve the release->main PR + let CI go green.
  Run Finish Sprint Release -> main gets a MERGE COMMIT, GH Release 2.1.0 created
  (+ stub prod publish), back-merge PR into dev auto-merged (merge commit).
- **Hotfix happy path**: Start Hotfix Release -> hotfix/2.0.1 off main. Approve,
  green. Finish Hotfix Release -> main SQUASH, GH Release 2.0.1, back-merge into
  dev SQUASH.
- **Idempotency**: re-run a Finish -> every step reports "already ... skipping".
- **Back-merge conflict raises**: push a conflicting change to dev before Finish
  -> back-merge step fails, PR left open. Resolve, re-run Finish -> resumes.
- **Gate reject (solo-testable)**: run Finish on an unapproved/red PR -> raises.
