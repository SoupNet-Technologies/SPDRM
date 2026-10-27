# Deploying an SPDRM site

The generated output is static: one `index.html`, a `manifest.json`, a
`sitemap.xml`, an `assets/` folder, and the error pages. Hash routing means no
server rewrites are needed anywhere, so any host that serves files will work.
These are the recipes, best first.

The builder writes everything to the repo root by default:

```text
python3 spdrm/build.py
```

Artifacts to deploy: `index.html`, `manifest.json`, `sitemap.xml`, `assets/`,
`403.html`, `404.html`, `500.html`. Nothing else. Do not deploy `spdrm/` (that is
the builder) and do not deploy `index.html.bak`.

## 1. Private git repo + Cloudflare Pages

The flagship path, and how the SPDRM demo itself is deployed
([spdrm.jessy.boo](https://spdrm.jessy.boo)). Your site source stays private; only the built
artifacts ever go out.

### Option A: CI direct upload (what this repo does)

The repo ships `.github/workflows/deploy.yml`. It builds the site on every push
to `main`, stages a `dist/` folder, and uploads it with wrangler.

1. Keep your site source (including `site_data.json`) in a private repo.
2. Create a Cloudflare API token with **Cloudflare Pages: Edit** permissions
   (Cloudflare dashboard → My Profile → API Tokens).
3. In the repo: Settings → Secrets and variables → Actions, add
   `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.
4. Create the Pages project once (any deploy creates it):
   `npx wrangler pages deploy dist --project-name=<yours>` locally the first
   time, or just let the workflow do it.
5. Add your custom domain in the Pages project: Custom domains → set up domain.

Every push to main now builds and ships. The build is the test: if the JSON is
broken, validation fails and nothing deploys.

### Option B: Cloudflare Pages git integration

In the Cloudflare dashboard: Workers & Pages → Create → Pages → Connect to Git.
Pick the repo, then:

- Build command: `python3 spdrm/build.py`
- Build output directory: `/` (the repo root; or use a build script that stages a
  `dist/` and point there (cleaner, see this repo's deploy workflow)
- Environment: Python 3 is preinstalled on Pages build images.

Cloudflare rebuilds on every push and runs branch previews for PRs.

## 2. GitHub Pages

Hash routing means no 404-rewrite gymnastics: `index.html` handles every route.

### Via Actions (keeps source private, deploys the artifact)

```yaml
name: GitHub Pages
on:
  push:
    branches: [main]
permissions:
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v5
      - run: python3 spdrm/build.py
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .   # or a staged dist/ folder
      - id: deployment
        uses: actions/deploy-pages@v4
```

Settings → Pages → Source: GitHub Actions.

### From a branch

If your repo is public anyway, commit the built artifacts and point Pages at the
branch root. Rebuild before pushing. Works, but CI is less forgettable than you.

## 3. Apache (classic)

From the original SPDRM hosting, circa 2023. `.htaccess` in the site root:

```apache
# strip www
RewriteEngine On
RewriteCond %{HTTP_HOST} ^www\.(.+)$ [NC]
RewriteRule ^(.*)$ https://%1/$1 [R=301,L]

ErrorDocument 403 /403.html
ErrorDocument 404 /404.html
ErrorDocument 500 /500.html

Options -Indexes
AddDefaultCharset UTF-8
```

Gzip and long-lived cache headers are worth adding; the original repo kept them
commented out for years. Learn from that or do not, it deployed fine anyway.

## 4. nginx

```nginx
server {
    listen 443 ssl;
    server_name yoursite.example;
    root /var/www/yoursite;
    index index.html;

    error_page 403 /403.html;
    error_page 404 /404.html;
    error_page 500 /500.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

`try_files ... =404` is all the "SPA routing support" you need, cause the router
never asks the server for a route in the first place.

## 5. Any dumb static host

Netlify, Vercel, a $2 VPS with `python3 -m http.server` behind a reverse proxy,
an S3 bucket, a Raspberry Pi on a shelf. Build command is the same, output is the
same, no rewrites anywhere. If the host can serve an HTML file, it can serve an
SPDRM site.
