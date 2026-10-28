# Dependency release status — 28 October 2026

The v0.8.0 Python release is **blocked**. No audit ignore, incompatible resolver override,
or successful upgraded-deployment claim has been added.

The initial CI audit found vulnerable retained transitive packages. The refreshed universal
Python 3.12 lock updates those packages, removes unused ADK evaluation extras from the shipped
fleet, and raises the media dependency to Pillow 13.0.0. The local audit now reports exactly
one advisory in one package:

| Package | Candidate | Advisory | Patched version | Constraint |
|---|---|---|---|---|
| `opentelemetry-api` | 1.44.0 | CVE-2026-114603 / GHSA-xcq7-p3pf-p88h | 1.45.1 | ADK 2.13.0 requires API/SDK <=1.44 |

The [upstream advisory](https://github.com/open-telemetry/opentelemetry-python/security/advisories/GHSA-xcq7-p3pf-p88h)
describes excessive CPU consumption while parsing malformed inbound `tracestate` headers.
The [ADK package metadata](https://pypi.org/pypi/google-adk/2.13.0/json) supplies the incompatible
upper bound. An offline successful suite does not clear that advisory or prove that malformed
headers are unreachable at every deployed instrumentation boundary.

Next: obtain a supported ADK constraint update or an explicitly reviewed patched distribution,
resolve the complete graph normally, then repeat audit and compatibility gates. Do not change
the requirement metadata silently, use `--no-deps`, or suppress the advisory as a release shortcut.

The public evidence console contains static HTML/CSS/JavaScript and reviewed media; it does not
install or execute the Python dependency graph. Its dated inventory/evidence correction can be
published separately, with immutable evidence links and an explicit release-pending source stamp.
It does not upgrade the GCP fleet. The report remains uncommitted and will be regenerated once,
after the engineering and feasible control/evidence work is finished.
