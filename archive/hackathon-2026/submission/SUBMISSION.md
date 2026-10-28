# Devpost submission handoff

**All Things Agentic Hackathon** · **Fortified Enterprise Fleet** · deadline Aug 31, 2026,
5:00 PM PT.

This file separates engineering closure from human publication. A checked engineering claim has
code, deployment, and evidence; an unchecked publication task must still be completed in Devpost
or a media platform.

## Pass/fail technology gates

The submitted packet and August observations below remain dated records. A separate
[post-hackathon report supplement](../../../assets/evidence/14-live-validation.md), collected
27 October, records 20 real-IAM executions on unchanged deployment metadata. It is not part
of the submitted video/gallery and does not close the two partial refusal/retry observations
or create an award claim. Its method and limits are integrated in the
local technical report draft (intentionally uncommitted).

- [x] Gemini 3.5 Flash through Vertex AI `global`; live calls captured in
      [evidence 02](../../../assets/evidence/02-gemini-investigation.md).
- [x] Google ADK 2.13.0 source target; three ADK agents, A2A workers, plugins, tools, and managed Runtime.
- [x] Google Cloud infrastructure; measured deployment in
      [evidence 04](../../../assets/evidence/04-private-fleet-deployment.md).
- [x] Fortified Enterprise Fleet brief addressed across Registry, Runtime, Memory, Identity,
      Gateway, Model Armor, and Observability.
- [x] Public MIT-licensed repository with history inside the submission period.
- [x] Python 3.12 spin-up, bootstrap, verifier, smoke, rollback, and teardown instructions.
- [x] Signed-out public evidence console verified at
      [`bastion.arjunganesh.dev`](https://bastion.arjunganesh.dev/); this is a presentation plane
      only, not a public agent endpoint.
- [x] Devpost category selected and all required fields saved. **Fortified Enterprise Fleet**,
      with description, five-image gallery, video link, repo, hosted URL, testing instructions,
      SDK, services, models and architecture upload all populated as of 2026-08-29.
- [x] Public English demo video under four minutes — **3:53** at [https://youtu.be/Xpj8YmzFfpk](https://youtu.be/Xpj8YmzFfpk),
      with the 36-cue English caption track attached.
- [x] Architecture GIF/image uploaded to Devpost. Two copies exist and they age differently: the
      one *inside* the description is fetched live from `raw.githubusercontent.com/.../main/`, so it
      is current by construction — confirmed on 2026-08-29 reading `Build state · 2026-08-27 ·
      21/21 APIs · 39 resources measured` off the rendered page. The one uploaded under **Additional
      info** is a static copy whose vintage cannot be read at thumbnail resolution; re-upload
      `assets/architecture/enterprise-fleet-architecture-dark.png` to be certain and to match the
      five dark gallery images. Counts have not moved, so only a disclosed date could differ.
- [x] Final submission sent before the deadline. Submitted 2026-08-29; the project page at
      <https://devpost.com/software/bastion-pfuy71> resolves publicly while signed out, with the
      video embedded, five gallery images, and no incomplete-submission notice.

## Three track obligations

| Requirement | Closed by |
|---|---|
| Catalog agents for cross-department use | Managed Registry has the Runtime and two worker cards; cards contain owner/department/purpose/skill/classification/version/approval metadata; deterministic routing rejects unknown departments. |
| Safely maintain context across weeks of asynchronous operations | Firestore IDs/leases/retry/dedup, managed sessions and Memory Bank, expiring approved exceptions, five-attempt DLQ, and idempotent notification. A human exception was observed suppressing its matching finding after a real three-day gap across deployments and restarts ([evidence 10](../../../assets/evidence/10-cross-week-suppression.md)); expiry firing remains test-only and no literal-week claim is made. |
| Use production data without violating policy | Read-only live IAM/Asset access. Raw members, roles, resources and bindings never cross the model boundary at all — minimisation is the sovereignty control, not residency. Opaque IDs, fail-closed Model Armor, post-model protected-data screen, separated identities, count-only private findings record, and explicit regional/global disclosure. |

## Seven-pillar proof

- [x] **Registry:** three governed Bastion agent records and approved platform destinations.
- [x] **Runtime:** identity-bearing Python 3.12 managed Runtime streamed live events through its
      Gateway-bound configuration ([evidence 05](../../../assets/evidence/05-runtime-gateway.md)).
- [x] **Memory Bank:** managed endpoint live; restart, retrieval, expiry, stale-memory, and
      failure branches covered by integration/unit tests. **Suppression is now observed on the
      deployed path** — an exception approved 2026-08-19 suppressed its matching finding on
      2026-08-22, re-confirmed 2026-08-23 after the deterministic-delivery rewrite (P0.1–P0.3)
      ([evidence 10](../../../assets/evidence/10-cross-week-suppression.md)). Expiry firing has not
      elapsed and stays test-only.
- [x] **Identity:** deployed Escalation identity denied IAM read while Auditor was permitted
      ([evidence 03](../../../assets/evidence/03-escalation-agent-denied.md)).
- [x] **Gateway:** IAP fail-closed policy and per-destination Runtime identity grants verified;
      dispatcher direct-peer credential and invoker grants removed. **Caveat:** IAP currently also
      denies a *legitimate* destination — Model Armor's regional endpoint, called from inside the
      Runtime — with the endpoint registered and the role held. Fail-closed is observed; correctly
      admitting a catalogued destination from the Runtime is not. Tracked as D2 in
      [09-capture-backlog.md](../../../docs/research/observation-backlog.md).
- [x] **Model Armor:** **the deployed agent callback refused a real injection attempt on 2026-08-25**
      ([evidence 12](../../../assets/evidence/12-agent-mediated-model-armor-refusal.md)) — sent through the Access
      Auditor's authenticated A2A surface, the task failed closed with `policy_match` and no model
      submission, completion or tool call followed. The threat modelled is a compromised authorized
      caller, not an anonymous one. [Evidence 01](../../../assets/evidence/01-model-armor-block.md) remains the earlier
      direct-template probe; fail-closed and protected-output screening are additionally tested.
- [x] **Observability:** payload-free audit lifecycle, retained regional sink/bucket, four metrics,
      five alerts, and operations dashboard ([evidence 07](../../../assets/evidence/07-observability.md), whose
      `europe-west4` 365-day retention and analytics were re-reviewed in the Console on 2026-08-25 —
      retention proven, immutability still not claimed because the bucket is unlocked). **One
      investigation is now reconstructable end to end:** 28 unique payload-free events across three
      invocation ids under a single investigation id ([evidence 11](../../../assets/evidence/11-current-route-correlation.md)),
      plus a connected 22-span Cloud Trace ([evidence 13](../../../assets/evidence/13-current-route-trace.md)). The trace is
      sampled and expires; the audit trail is the compliance record. They are never derived from each
      other.

## Safety, durability, and failure proof

- [x] Missing/invalid risk fails closed.
- [x] A model cannot alter the authoritative finding set or skip a required delivery: the
      Auditor's structured answer is checked field-by-field against the tool's own canonical
      output (P0.1), the Escalation Agent is a deterministic worker with no model or tool surface
      to poison (P0.2), and a completion gate refuses to report an investigation done unless every
      routed department was actually confirmed delivered (P0.3). Deployed and observed 2026-08-23
      on a real triggered investigation.
- [x] Raw IAM member/binding data stops before the model; unsafe output stops before notification.
- [x] Fixed tool declarations and allowlists defend the tool-metadata boundary; the Escalation
      Agent holds no policy tool at construction, asserted and shown to fail when widened
      ([evidence 08](../../../assets/evidence/08-tool-poisoning.md)).
- [x] Worker timeout/malformed response, hallucinated arguments, Model Armor/dependency outage,
      notification failure, duplicate event, expired lease, retry, dead letter, and stale memory
      are exercised across populated unit, integration, security, and load suites.
- [x] Real findings endpoint denies anonymous traffic and collapses an authorized duplicate
      ([evidence 06](../../../assets/evidence/06-durable-findings.md)).
- [x] 321 tests pass with 100% configured core statement and branch coverage under Python 3.12.
- [x] Ruff, formatting, mypy, dependency audit, secret scan, docs/version checks, and diagram
      determinism are release gates.
- [x] ADK deprecation/experimental risk consciously accepted and pinned in
      [ADR-005](../../../docs/adr/005-adk-as-the-agent-framework.md).

## Prerequisites and bonus

- [x] Hackathon credits/project available; sensitive account details omitted.
- [x] [Gemini Enterprise Agent Ready badge](https://developers.google.com/profile/badges/community/gear?u=iarjunganesh)
      claimed and linked from README.
- [x] Devpost registration and project ownership reconfirmed on 2026-08-27; live project `1398552`
      remains a `submission_draft`, with no submission timestamp and an empty video field.
- [ ] Billing budget/anomaly notification reconfirmed in the console before final recording.
- [x] Optional launch blog published with the hackathon disclosure. <https://dev.to/arjunganesh/what-100-test-coverage-missed-state-across-google-adk-a2a-boundaries-29i1>
- [x] Optional social post published with `#AllThingsAgenticHackathon`. <https://www.linkedin.com/posts/iarjunganesh_allthingsagentichackathon-googlecloud-share-7499586701733068801-PENp/>

## Do not claim until verified

The following claims are deliberately not made:

- no automated IAM remediation or permission write;
- no WORM/immutable audit storage—the 365-day bucket is unlocked;
- no end-to-end EU residency—Gemini uses Vertex AI `global`;
- no legal compliance certification;
- no historical 99% availability, latency, cost, or accuracy figure;
- no claim that a wall-clock week elapsed—the observed gap is three days and expiry firing is
  covered by tests only;
- no claim that Model Armor alone prevents tool poisoning—the fixed tool and IAM boundaries do.

## Final publication pass

- [x] Prepare the field-by-field local Devpost worksheet, judge-facing write-up, architecture PNG,
      3:2 thumbnail, capture runbook, demo script, and bonus-copy drafts. The Devpost draft,
      required architecture image, the five-image gallery and the demo video now all exist. See
      [`../devpost-submission.md`](../devpost-submission.md).

- [x] Generate the narration and lock the cut. Twelve beats are synthesised with Google Cloud
      Text-to-Speech, measured rather than estimated, and hash-stamped so a casual re-run cannot
      re-jitter the timings; the cut is **3:53**, inside the four-minute ceiling with seven
      seconds to spare. `archive/hackathon-2026/scripts/assemble_demo_video.py` builds the timeline from that committed
      audio, so the picture cannot drift from the sound and no timeline editor is involved.
- [x] Capture the opening beat from the live public console. `archive/hackathon-2026/scripts/capture_site_hook.mjs`
      drives a real browser against `bastion.arjunganesh.dev` and records the hero, the fleet
      counters, the governed production-data path and the remembered human decision. It records
      the page viewport from a fresh profile, so no browser chrome or account photo can enter
      frame.

- [x] Record the catalog → event → Runtime/Gateway → IAM denial → Armor refusal → idempotent review
      → audit dashboard story without exposing a principal or endpoint. **Published 2026-08-29** at
      [https://youtu.be/Xpj8YmzFfpk](https://youtu.be/Xpj8YmzFfpk): 3:53, twelve beats, declared in `VIDEO_REDACTIONS`
      and reviewed at every beat boundary. Any beat can still be upgraded by dropping a screen
      recording into `assets/demo-video/beats/<NN>-<slug>.mp4`, which takes precedence
      automatically — but the published URL points at a fixed file, so a re-cut means re-uploading.
      `python archive/hackathon-2026/scripts/assemble_demo_video.py --check` lists what each beat is showing.
- [ ] Verify every Devpost number against `gcp-state.json` immediately before submission.
- [x] Verify the static evidence console and custom domain while signed out; its observed browser
      network log contains no private GCP request.
- [ ] Keep private services running through judging; do not expose an agent merely to create a
      public hosted-project URL.
- [x] Run the complete local and live release gates, push `main`, and confirm GitHub Actions
      green. Done for `v0.5.1`; due again for `v0.6.0` and after the final submission-preparation
      commit, because this
      one is satisfied per-push rather than once.
- [x] Release tags are explicit release decisions rather than engineering side effects:
      `v0.2.0` carries the seven deployed-fleet defects found after `v0.1.0`, and `v0.2.1` carries
      the escalation hand-off fix. `v0.3.0` is the hosted-evidence release. `v0.4.0` carries the
      deterministic Auditor-fidelity, Escalation-delivery, and completion-gate rewrite (P0.1–P0.3),
      deployed and re-verified live the same day. `v0.5.0` packages clean-clone proof, the claim
      matrix, submission drafts, and five closed observations; `v0.5.1` corrects and gates the
      architecture capture date; `v0.5.2` composes the five-image gallery and adds the redaction
      gate that caught an operator account photo in a promoted evidence capture; `v0.6.0` moves
      every pin to the newest release the resolver allows and fixes the pre-tag gate that had been
      surveying five pins of twenty-three; `v0.7.0` is the publication release — it assembles the
      3:53 demo from the committed narration, publishes it, and threads the URL through the README,
      the public console, the Devpost write-up and the bonus drafts. Each annotated tag is created
      only after its release metadata, full gates, pushed commit, and green `main` CI all agree.

- [ ] **Redeploy both surfaces onto the `v0.6.0` dependency resolution and re-verify live.** Until
      this happens the source targets the upgrade in [version provenance](../../../docs/VERSIONS.md), and no claim
      may say production runs the newer resolution. Doing it obliges re-capturing evidence 11, 12
      and 13 and recomposing gallery images 03, 04 and 05, because those records name the current
      Cloud Run revisions.
