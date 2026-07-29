# Gitflow sandbox

Test bed for the fidesplus release process and the Talos release skills that drive it,
with zero prod risk. The heavy fidesplus publish/RC builds are stubbed (echo only);
fidesinfra dispatch is omitted.

## What this mirrors

**fidesplus has no Start/Finish release workflows and no auto-RC.** That automation
(fidesplus#4048) was abandoned. A release is driven by hand — by a human, or by the
Talos `start-*`/`finish-*` release skills — and the only automation involved is the
back-merge bot. This repo used to model the abandoned design, which made it a test bed
for a process that does not exist; those five workflows have been removed.

What is left mirrors fidesplus one-for-one:

| Sandbox | fidesplus | Purpose |
|---|---|---|
| `backmerge-main-to-dev.yml` | same file, byte-identical | the only release automation: three-phase back-merge |
| `docker-rc.yml` | `docker_fidesplus_release_candidate.yml` | fires on a pushed `X.Y.ZrcN` tag |
| `docker-prod.yml` | `release.yml` | fires on a published GitHub Release |
| `enforce_branch_policy.yml` | same | PRs into `main` must come from `release/*` or `hotfix/*` |
| `check_changelog.yml` | `check_changelog.yml` | fragment required, `backmerge/*` exempt |

Merge semantics match too, which is the point of most of these tests: `main` queue =
**MERGE**, `dev` queue = **SQUASH**, `release/**` PR-required.

**Keep `backmerge-main-to-dev.yml` byte-identical to the fidesplus copy** (below its
header note). If the fidesplus one changes, re-copy it rather than hand-editing — the
whole value here is that the commands the skills run are the commands fidesplus runs.

## What this cannot test

No alembic tree and no `release_manifest.yml`, so the migration `down_revision`
preflight, the repoint, and the Postgres reconcile — the highest-risk logic in a patch
release — are **not** covered here. Those need fixture-repo unit tests or a migrations
tree added to this repo.

## One-time setup

1. Create a **test GitHub App** (Settings > Developer settings > GitHub Apps):
   permissions Contents: write, Pull requests: write, Checks: read.
   Install it on `Galvanized-Dev/gitflow-sandbox`. Note the **App ID**, generate a
   **private key**.
2. Repo secrets: `MERGE_BOT_APP_ID`, `MERGE_BOT_PRIVATE_KEY`.
3. Repo Settings > General: enable **Allow squash merging** + **Allow merge commits**
   + **Allow auto-merge**. (Public repo => merge queue is free.)
4. Apply rulesets: `APP_ID=<app id> .github/rulesets/apply.sh` — this also puts the App
   in the `dev-queue` bypass list, which is what lets the back-merge land by push.
5. For the approval-gate happy path: add a **second collaborator** (alt account)
   so a non-author can approve PRs. Solo, you can only test the reject path (and the
   bot warns when the approver and the dispatcher are the same person).

## Test scenarios

Each of these is a step in a Talos release skill, so run them the way the skill says —
`/ethyca-talos:start-sprint-release`, `finish-sprint-release`, `start-patch-release`,
`finish-patch-release` — pointing at this repo with `--repo Galvanized-Dev/gitflow-sandbox`.

- **Sprint, start**: cut `release/2.1.0` off `dev`, push it, open the release→main PR
  from the template, then push the `2.1.0rc0` tag **by hand** and confirm `docker-rc`
  fires. Nothing cuts that tag for you — that is the behaviour being verified.
- **Sprint, stabilize**: open a PR into `release/2.1.0`, merge it via the queue, then
  push `2.1.0rc1` by hand. Confirm no rc appears on push alone.
- **Sprint, finish**: compile the CHANGELOG into `## [2.1.0]` via a PR into the release
  branch; approve the release→main PR and let CI go green; `gh pr merge --merge` and
  confirm the queue lands **two parents** on `main`; publish the GitHub Release and
  confirm `docker-prod` fires.
- **Back-merge, three phases**: dispatch the bot (prepare) → confirm a **draft** PR into
  `dev` and that `dev` has not moved → approve it → dispatch with
  `-f source=backmerge/<v>-to-dev -f land=true` → confirm `dev` fast-forwarded, tip has
  `parents=2`, and the PR was closed with the landed SHA.
- **Back-merge, approval gate**: dispatch `land=true` with no approval → refuses.
  Approve, push another commit to the branch, `land=true` again → refuses as **stale**
  (approval was for an earlier tip). Re-approve → lands.
- **Back-merge, conflict**: push a conflicting change to `dev` before preparing →
  prepare fails, nothing pushed, `dev` untouched, and the run prints the resolution
  recipe. Resolve on the `backmerge/*` branch, push, approve, land.
- **Back-merge, idempotency**: dispatch prepare when `main` is already an ancestor of
  `dev` → "nothing to back-merge". Dispatch `land=true` on an already-landed branch →
  "nothing to land", and it tidies up the PR.
- **Patch**: cut `hotfix/2.0.1` off the `2.0.0` tag, cherry-pick a `dev` fix with `-x`,
  open the hotfix→main PR, push `2.0.1rc0` by hand, then finish as above. Confirm
  `main` gets a **merge commit**, not a squash.
- **Branch policy**: open a PR into `main` from `feat/whatever` → `Enforce Branch
  Policy` fails it.
