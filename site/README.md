# Bastion public evidence console

This directory is a dependency-free static presentation plane for public readers. It is deliberately
separate from Bastion's operational fleet and can be removed without changing any Python or GCP
runtime component.

It does not create a second visual system. `asset-manifest.json` allowlists reviewed light/dark
SVG and animated GIF variants from `assets/brand/` and `assets/architecture/`; `build.mjs` copies
only those files into the static output. The page follows the system theme, offers a local override,
and swaps animated GIFs for the matching static SVGs when reduced motion is requested.

The browser reads only files under `site/`. It never receives a service credential, private
service origin, investigation ID, policy payload, principal, prompt, response, or production token.
The evidence gallery is rendered from the sanitized, source-controlled index in
`data/site-content.json`; the error state links back to the public repository rather than falling
back to a production API.

The index includes the separately dated
[27 October validation](../assets/evidence/14-live-validation.md): 20 real-IAM
executions, not 20 independent policies or an SLO/privacy benchmark. The HTML introduction
and JSON gallery describe the same supplement, including collector recovery and bounded
replay/trace claims. `verifiedAt` and the inventory stamp refer to the independently refreshed
[28 October count-only census](../assets/evidence/15-fleet-inventory.md), which again measured
21 APIs and 39 resources. It does not refresh the 25 August binding count or prove an upgrade.
The architecture images retain their historical August dates.
The submitted gallery/video remain historical. Local source updates do not deploy the site.

Two things on the page look dynamic and are not. The snapshot age beside the verification stamp is
computed in the browser from the `datetime` attribute `check_site.py` already pins to
the selected count-only snapshot's `captured_utc` — there is no second source and no request, because a page that
fetched its own freshness would be claiming a liveness this console deliberately does not have. It
exists to make staleness visible rather than leave a reader to subtract dates. The footer names the
source version and explicitly marks an unreleased candidate; that string is written in `index.html` and gated against
`pyproject.toml` rather than substituted during the build, so the deployed bytes stay identical to
the reviewed source and `check_site.py` can keep failing on any drift between them.

## Local preview

From the repository root, build and serve the exact deployable output:

```powershell
node site/build.mjs
python -m http.server 4173 --directory site/dist
```

Open the local address printed by the server. Run the leak and snapshot-alignment gate before
deployment:

```powershell
python scripts/check_site.py
```

## Vercel

Import the repository through Vercel's native Git integration; no Vercel deployment token or
GitHub Action is needed for this project:

1. In the Vercel dashboard, choose **Add New → Project**, select the intended team, and import
   `iarjunganesh/bastion` from GitHub.
2. Use a presentation-specific project name such as `bastion-evidence`. Set **Framework Preset**
   to **Other** and **Root Directory** to `site`.
3. In the Root Directory setting, keep **Include source files outside of the Root Directory in the
   Build Step** enabled. `build.mjs` needs read access only to the allowlisted reviewed assets in
   the repository-level `assets/` directory.
4. Do not add environment variables, storage, server functions, marketplace integrations, or a
   Railway service. Keep the production branch as `main`.
5. Do not override the repository configuration: `vercel.json` selects the static framework,
   runs `node build.mjs`, publishes `dist`, applies browser security headers, and permits only a
   future privacy-enhanced YouTube or Vimeo player frame.
6. Select **Deploy**. Verify the generated `vercel.app` production URL while signed out before
   configuring the custom domain.

For `bastion.arjunganesh.dev`, open **Project → Settings → Domains**, add the full subdomain, and
copy the exact CNAME host/value Vercel displays into the authoritative DNS provider. Do not assume
a generic target when Vercel supplies a project-specific value. Wait for Vercel to report the
domain valid and provision HTTPS, then ensure production deployment protection does not require a
Vercel login.

The resulting `dist/` output contains no other repository content. No environment variable,
server runtime, external integration, or backend proxy is required.

The release gate was observed on 2026-08-23. The canonical signed-out production URL is
[`https://bastion.arjunganesh.dev/`](https://bastion.arjunganesh.dev/); HTTPS redirect, headers,
desktop/mobile layout, theme switching, reduced motion, 404 behavior, and a browser network log
containing no private GCP request all passed.

The static console may be published independently of a Python fleet release. Evidence URLs
are pinned to an existing public source commit, so locally withheld reports and an unmerged
upgrade cannot create missing `main` links. A static-site update does not deploy GCP code.
