# Security Policy

SPDRM is a static-site builder: there is no server component, no database, and
nothing to break into on the project side. The generated site is plain static
files. That said, if you find something real, here is where it belongs.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting (the "Report a vulnerability"
button under the repo's Security tab). Please do not open a public issue for
something exploitable.

## What counts

- The builder writing files outside the project root, or executing content
  from `site_data.json` (content should be data, never code that runs at build
  time)
- The generated page executing attacker-controlled input beyond what the
  documented innerHTML caveats already state (see SPEC, Limitations)
- Anything in the runtime that phones home. It should not. If any byte of this
  project contacts a server you did not configure, that is a bug worth
  reporting loudly.

## What does not count

- XSS via `generateDialog()`/`zoomimg()` fed user input, documented behavior;
  they interpolate into innerHTML by design and are meant for fixed internal
  call sites. A proof of concept with the documented caveats removed is still
  worth a read, but it is not a surprise.
- "The back button leaves the site", documented, deliberate, roadmap item.
- Your own site's content is your own problem; the builder validates structure,
  not truth.
