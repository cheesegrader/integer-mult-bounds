# Reproducing the source-invocation work

Task A has its own independent replay in `../lean-multi-host-framework`.
This directory concerns Task B. A successful build certifies the statements
actually present in the Lean files; consult `README.md` for the precise scope
of the source connection and any remaining obligations.

## Versions

- Lean 4.33.0, commit `d8b18978322de05a8f3dba51ef03cf5461676c17`.
- Mathlib tag v4.33.0, commit `db584cd6d46c92f209a44c0f1c829460d327499d`.
- Mathlib dependencies: exact commits in `mathlib-lake-manifest.json`.
- Repository sources and compressed input snapshots: `source-versions.json`.

The original generated source bytes are included under `inputs/`. Their raw
and compressed SHA-256 hashes are checked. These files are deterministic
replay artifacts from pinned PR442 and its inherited supplier, not new source
algorithms or a revised claimed bound.

To regenerate the upstream snapshots separately from the supplied inputs,
make a second public checkout and explicitly fetch the pinned PR head:

```sh
git clone --no-checkout https://github.com/CrocSwap/integer-mult-bounds.git /tmp/pr442-source-review
git -C /tmp/pr442-source-review fetch origin 4e16d001d505d4f21dd2bcfc44591f9be4c279bd
git -C /tmp/pr442-source-review checkout --detach 4e16d001d505d4f21dd2bcfc44591f9be4c279bd
```

Follow that checkout's own producer requirements and run
`python3 -B research/idle-axis-hosting/verify.py OUTPUT` in that checkout.
This larger upstream replay is optional for the packaged Lean reproduction;
the six required snapshots are already included. Each original path beneath `OUTPUT` is recorded in
`source-versions.json`. Compare the uncompressed hashes before regenerating
this package's Lean literals. The earlier
`../lean-source-invocation-audit/SOURCE-INSPECTION.md` documents the inherited
record format and the exact call selection.

## Library preparation

Install the official Lean toolchain and put its `bin` directory first in PATH.
Clone Mathlib and check out the exact commit above. From that checkout, build:

```sh
lake build Mathlib.Data.Matrix.Mul \
  Mathlib.Algebra.BigOperators.Fin \
  Mathlib.Tactic.FieldSimp Mathlib.Tactic.Ring Mathlib.Tactic.NormNum
```

Mathlib's official `lake exe cache get` can supply the same library artifacts
when available. In this session the configured proxy refused the official
Azure cache endpoint, so the required library modules were built from source.
For writable cache storage use `MATHLIB_CACHE_DIR`; changing HOME is unnecessary.

## Source binding and proof replay

The source-binding checker uses Python 3 and SymPy (tested with Python 3.12 and
SymPy 1.14). SymPy constructs integer witnesses. Their mathematical validity
is checked by Lean, independently of the witness computation.

```sh
python3 research/lean-multi-host-source/check_sources.py \
  --receipt /tmp/source-binding.json

python3 research/lean-multi-host-source/replay.py \
  --lean /path/to/lean-4.33.0-linux/bin/lean \
  --mathlib /path/to/mathlib4 \
  --build-dir /tmp/multi-host-source-fresh \
  --receipt /tmp/multi-host-source-replay.json
```

The build directory must not already exist. Every local module is copied
from the manifested source and compiled afresh with `lean -t 0`. The replay
records compiler output, source hashes, elapsed times, and transitive axiom
closures. Only Lean/Mathlib's standard `propext`, `Quot.sound`, and
`Classical.choice` are accepted; project axioms, `sorry`, `admit`, and
`native_decide` are forbidden. The finite computations use kernel reduction.

Large matrix certificates can take tens of minutes. If a retained build is
interrupted, the same command with `--resume` reuses only this script's
successful builds whose source, dependency, and compiled-artifact hashes
still match. Current builds also bind the installed toolchain, clean pinned
Mathlib/dependency sources, library artifacts, companion local artifacts,
and library search order. Changed modules and their dependents are rebuilt. The final
axiom audit is always rerun. The default per-module timeout is two hours;
`--module-timeout` adjusts it without changing a theorem or its proof.

The first completed build predates the external-environment fingerprint.
Default resume rejects that legacy cache. For the packaging validation only,
an explicit `--allow-legacy-resume --legacy-receipt PATH --legacy-commit COMMIT`
was used together with `--resume`, anchoring each retained local source,
dependency and `.olean` hash to the successful receipt committed at
`f86e52f19569e801ac8d133d7070aa3fe39db08c`. The current external environment
was checked and fingerprinted, but its historical bytes cannot be recovered
from that old receipt. The new receipt labels this limitation and reports
fresh, reused and legacy-reused module counts separately. This is not a
fresh 52-module recompilation or a `leanchecker --fresh` run. The legacy
option requires that historical Git receipt; fresh reproduction does not.

The portable delivery and one-command fresh reproduction of both tasks are
documented in [`../lean-external-review/README.md`](../lean-external-review/README.md).
Its validation notes and `EXTERNAL-BUILD-REVIEW.md` describe the exact checks
used for this delivery, while the original `replay-result.json` remains unchanged.

The JSON parser and extraction scripts are a reproducible provenance boundary,
not a formally verified JSON parser. `check_sources.py` independently compares
the chronological normalized event list with the pinned template, verifies all
input hashes, and re-renders the generated certificates. The Lean statements
apply to the embedded literal data. Changing a generator cannot make a false
matrix identity pass the Lean kernel.

After intentional changes to local Lean sources, run `update_manifest.py` in
this directory and review its changed inventory before replaying. Reproduction
of the committed sources does not require regenerating the manifest.
