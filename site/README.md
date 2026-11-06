# Public evidence console

A static presentation plane, separate from the operational GCP fleet. The browser reads only
sanitised files under this site: no credentials, private origins, principals, findings payloads
or production API requests. Removing the console does not change the fleet.

`asset-manifest.json` allowlists the reviewed brand/architecture variants copied by `build.mjs`.
`data/site-content.json` supplies the evidence cards. Each card is bounded by its linked dated
record; an older record cannot substantiate a later deployment. `verifiedAt` refers only to
the 28 October count-only inventory, not liveness or package resolution. Architecture images,
submitted gallery and fixed video keep their historical dates. Local edits are not deployment.

## Build and preview

```powershell
node site/build.mjs
python scripts/check_site.py
python -m http.server 4173 --directory site/dist
```

The gate checks source/output agreement, inventory dates, public links, headers and prohibited
private content. The browser computes snapshot age locally. The footer source version must
match `pyproject.toml`; the build does not substitute a newer deployment claim.

## Vercel deployment

Deploy only after reviewing the generated output and obtaining the required authorization:

1. Import `iarjunganesh/bastion` with root directory `site`, preset **Other**, production branch
   `main`, and access to repository files outside that root enabled for the allowlisted assets.
2. Keep `vercel.json`: static build `node build.mjs`, output `dist`, security headers and limited
   video-frame policy. Add no environment variables, storage, server functions or backend proxy.
3. Verify the signed-out deployment before adding the custom domain. In **Settings → Domains**,
   add `bastion.arjunganesh.dev` and use the exact CNAME Vercel supplies; wait for valid DNS/TLS.
4. Check redirects, headers, desktop/mobile layout, theme switching, reduced motion, 404 handling
   and a browser network log containing no private GCP requests.

The canonical [public console](https://bastion.arjunganesh.dev/) passed that publication check
on 23 August; subsequent source alignment is not a fresh deployed-byte verification. Published
record URLs pin existing public commits. Withheld report/new evidence sources remain local
until their separate publication step. See the [report plan](../docs/research/report-plan.md).
