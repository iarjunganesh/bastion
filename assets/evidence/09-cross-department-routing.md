# Evidence 09 — real IAM routes findings to more than one department

**Observed:** 2026-08-18 against the live `bastion-fleet-2026` IAM policy, read through Cloud
Asset Inventory by the deployed Access Auditor's own code path.

The track's first obligation is *"how agents are cataloged for cross-department use."* A
`department` column that nothing branches on does not answer it. This is the measurement that
the branch exists and that **production data actually exercises it**.

## Measured

| | |
|---|---|
| Catalogued departments | 4 |
| IAM bindings scanned | 52 |
| Overly-broad findings | 3 (`roles/owner` × 1, `roles/editor` × 2) |
| **Departments routed to** | **2** — `platform-infra` (1), `security-engineering` (2) |

The findings are produced by `find_anomalies()` and routed by `resolve_owning_department()`,
both deterministic. Routing is matched on the principal string because that is what an IAM
binding carries; it is deliberately **not** a model judgement, since "which team owns this
service account" is an org-chart fact and a model that answered differently on two runs would
send the same finding to two different teams.

## Why two departments rather than one

`platform-infra` claims the default Compute Engine service account, which Google creates with
`roles/editor` and which nothing Bastion builds uses. `security-engineering` is last in the
catalog and matches everything, so it is the default owner rather than a special case — and it
therefore also owns Bastion's own service accounts. **The fleet's own over-permissioning is
security's finding to review**, which is the self-audit loop the project is built around.

A single-department result would have proven only that routing runs. Two departments from
unmodified production data is the obligation demonstrated rather than asserted.

## Proof boundary

- Counts and department identifiers only. **No principal, member, binding, or resource name is
  recorded here**, and none was printed to produce it — the same minimisation the Auditor applies
  before the model boundary applies to this capture.
- This measures routing on live data. It is not a claim about a completed end-to-end
  investigation; that is [evidence 06](06-durable-findings.md).
- The finding count reflects the policy on the observation date. It changes as the project's IAM
  changes, which is the point of a continuous review rather than a quarterly one.
- Department definitions are repository-owned static source in `registry/departments.py`.
  Agent Registry catalogs *agents*; departments are org-chart facts and deliberately do not
  come from a catalog any agent can write to.

```powershell
python -m infrastructure.verify_fleet
```
