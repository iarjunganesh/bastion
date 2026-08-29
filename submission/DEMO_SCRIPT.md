# Bastion demo recording script

- **Target:** **3:53**, locked and measured. Never exceeds four minutes.
- **Start only after:** `submission/CAPTURE_RUNBOOK.md` is complete and the claim matrix is
  reconciled. Both were as of 2026-08-27.

## Recording setup

- Record 1920×1080 at 30 fps with browser and terminal text readable.
- Use one clean browser profile and pre-open every sanitized console tab.
- Disable notifications and hide bookmarks, account menus, project IDs, principals, and URLs.
- Keep the final architecture PNG ready as the opening and closing frame.
- Record the screen beat by beat, into `assets/demo-video/beats/<NN>-<slug>.mp4`. The
  narration is already continuous and every picture change lands on a beat boundary, so the
  seams are inaudible and invisible — and one fluffed step costs one beat, not the take. A
  single continuous screen recording is equally welcome; split it into the same filenames.
- A cut may shorten a pause but must never imply a result that did not run, and beats must
  stay in scripted order: the sequence is the claim.
- Discard any take containing a secret, private origin, principal, raw IAM policy, prompt, response,
  or unredacted payload.

## Timed shot list and narration

**Generated — do not hand-edit.** The narration text lives in
[`scripts/generate_demo_voiceover.py`](../scripts/generate_demo_voiceover.py); this table is
emitted by `python scripts/generate_demo_voiceover.py --table` from the **measured** duration of
each committed clip, plus a deliberate hold for the live action on screen. Editing the words here
instead is how a shooting script and its committed audio drift apart, which is worse than either
being wrong alone: the session trusts the doc and the timeline trusts the audio.

Total **3:53** — 199s narrated across twelve beats, 34s of holds, with seven seconds of headroom
under a ceiling judges have said they enforce. Two deliberate trades are recorded in
`TARGET_LOW`/`TARGET_HIGH` so the guard still fails on drift rather than quietly widening: the
closing sign-off, and the hook's honest-capture rewording, which cost 2.4s and was paid for by
trimming that beat's hold — it was only cloning the final frame of a 34.3s recording anyway.

| Time | Screen and action | Narration |
|---|---|---|
| 0:00–0:34 | The live public evidence console, scrolled: the hero claim, the fleet counters, the governed production-data path, and the remembered human decision | “Enterprise permissions change every day. Access reviews don't. Bastion is a fleet of three governed agents that audits the Google Cloud project it runs inside — reading production IAM read-only. It can ask a human to review a permission. It cannot change one. It's deployed on Google's managed agent stack, not a local script — and building it there surfaced a real defect in Google's own ADK, which we reported upstream. Everything after this was captured from the deployed fleet.” |
| 0:34–0:53 | Publish the approved event; show the durable inbox admitting it | “An approved enterprise event opens the investigation. Pub/Sub and Eventarc give it a durable inbox with a lease, so the work survives a restart. This deployment is event-triggered — there is no recurring schedule in this snapshot.” |
| 0:53–1:17 | Live IAM counts landing, then the canonical deterministic findings | “The Access Auditor reads production IAM with read-only authority — sixty-two live bindings on this route. Deterministic rules, not the model, produce the findings: three, across two owning teams. Raw principals, roles and bindings stop inside that tool.” |
| 1:17–1:37 | Gemini rationale appearing, then the fidelity check passing | “Gemini 3.5 Flash writes a bounded rationale for one finding. It cannot add, drop, re-score or redirect one. Every field is checked against the tool's canonical output; if they disagree, the investigation fails closed.” |
| 1:37–1:57 | Two department deliveries and the single durable review record | “The Escalation Agent holds no IAM read role at all, and no model. It delivers count-only reviews to the teams that own them — two findings to security-engineering, one durable review record. Completion requires a receipt from every required delivery.” |
| 1:57–2:18 | The approved exception, then the later suppression and the absent notification | “A human approved an exception for platform-infra. Three days later, across redeployments and restarts, the matching finding was suppressed and that team was not paged again. The decision was remembered across a real elapsed gap — not re-derived by a model.” |
| 2:18–2:37 | Auditor identity permitted, Escalation identity denied the same read | “Separation is enforced by IAM, not prompt wording. The Auditor identity performs this read; the Escalation identity is denied the same call. This denial is reproduced by impersonation, not captured mid-investigation.” |
| 2:37–2:54 | The agent-mediated Model Armor refusal on the Auditor's own A2A surface | “A compromised authorized caller sends an injection through the Auditor's own A2A surface. The deployed callback refuses it before Gemini. The task fails closed, and zero model submissions, completions or tool calls follow.” |
| 2:54–3:15 | Cloud Trace span tree, then the correlated payload-free audit query | “Cloud Trace shows one connected chain — twenty-two spans across the Runtime and both workers. Separately, a payload-free audit joins every event under one investigation ID, retained a year in europe-west4. The trace expires; the audit is the compliance record.” |
| 3:15–3:30 | Deployment overview across the managed Google Cloud surface | “All of it runs privately on Google Cloud — managed Agent Runtime, Gateway, Registry and Memory Bank, with Cloud Run, Firestore, Pub/Sub and Vertex AI behind an IAM-private boundary.” |
| 3:30–3:50 | The architecture flow animating, then the coverage report on the same commit | “Bastion turns real IAM into remembered, department-owned action — without ever giving an agent write access. The ADK defect it surfaced is now an open issue upstream, confirmed by a Google maintainer. Every claim here has a proof boundary in the public repository.” |
| 3:50–3:53 | The animated brand banner, with the repository and public evidence console URLs | “Thank you for watching.” |

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

Captions are at `assets/demo-video/bastion.srt`, 36 cues. No timepointing is exposed for Chirp3-HD,
so each cue boundary is a real per-sentence measurement scaled to the beat clip's measured length —
a scaled measurement, not a word-count estimate, and not a direct one either.

### Assembling the cut

```powershell
python scripts/assemble_demo_video.py --check   # which beats are live, which are still placeholder
python scripts/assemble_demo_video.py           # render
python scripts/assemble_demo_video.py --beat iam  # after re-recording one beat
```

**The audio defines the cut, so the edit is not a judgement call.** Each beat occupies its measured
narration length plus its declared hold; the assembler reads both from
[`scripts/generate_demo_voiceover.py`](../scripts/generate_demo_voiceover.py) rather than from this
table, so the picture cannot drift from the sound. A take longer than its beat is trimmed; a shorter
one holds its final frame. Nothing needs to be nudged on a timeline by hand.

Until a beat has a live take the assembler substitutes a reviewed still, and says so. **That build
is a rehearsal scaffold, not the submission** — the hook narration promises live footage, and a
screenshot reel would not keep that promise. The distinction is structural rather than a note to
remember: a scaffold is written to the ignored `assets/demo-video/build/`, and only a fully live cut
earns the name `assets/demo-video/bastion.mp4`, which sits inside the redaction gate's watched globs
and must therefore be declared in `VIDEO_REDACTIONS` and frame-reviewed before the offline gate goes
green again.

Beats are joined by a 0.4s cross-dissolve and the film opens and closes on black. Eight of the
twelve pictures are static console captures, so with hard cuts the middle read as a slideshow; a
short dissolve is what makes a sequence of stills feel authored. Every segment after the first is
rendered one dissolve longer than its beat so the overlap consumes the surplus — the compensation
is per *segment* rather than per beat, because a beat holding two shots contributes two dissolves,
and covering only the beat seams left the picture finishing 0.4s ahead of the narration.

A placeholder is not always a frozen frame. `PICTURES` in the assembler declares each beat's
shots, and a shot is held, looped, or scrolled. The hook is recorded from the live public console by
[`scripts/capture_site_hook.mjs`](../scripts/capture_site_hook.mjs), which drives a real browser
against `bastion.arjunganesh.dev` and pans the hero, the fleet counters, the governed
production-data path and the remembered human decision. It is a recording rather than a scrolled
screenshot because the page genuinely moves — the hero route diagram carries 24 `animateMotion`
elements — and because a fresh browser profile has no account photo, bookmark bar or open tab to
leak, which is the failure the promoted `.takes/` captures had to be cropped around. The committed
repository-page stills remain the fallback when that recording is absent. Where
a placeholder is a diagram it is the **animated** master rather than the still: the event beat runs
the governed investigation flow, whose dots travel Pub/Sub to Eventarc to the durable ingress while
the narration says exactly that, and the close loops the fleet architecture before cutting to the
coverage report on the same commit, after which the sign-off runs the animated brand banner
with the repository and console URLs composited into the clear band beneath its stats row —
on the video frame only, never on the hand-reviewed SVG. Both page captures were promoted
out of ignored `.takes/` the way the gallery images were: browser chrome cropped away, the account
photos that remained in page content masked, and both declared in `REDACTIONS` so
`scripts/redact_evidence.py --check` covers them. The coverage page is shown and never spoken to —
100% is evidence of test discipline, and this project's own upstream ADK finding is the standing
proof that it is not evidence of correctness.

Captions stay a sidecar for the YouTube upload, which is what the publication gate below asks for.
`--burn-captions` hard-subtitles the render instead, for a platform that cannot carry a caption
track.

## Rehearsal and publication gate

- [x] The assembled cut measures 3:53. It is built rather than performed, so it cannot drift
      between takes; re-run `python scripts/assemble_demo_video.py --check` after any change.
- [ ] The problem and the self-audit twist land inside the first 20 seconds of the hook, before
  the ADK clause.
- [ ] Live behavior and Google Cloud proof are unmistakable.
- [x] The video says “three days,” not “weeks observed.”
- [x] The video distinguishes explanatory trace from retained compliance audit.
- [x] The video never claims IAM remediation, end-to-end EU residency, immutable retention,
  recurring scheduling, or an unobserved failure boundary.
- [x] Review every transition frame for sensitive data. Reviewed at all twelve beat boundaries
      as well as the gate's sampled points; `assets/demo-video/bastion.mp4` is declared in
      `VIDEO_REDACTIONS` and the redaction gate passes.
- [ ] Upload to YouTube or Vimeo and enable English subtitles/captions.
- [ ] Verify 1080p public playback while signed out.
- [ ] Add the final URL to README, the public evidence console, and `devpost-submission.md`.

## Failure recovery

If a live step fails, keep the investigation failed/reclaimable, restore the healthy revision, and
verify the fleet before another take. Do not splice an old success into a current-revision demo.
If a console view cannot be safely redacted without becoming unreadable, replace it with the
reviewed evidence artifact and narrate exactly what was observed.
