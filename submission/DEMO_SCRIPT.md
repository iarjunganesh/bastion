# Bastion demo recording script

- **Target:** one 3:45–3:55 public English demo, never exceeding four minutes.
- **Start only after:** `submission/CAPTURE_RUNBOOK.md` is complete and the claim matrix is
  reconciled.

## Recording setup

- Record 1920×1080 at 30 fps with browser and terminal text readable.
- Use one clean browser profile and pre-open every sanitized console tab.
- Disable notifications and hide bookmarks, account menus, project IDs, principals, and URLs.
- Keep the final architecture PNG ready as the opening and closing frame.
- Prefer one continuous take. Cuts may shorten pauses but must not imply a result that did not run.
- Discard any take containing a secret, private origin, principal, raw IAM policy, prompt, response,
  or unredacted payload.

## Timed shot list and narration

| Time | Screen and action | Narration target |
|---|---|---|
| 0:00–0:18 | Title over enterprise-fleet architecture | “Permissions change continuously, but enterprise access reviews are periodic and forgetful. Bastion is a private agent fleet that audits the cloud project running it.” |
| 0:18–0:42 | Three Agent Registry cards | “Each institutional agent is catalogued with an owner, department, version, approved skills, classification, and its own identity.” |
| 0:42–1:04 | Publish the approved event; show admission | “An approved enterprise event starts the workflow. This deployment is event-driven; I am not claiming a recurring Scheduler job.” |
| 1:04–1:35 | Live IAM counts and canonical findings | “The Auditor reads production IAM with read-only authority. Deterministic rules create the findings before Gemini sees anything. Raw principals and bindings never cross the model boundary.” |
| 1:35–1:56 | Gemini rationale then validated routing | “Gemini 3.5 Flash explains a bounded finding. It cannot add, remove, re-score, redirect, or clear one; the output must match the canonical set field by field.” |
| 1:56–2:17 | Two department deliveries | “The model-free Escalation Agent delivers count-only reviews to the departments that own them, and completion requires a receipt from every required delivery.” |
| 2:17–2:40 | Approved exception and later suppression | “This human exception was approved, then remained effective three days later across deployments and restarts. The matching department received no duplicate notification.” |
| 2:40–2:57 | Auditor permitted; Escalation denied | “IAM, not prompt wording, enforces separation: the Auditor can perform this read and the Escalation identity is denied the same operation.” |
| 2:57–3:13 | Agent-mediated Model Armor refusal | “A compromised authorized input is refused by the deployed agent callback before Gemini, and the investigation fails closed.” |
| 3:13–3:31 | Trace then retained audit | “Cloud Trace explains the current route. A separate payload-free retained audit joins Runtime and both workers by investigation ID for compliance reconstruction.” |
| 3:31–3:45 | GCP deployment overview | “The backend runs privately on Google Cloud across managed agent services, Cloud Run, Firestore, Pub/Sub, Eventarc, Vertex AI, and Cloud operations.” |
| 3:45–3:55 | Closing architecture | “Bastion turns real IAM into remembered, department-owned action—without giving an agent write access.” |

If an evidence sprint item remains partial, remove its shot and narration rather than speaking the
target state. Use the exact narrower wording from `submission/planning/11-claim-matrix.md`.

## Rehearsal and publication gate

- [ ] Two full rehearsals finish under 3:55 without speeding up.
- [ ] The problem and self-audit twist land within 18 seconds.
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
