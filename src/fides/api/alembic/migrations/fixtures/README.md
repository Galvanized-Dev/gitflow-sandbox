# Migration scenario fixtures

The sandbox ships a real, migratable alembic tree so the parts of a release that touch
migrations can be tested here instead of only in production. `versions/` holds the
**released spine**; this directory holds the **scenario pieces**, staged into
`versions/` per test so each run starts from a known shape.

Everything below drives the Talos `verify-release` scripts unmodified — they assume the
fidesplus layout (`src/fides/api/alembic`, `migrations/versions`,
`migrations/release_manifest.yml`), which this repo mirrors.

## The chain

```
a00000000001  create widget            ── released spine (in versions/, in every tag)
a00000000002  add widget.color         ── the "2.0" head in release_manifest.yml
      │
b00000000001  create schema shadow     ── UNRELEASED dev chain (fixture)
b00000000002  create shadow.audit      ──   depends on the schema above
      │
c00000000001  add widget.size          ── the patch fix (fixture); parent is unreleased
      │
d00000000001  create shadow.report     ── child of the fix; NEEDS schema shadow
```

`shadow.report` needing a schema built by the *buried* chain is the whole point: it
makes ordering observable. Parentage alone looks fine while the upgrade still fails.

## Scenario 1 — patch downrev preflight (`missing_ancestor`)

Cut a patch from a tag containing only the spine, with `c00000000001` as the fix.

```bash
RS=<verify-release skill dir>
cp fixtures/c00000000001_add_widget_size.py versions/
git commit -am "fix: add widget.size"            # the dev-side fix
bash "$RS/check-migration-downrev.sh" --release <spine-tag> --fix <sha> --repo "$PWD"
```

Expect `issue: missing_ancestor`, `down_revision: b00000000002`,
`suggested_down_revision: a00000000002`, exit 1. Repointing to the suggestion and
re-running should give `ok`.

## Scenario 2 — the false alarm

Stage **both** `b00000000002` and `c00000000001` into the patch. The preflight still
reports `missing_ancestor` for `c00000000001` (it checks each fix against the tag in
isolation), but the parent now rides the same patch, so the correct action is to leave
it alone. Verifies the skill's judgment, not the script's.

## Scenario 2b — static checks pass, the upgrade still fails

Verified, not hypothetical. Take scenario 2's correct resolution: repoint
`b00000000002` to `a00000000002`, leave `c00000000001` pointing at `b00000000002`.
`alembic heads` reports a single head and the downrev preflight reports `ok` — and the
upgrade dies:

```
Running upgrade a00000000002 -> b00000000002, Create shadow.audit
psycopg2.errors.InvalidSchemaName: schema "shadow" does not exist
```

`b00000000002` creates a table *in* the `shadow` schema, and the `CREATE SCHEMA` lives
in `b00000000001`, which was excluded from the patch. Head-counting is a graph check; it
cannot see a dependency on something an excluded migration built.

The lesson for the skills: a repoint is not proven by `alembic heads`. Finish on real
Postgres via the PROD phase, which stamps a DB at the base tag's head — the shape prod
is in — and upgrades through the patch tree:

```bash
ALEMBIC_BIN=<alembic> bash "$RS/verify-migration-reconcile.sh" --repo "$PWD" \
  --release-ref HEAD --main-ref <spine-tag> --pg-container <pg>
```

## Scenario 3 — sprint reconcile, scenario 7 (silently skipped chain)

The patch shipped `c00000000001` repointed to `a00000000002`; `dev` still has it
parented at `b00000000002`. Now ship the buried chain:

```bash
cp fixtures/b0000000000{1,2}_*.py versions/
git merge origin/main --no-edit                  # brings main's repointed c00000000001
python "$RS/reconcile_sprint_migration.py" --main-ref origin/main --dev-ref origin/dev --apply
```

Taking dev's side instead makes the chain an *ancestor* of an already-applied revision,
so prod skips it — tables silently missing. The reconcile must keep MAIN's side and join
the chain as siblings.

## Scenario 4 — sprint reconcile, scenario 8 (ordering crash)

As scenario 3, plus `d00000000001` staged. Join the chain at the sprint tip rather than
before `c00000000001`'s children and the upgrade dies with
`schema "shadow" does not exist`. Prove the fix on real Postgres:

```bash
ALEMBIC_BIN=<a real alembic> bash "$RS/verify-migration-reconcile.sh" --repo "$PWD" \
  --release-ref HEAD --main-ref origin/main --dev-ref origin/dev --pg-container <pg>
```

Expect **PASS** on all of single-head / prod / fresh / dev-edge. This is the only check
that catches scenario 8; `check_migration_downrev.py`-style static guards cannot.

## Requirements

- A Postgres to point at (`--pg-container <name>` shells in via `docker exec`, otherwise
  a host `psql`). The script creates and drops its own scratch DBs (`prod_verify`,
  `fresh_verify`, `dev_verify`) and never touches an app database.
- `alembic` + `psycopg2` on the `ALEMBIC_BIN` you pass. Any venv with those works; the
  sandbox deliberately has no application code to install.
