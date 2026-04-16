---
title: "Hardening a Static Blog: Headers, CSP, and One Warning I Left Alone"
date: 2026-04-16
description: "How I went from no security headers to a clean scan on mrdee.in — and what I learned reading Congo theme source along the way."
tags: ["security", "hugo", "cloudflare", "csp", "notes"]
---

I ran [securityheaders.com](https://securityheaders.com) against mrdee.in recently. The grade was not good. Missing HSTS, no CSP, no framing protection — the usual neglect you accumulate when you're focused on content and treating the hosting layer as someone else's problem.

It took about 20 minutes to fix. Here's what I did and why.

---

## The Fix: a `_headers` file

Cloudflare Pages reads a `_headers` file from the root of your published site and applies the directives to every response. No middleware, no Workers, no config panel. Drop a file, push, done.

I added `static/_headers` to the Hugo repo so it gets copied into the build output automatically:

```
/*
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'self' static.cloudflareinsights.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' cloudflareinsights.com; font-src 'self'; frame-ancestors 'none'
```

What each one does:

- **HSTS** — tells browsers to only ever connect over HTTPS, for the next two years, including subdomains. The `preload` flag submits the domain to browsers' built-in HSTS lists.
- **X-Content-Type-Options: nosniff** — stops browsers from guessing content types. Prevents a text file being executed as a script.
- **X-Frame-Options: DENY** — blocks the site from being embedded in an iframe. Clickjacking mitigation.
- **Referrer-Policy** — sends the full URL as referrer within the site, but only the origin when crossing to other domains.
- **Permissions-Policy** — explicitly revokes camera, microphone, and geolocation access. Belt-and-suspenders on a blog that needs none of those.
- **Content-Security-Policy** — the interesting one. More on this below.

---

## The CSP `unsafe-inline` Problem

My first draft of the CSP included `'unsafe-inline'` in `script-src`. The scan came back with an amber warning: *this policy contains 'unsafe-inline' which is dangerous in the script-src directive.*

The standard advice is to replace `'unsafe-inline'` with per-script hashes or a nonce. But before doing that, I wanted to understand whether the site actually needed it.

I read through the Congo theme's layout templates — specifically `head.html`, `schema.html`, `analytics.html`, and `vendor.html`. What I found:

- All JavaScript is loaded as **external files** with SRI integrity hashes (`$jsAppearance`, `$bundleJS`). No inline `<script>` blocks with executable code.
- The only inline `<script>` tags are `type="application/ld+json"` — JSON-LD structured data for schema.org. These are not executed as JavaScript by browsers.
- Cloudflare Web Analytics, when injected by Cloudflare Pages, uses an external `<script src="...">` tag, not inline code.

`'unsafe-inline'` wasn't needed. I removed it. `style-src` still carries it because Congo applies dynamic appearance classes at runtime (dark/light mode switching) that require it — that's a separate and lower-severity issue.

---

## The Amber Finding I Left Alone

After fixing the CSP, one amber finding remained: `Access-Control-Allow-Origin: *`.

This sounds alarming. Wildcard CORS means any website can fetch your content cross-origin. On an API server with authenticated sessions and sensitive responses, that's a real problem.

On a public static blog, it's the correct setting. There's no private data, no cookies tied to anything sensitive, no user-specific responses. Locking it down to `https://mrdee.in` would break RSS readers and any site legitimately fetching the content — with zero security benefit. Cloudflare Pages sets this by default on static assets. I didn't add it, and I didn't remove it.

Security findings are not equally weighted. This one is amber on a scanner because it *can* be dangerous in the wrong context. In this context it isn't.

---

The final scan came back clean on everything that matters. The whole thing — reading the theme source, writing the headers, pushing, re-scanning — took less time than writing this post.
