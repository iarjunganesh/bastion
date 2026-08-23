# Social launch copy

Publication drafts only. Refresh the Devpost/video URLs and upstream status immediately before
posting. Publish one primary post; do not fragment the bonus proof across unrelated posts.

## LinkedIn draft

I built **Bastion**, a private fleet of catalogued agents that audits the IAM policy of the Google
Cloud project running it.

The twist is that Gemini does not decide what is risky. Deterministic rules create the canonical
findings before the model boundary; Gemini 3.5 Flash contributes bounded rationale; IAM and a
model-free delivery agent enforce who can read data and who can contact each department.

Bastion also remembers human-approved exceptions in durable state. In the deployed proof, a
decision remained effective three days later across deployments and restarts, suppressing the
matching duplicate notification.

Building the real A2A topology uncovered an ADK session-state boundary that local tests could not
show, even with full configured core coverage. I reported the reproducer upstream and proposed a
complementary construction-time warning.

- Project: TODO_DEVPOST_URL
- Demo: TODO_VIDEO_URL
- Evidence: <https://bastion.arjunganesh.dev/>

\#AllThingsAgenticHackathon

## X / concise draft

Bastion is a private fleet of catalogued agents that audits live GCP IAM, remembers human
decisions, and routes minimized findings—without IAM write access.

Deterministic findings. Gemini 3.5 Flash rationale. IAM-separated agents. Durable context. Real
GCP proof.

TODO_DEVPOST_URL

\#AllThingsAgenticHackathon

## Publication gate

- [ ] Replace every `TODO_*` placeholder.
- [ ] Attach `assets/screenshots/01-enterprise-fleet-architecture.png` or the approved security
  boundary image.
- [ ] Keep `#AllThingsAgenticHackathon` exact.
- [ ] Ensure the post and every link are public while signed out.
- [ ] Do not say the upstream pull request is merged without a live GitHub check.
- [ ] Save the public post URL for the Devpost bonus field.
