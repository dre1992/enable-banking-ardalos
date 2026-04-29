# Enable Banking — Privacy & Terms site

Static site to host the privacy policy and terms of service for a personal
restricted-access Enable Banking app, served via GitHub Pages.

## What's in here

- `index.md` — landing page with links
- `privacy.md` — privacy policy (served at `/privacy/`)
- `terms.md` — terms of service (served at `/terms/`)
- `_config.yml` — Jekyll config (uses the built-in `minimal` theme)

## Setup (5 minutes)

### 1. Fill in the placeholders

There are four placeholders across the files: `{YOUR_NAME}`, `{YOUR_EMAIL}`,
`{APP_NAME}`, and (optionally for the URL) your GitHub username + repo name.

From inside this directory, run:

```bash
sed -i.bak \
  -e "s|{YOUR_NAME}|Your Full Name|g" \
  -e "s|{YOUR_EMAIL}|you@example.com|g" \
  -e "s|{APP_NAME}|My Personal Banking Tool|g" \
  index.md privacy.md terms.md _config.yml

rm *.bak
```

(On macOS the `-i.bak` form is required; on Linux you can drop the `.bak`
and skip the `rm`.)

### 2. Push to GitHub

```bash
git init
git add .
git commit -m "Privacy and terms for Enable Banking app"
git branch -M main
# create the repo on github.com first (e.g. enable-banking-legal), then:
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3. Enable GitHub Pages

On github.com:

1. Open the repo → **Settings** → **Pages**
2. Under **Source**, select **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)` → **Save**
4. Wait ~1 minute for the first build

Your URLs will be:

- `https://YOUR_USERNAME.github.io/YOUR_REPO/` — landing page
- `https://YOUR_USERNAME.github.io/YOUR_REPO/privacy/` — privacy policy
- `https://YOUR_USERNAME.github.io/YOUR_REPO/terms/` — terms

### 4. Plug into Enable Banking

In the Enable Banking Control Panel app registration form:

| Field | Value |
| --- | --- |
| Privacy URL | `https://YOUR_USERNAME.github.io/YOUR_REPO/privacy/` |
| Terms URL | `https://YOUR_USERNAME.github.io/YOUR_REPO/terms/` |
| Data protection email | the email you used in step 1 |

Confirm both URLs return a 200 in your browser before submitting — Enable
Banking's validator fetches them and rejects unreachable URLs.
