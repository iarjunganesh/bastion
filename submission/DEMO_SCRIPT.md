# Bastion demo recording script

- **Target:** **3:49**, locked and measured. Never exceeds four minutes.
- **Start only after:** `submission/CAPTURE_RUNBOOK.md` is complete and the claim matrix is
  reconciled. Both were as of 2026-08-27.

## Recording setup

- Record 1920×1080 at 30 fps with browser and terminal text readable.
- Use one clean browser profile and pre-open every sanitized console tab.
- Disable notifications and hide bookmarks, account menus, project IDs, principals, and URLs.
- Keep the final architecture PNG ready as the opening and closing frame.
- Prefer one continuous take. Cuts may shorten pauses but must not imply a result that did not run.
- Discard any take containing a secret, private origin, principal, raw IAM policy, prompt, response,
  or unredacted payload.

## Timed shot list and narration

**Generated — do not hand-edit.** The narration text lives in
[`scripts/generate_demo_voiceover.py`](../scripts/generate_demo_voiceover.py); this table is
emitted by `python scripts/generate_demo_voiceover.py --table` from the **measured** duration of
each committed clip, plus a deliberate hold for the live action on screen. Editing the words here
instead is how a shooting script and its committed audio drift apart, which is worse than either
being wrong alone: the session trusts the doc and the timeline trusts the audio.

Total **3:49** — 195s narrated across eleven beats, 35s of holds. The four-minute ceiling is hard
and judges have said they stop at it, so the cut is built to land with eleven seconds to spare.

| Time | Screen and action | Narration |
|---|---|---|
| 0:00–0:33 | Title over the dark enterprise-fleet architecture, then straight into the console | “Enterprise permissions change every day. Access reviews don't. Bastion is a fleet of three governed agents that audits the Google Cloud project it runs inside — reading production IAM read-only. It can ask a human to review a permission. It cannot change one. It's deployed on Google's managed agent stack, not a local script — and building it there surfaced a real defect in Google's own ADK, which we reported upstream. Everything after this is live.” |
| 0:33–0:52 | Publish the approved event; show the durable inbox admitting it | “An approved enterprise event opens the investigation. Pub/Sub and Eventarc give it a durable inbox with a lease, so the work survives a restart. This deployment is event-triggered — there is no recurring schedule in this snapshot.” |
| 0:52–1:17 | Live IAM counts landing, then the canonical deterministic findings | “The Access Auditor reads production IAM with read-only authority — sixty-two live bindings on this route. Deterministic rules, not the model, produce the findings: three, across two owning teams. Raw principals, roles and bindings stop inside that tool.” |
| 1:17–1:36 | Gemini rationale appearing, then the fidelity check passing | “Gemini 3.5 Flash writes a bounded rationale for one finding. It cannot add, drop, re-score or redirect one. Every field is checked against the tool's canonical output; if they disagree, the investigation fails closed.” |
| 1:36–1:57 | Two department deliveries and the single durable review record | “The Escalation Agent holds no IAM read role at all, and no model. It delivers count-only reviews to the teams that own them — two findings to security-engineering, one durable review record. Completion requires a receipt from every required delivery.” |
| 1:57–2:17 | The approved exception, then the later suppression and the absent notification | “A human approved an exception for platform-infra. Three days later, across redeployments and restarts, the matching finding was suppressed and that team was not paged again. The decision was remembered across a real elapsed gap — not re-derived by a model.” |
| 2:17–2:37 | Auditor identity permitted, Escalation identity denied the same read | “Separation is enforced by IAM, not prompt wording. The Auditor identity performs this read; the Escalation identity is denied the same call. This denial is reproduced by impersonation, not captured mid-investigation.” |
| 2:37–2:54 | The agent-mediated Model Armor refusal on the Auditor's own A2A surface | “A compromised authorized caller sends an injection through the Auditor's own A2A surface. The deployed callback refuses it before Gemini. The task fails closed, and zero model submissions, completions or tool calls follow.” |
| 2:54–3:15 | Cloud Trace span tree, then the correlated payload-free audit query | “Cloud Trace shows one connected chain — twenty-two spans across the Runtime and both workers. Separately, a payload-free audit joins every event under one investigation ID, retained a year in europe-west4. The trace expires; the audit is the compliance record.” |
| 3:15–3:29 | Deployment overview across the managed Google Cloud surface | “All of it runs privately on Google Cloud — managed Agent Runtime, Gateway, Registry and Memory Bank, with Cloud Run, Firestore, Pub/Sub and Vertex AI behind an IAM-private boundary.” |
| 3:29–3:49 | Closing on the dark architecture still | “Bastion turns real IAM into remembered, department-owned action — without ever giving an agent write access. The ADK defect it surfaced is now an open issue upstream, confirmed by a Google maintainer. Every claim here has a proof boundary in the public repository.” |

The narration is bounded by [`planning/11-claim-matrix.md`](planning/11-claim-matrix.md). The two
`Partial` rows — managed Gateway refusal and retry/dead-letter — appear nowhere in the script at
all, rather than appearing in narrowed form. If a further item turns out partial on the day, remove
its shot and narration rather than speaking the target state.

### Why the ADK finding is mentioned twice

The internal winning plan holds that the upstream contribution is *"the closing credibility beat,
not the product's opening beat."* That is right, and the cut follows it: the hook spends one clause on it — enough that a judge knows it exists — while the full
story, including the maintainer's confirmation, lands in the close where the plan wanted it. The
opening remains about the product: the problem, the self-audit twist, the read-only boundary, and
the managed stack.

### Producing the audio

```powershell
python scripts/generate_demo_voiceover.py            # synthesise clips, captions, and this table
python scripts/generate_demo_voiceover.py --table    # re-measure without re-synthesising
python scripts/generate_demo_voiceover.py --clip hook # after changing one beat's wording
```

Clips are committed under `assets/demo-voiceover/` with a SHA-256 sidecar each. **Chirp3-HD returns
a slightly different duration for identical text on each call** — one beat measured 16.2s, 18.9s
and 16.2s across three runs — so the committed MP3 is the stable artifact and the sidecar stops a
casual re-run from re-jittering every timing this table depends on. Regeneration happens only when
the words change.

Captions are at `assets/demo-video/bastion.srt`, 35 cues. No timepointing is exposed for Chirp3-HD,
so each cue boundary is a real per-sentence measurement scaled to the beat clip's measured length —
a scaled measurement, not a word-count estimate, and not a direct one either.

## Rehearsal and publication gate

- [ ] Two full rehearsals finish at 3:49 ± 3s without speeding up or trimming a hold.
- [ ] The problem and the self-audit twist land inside the first 20 seconds of the hook, before
  the ADK clause.
- [ ] Live behavior and Google Cloud proof are unmistakable.
- [ ] The video says “three days,” not “weeks observed.”
- [ ] The video distinguishes explanatory trace from retained compliance audit.
- [ ] The video never claims IAM remediation, end-to-end EU residency, immutable retention,
  recurring scheduling, or an unobserved failure boundary.
- [ ] Review every transition frame at 200% zoom for sensitive data.
- [ ] Upload to YouTube or Vimeo and enable English subtitles/captions.
- [ ] Verify 1080p public playback while signed out.
- [ ] Add the final URL to README, the public evidence console, and `devpost-submission.md`.

## Failure recovery

If a live step fails, keep the investigation failed/reclaimable, restore the healthy revision, and
verify the fleet before another take. Do not splice an old success into a current-revision demo.
If a console view cannot be safely redacted without becoming unreadable, replace it with the
reviewed evidence artifact and narrate exactly what was observed.
