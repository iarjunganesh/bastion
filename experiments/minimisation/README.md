# Offline minimisation study preparation

This folder is an evaluation of Bastion's design using synthetic IAM only. It is
not a product input path, benchmark result, live audit, or model evaluation yet.
The current harness contains no network or model client and requires no extra
packages. Use Python 3.12; outputs belong in ignored scratch directories.

```powershell
python -m unittest discover -s experiments/minimisation -p "test_*.py" -v
python experiments/minimisation/study.py --output .tmp/minimisation-preparation
```

## Protocol fixed before model runs

- Dataset: 50 policies, 20-80 single-member bindings each; fixed seed 20261011.
  Five clean controls, unique synthetic principals under `example.invalid`,
  synthetic department mapping and a public experiment-only HMAC key. No actual
  project IAM, credentials, production key or catalog is read.
- Scoped ground truth: Owner/Editor grants only, fixed score 0.8. The adapter
  compiles the unchanged production `finding_id`/`find_anomalies` AST bodies and
  constants with isolated synthetic dependencies. It avoids importing agent and
  cloud clients. It records the full source hash. This is not module integration
  verification. The dedicated parity test compares all 50 cases with the normally
  imported detector under synthetic key/resolver fixtures and a socket-connect
  guard. It passed on Python 3.12.12 using existing dependencies; no packages or
  production environment configuration were changed.
- Raw detection: policy input, predicted member-role pairs; precision/recall,
  duplicates and score/schema diagnostics should be reported separately. Empty
  denominators are undefined, not silently perfect. Current scorer supplies pair
  metrics only; full response schema/score diagnostics remain to implement.
- Matched explanation comparison: raw policy plus canonical findings versus the
  identical canonical findings alone. Both arms explain, preserving finding
  fields. This is a representation comparison, not a detection comparison.
- No-model template: one fixed category explanation. Offline output controls
  validate the harness; they are not substituted model responses.
- Injection pair: malicious synthetic resource label appears in raw matched input;
  paired minimised input is identical to its benign version because that label
  is absent. This tests label exclusion, not all injection placements or the live
  fetch path. Model refusal/drift effects remain unmeasured.
- Three replicate IDs per model condition: 750 request envelopes prepared, zero
  dispatched. Replicates are identifiers, not claims of model seed support.
- Structural fidelity compares IDs, duplicate detection, deterministic fields,
  count and rationale length. This is not semantic explanation faithfulness.
- Exposure: exact/NFKC-casefold-whitespace-normalized matches against synthetic
  principal, role and benign resource-label strings. Exposure of a role name may
  be useful explanation rather than harmful leakage; report string classes
  separately. No inference/paraphrase/side-channel privacy guarantee follows.

## Still required before model evaluation

Local configuration and response-validation update (11 October): `config.json`
explicitly selects Bastion project/quota project and global location. Generation
is disabled. `configuration.py` validates settings and provides a future SDK
credential override in memory; it never modifies saved ADC or gcloud configuration.
`responses.py` now strictly parses model response JSON and records structural
invalidity/refusals/errors without turning them into valid empty answers. Nine
tests pass. No SDK client, model dispatch or reliable cost enforcement exists yet;
the configured 200 SEK ceiling alone is not a working spend limiter.

1. Finish batch ingestion and per-condition aggregation around the completed
   strict parser/evaluator. Join all planned trials, explicitly represent missing
   records and reject duplicate/unknown trial identities. Keep refusals/errors in
   denominators and distinguish invalid from empty answers.
2. Add reviewed field-level matched raw context, human rating sheets and a bounded
   rationale faithfulness/usefulness rubric. Blind condition labels; use two
   raters for agreement or explicitly report single-rater limitations. Compare
   against the template. No human scores or agreement currently exist.
3. Finalize injection success criteria and threat scope before running. General
   omission rates differ from attack success; pair benign/injected cases.
4. Add a separately authorized model adapter with exact model/version/date,
   generation settings, token usage, latency, retries and actual cost accounting.
   Fail before dispatch without a verified spend budget; hard cap 200 SEK.
5. Analyze paired effects with uncertainty bootstrapped over policy, keeping its
   replicates together. No statistical results exist from this preparation.

The experiment stays outside production packaging, the configured core coverage
sources and the existing pytest `tests/` discovery path. No third-party dependency
or optional requirements file is needed yet. Product detection is unchanged.
