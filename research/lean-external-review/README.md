# External review: one literal R747 invocation

This delivery packages the completed Task A and Task B. No mathematical scope
is added in the packaging commit. The human contributor initiated and
coordinated the AI-assisted effort; they do not claim independent derivation or
personal checking of the mathematics. Codex agents developed the proofs, ran
checks, and prepared the reviews. A separate agent review is not a human audit.

## Start here

- [Task A](../lean-multi-host-framework/README.md): multi-host completion and
  exact single-host recovery, with abstract endpoint contracts as premises.
- [Task B](../lean-multi-host-source/README.md): those contracts instantiated by
  one literal PR442 forward invocation, including native coordinates and dirty inputs.
- [Statement/claim review](../lean-multi-host-source/EXTERNAL-CLAIM-REVIEW.md):
  precise theorem statements, hypotheses, external source binding, and limits.
- [Draft PR text](DRAFT-PR.md), [validation](VALIDATION.md), and
  [bounded overlap refresh](../lean-multi-host-source/EXTERNAL-OVERLAP-REVIEW.md).

The selected invocation is stage 2, replica 0, pair 0 at PR442 commit
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`. Its 19,002-event word has 987
arbitrary live Boolean payload streams and one explicitly initialized clean
private temporary. Theorems quantify over any address field with `2 ≠ 0`
and an invertible invocation chart. They retain every affected host/data
stream and the exterior of the union of active owners. Actual old-bank
outputs are threaded as auxiliary state.

This is a local stream-model theorem with explicit input embeddings and
immediate completion by remaining pending swaps. The source parser and
extraction are externally checked Python, not a proved compiler. There is
no proof here of the full cover sweep, later recursive scheduling, arbitrary
global allocation equivalence, physical costs, all-size compilation, analytic
transfer, or κ. PR448's split-helper gain remains unestablished.

## Delivery and patch order

Public repository: <https://github.com/CrocSwap/integer-mult-bounds>.
Exact base: `12a4934d15006e8c10f9b2264f13f8f341be802b`.

**There is one patch to apply: `review.patch`.** It is cumulative from that
public base, including earlier local dependencies. Do not first apply Task A,
Task B, or any historical archived patches. They are archival alternatives
with different bases, not steps in this delivery's application order.

```sh
git clone https://github.com/CrocSwap/integer-mult-bounds.git review-checkout
cd review-checkout
git checkout --detach 12a4934d15006e8c10f9b2264f13f8f341be802b
git apply --check /absolute/path/to/review.patch
git apply /absolute/path/to/review.patch
python3 research/lean-external-review/verify_package.py
```

Alternatively, unpack `integer-mult-lean-review.tar.gz` and enter its
`integer-mult-lean-review/` directory. It already contains the final source
snapshot: run `sha256sum -c SHA256SUMS`, then the same verification/build commands.
Do not apply the patch inside the extracted snapshot.

Both routes supply every local dependency, in particular:

```text
research/lean-whole-residual-hosting/CoordinateSwap.lean
research/lean-whole-residual-hosting/Hosting.lean
research/lean-whole-residual-hosting/PhysicalHosting.lean
research/lean-multi-host-framework/{MultiHosting,SingleHostRecovery,MultiHostControls}.lean
research/lean-multi-host-source/   # all 50 own modules, six source snapshots, generators
```

Task B's 52-module build includes `CoordinateSwap` and `MultiHosting` from
their sibling directories. Task A's six-module build includes all three
WholeHosting dependencies. No unpublished local commit needs to be fetched.
Earlier obstruction/source-audit packages and their reviews are included as
historical context; their smaller claims and old workspace paths do not
define the current reproduction procedure.

The development checkpoints are Task A
`84f49692065163182d9fcbe1580495f841a75008` and Task B
`f86e52f19569e801ac8d133d7070aa3fe39db08c`. The exact final packaging commit
is recorded in the exported `delivery.json`; embedding a commit's own hash
inside its tracked files would be circular.

## Install the public dependencies

The package includes all project sources, generated literals, input snapshots,
manifests, scripts, and receipts. Lean and Mathlib are standard external
dependencies installed from the pinned public releases below; their binaries
are not bundled. The commands here target Linux x86-64 with Git, Python 3.12,
venv/pip, curl, tar, zstd, and a normal build environment installed.

```sh
python3 -m venv /tmp/lean-review-python
/tmp/lean-review-python/bin/python -m pip install -r research/lean-external-review/requirements.txt

mkdir -p /tmp/lean-review-deps
curl -fL https://github.com/leanprover/lean4/releases/download/v4.33.0/lean-4.33.0-linux.tar.zst \
  -o /tmp/lean-review-deps/lean-4.33.0-linux.tar.zst
echo '4b3fb03c29a1e0a253fb1d11f9bae3725f19a0dc6fc09b3ea16d2c9df3349e2c  /tmp/lean-review-deps/lean-4.33.0-linux.tar.zst' | sha256sum -c -
tar --zstd -xf /tmp/lean-review-deps/lean-4.33.0-linux.tar.zst -C /tmp/lean-review-deps
export PATH="/tmp/lean-review-deps/lean-4.33.0-linux/bin:$PATH"
lean --githash
# Expected: d8b18978322de05a8f3dba51ef03cf5461676c17

git clone https://github.com/leanprover-community/mathlib4.git /tmp/lean-review-deps/mathlib4
git -C /tmp/lean-review-deps/mathlib4 checkout --detach db584cd6d46c92f209a44c0f1c829460d327499d
cmp research/lean-multi-host-source/mathlib-lake-manifest.json /tmp/lean-review-deps/mathlib4/lake-manifest.json
```

In the Mathlib checkout, run the following command. Lake obtains the exact
transitive source revisions in the included manifest; no `lake update` is needed.

```sh
lake build Mathlib.Data.Matrix.Mul Mathlib.Algebra.BigOperators.Fin \
  Mathlib.Tactic.FieldSimp Mathlib.Tactic.Ring Mathlib.Tactic.NormNum
```

Mathlib's official cache is optional. The original environment could not
access its Azure endpoint and successfully built these targets from source.
The pinned Mathlib release also pins Lean 4.33.0. No project-specific
precompiled artifacts are required for fresh reproduction.

## Reproduce both tasks

From the review source root, after preparing the dependencies:

```sh
/tmp/lean-review-python/bin/python research/lean-external-review/reproduce.py \
  --lean /tmp/lean-review-deps/lean-4.33.0-linux/bin/lean \
  --mathlib /tmp/lean-review-deps/mathlib4 \
  --build-dir /tmp/lean-review-task-b-fresh \
  --receipt-dir /tmp/lean-review-receipts-fresh
```

The last two paths must be new. This verifies the complete package inventory,
rechecks source binding/regeneration, builds Task A afresh, then builds Task B
afresh and audits all named theorem closures with `lean -t 0`. Logs and receipts
go under `--receipt-dir`. The earlier Task B build took about 46 minutes of
module wall time, plus Mathlib setup; timings vary. Task A needs no Mathlib.

The packaged Task B validation reused 52 local compiled modules. Their original
receipt did not record byte hashes for the installed Lean distribution, Mathlib
or Mathlib's eight dependencies; see [validation](VALIDATION.md) for their names
and the resulting limit on that resumed PASS. The fresh command above removes
reliance on those historical modules: it recompiles all 52 and records the
actual toolchain/library hashes for the new run. It resolves the missing record
for that new verification, without changing the historical receipt.

For a build interrupted under the current runner, use the same build directory,
a new receipt directory, and `--resume`. Every reuse is checked against source,
local dependency, artifact, and recorded external-environment hashes. See
[BUILD.md](../lean-multi-host-source/BUILD.md) and the build review for the
explicitly disclosed legacy-cache path used for this packaging validation.
The default fresh command above needs no historical cache.

`package-manifest.json` binds all delivered review files except itself and
its inventory-validation receipt, avoiding a hash cycle. The exported
`SHA256SUMS` binds those files too. Old receipts remain historical evidence;
new receipts identify fresh compilation versus reuse. Hash equality alone
is an integrity check, not an independent mathematical review.

## Regenerating the delivery

After committing a clean reviewed tree, the following exports the cumulative
patch, portable source archive, exact commit IDs, and checksums outside Git:

```sh
python3 research/lean-external-review/export_review.py --output-dir /tmp/lean-review-delivery
```

The exporter deliberately does not commit its own output into the package.
This avoids recursive archives while keeping the complete delivery recipe
and all authoritative sources under version control. Nothing is pushed or published.
