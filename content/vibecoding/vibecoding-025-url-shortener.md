---
title: "Vibecoding 025 — go.short: a custom URL shortener, admin UI, and linktree"
date: 2026-05-01
description: "A Cloudflare Worker + KV URL shortener with a full admin UI, 36 slugs, and a branded linktree — plus everything that went wrong with DNS, redirect rules, and CNAME metadata before it worked."
tags: ["vibecoding", "cloudflare", "workers", "kv", "dns", "javascript"]
aliases: ["/writing/vibecoding-025-url-shortener/"]
weight: -25
---

I've been pasting long blog post URLs into my Mastodon bio, notes, and slide decks for months. The obvious fix was a URL shortener. The less obvious part was how much Cloudflare's routing layers can fight each other when you're building one.

**Linktree:** [mr-dinesh-links.pages.dev](https://mr-dinesh-links.pages.dev) · **Short links:** [short.mrdee.in](https://short.mrdee.in) · **Admin:** [go-admin-76o.pages.dev](https://go-admin-76o.pages.dev)

## What it does

A slug like `short.mrdee.in/vc1` hits a Cloudflare Worker, does a KV lookup, and returns a `301` to the destination URL. That's it. The interesting parts are everything around it.

The admin UI is a single HTML file deployed to Cloudflare Pages. Password authentication via `Authorization: Bearer` header checked against a Worker secret. List all slugs, add new ones, delete existing ones — all against a JSON API served by the same Worker.

The linktree (`short.mrdee.in/links`) is a static page deployed to Cloudflare Pages. It groups all 37 short links into three sections — live tools, blog & notes, and all 24 vibecoding posts — so there's one URL to share that maps the whole project.

## Architecture

| Layer | Tech |
|---|---|
| Redirect logic + API | Cloudflare Worker |
| Slug storage | Cloudflare KV |
| Admin UI | Cloudflare Pages (single HTML file) |
| Linktree | Cloudflare Pages (single HTML file) |
| Auth | `ADMIN_PASSWORD` Worker secret |

The Worker handles four routes:

- `GET /<slug>` — KV lookup → `301` redirect or branded `404` HTML
- `GET /api/links` — list all slugs (auth required)
- `POST /api/links` — create/overwrite a slug with `{slug, url}` (auth required)
- `DELETE /api/links/<slug>` — remove a slug (auth required)

Slug sanitisation strips everything outside `[a-z0-9_-]` on write. Destinations without a scheme get `https://` prepended automatically.

## The DNS rabbit hole

Getting `short.mrdee.in` to invoke the Worker was not straightforward.

The initial domain was `go.mrdee.in`. Every request returned a `301` back to itself. `wrangler tail` showed zero Worker invocations — the request never reached the Worker. Something upstream was swallowing it.

The culprit was a Cloudflare Redirect Rule in the zone settings, set to apply to **all** incoming requests:

```
wildcard_replace(http.request.full_uri, "http://*", "https://${1}")
```

The intent was HTTP → HTTPS. The bug: `http://*` doesn't match `https://...`, so `wildcard_replace` returns the original URL unchanged, and Cloudflare issues a `301` to the same HTTPS URL. A self-redirect loop for every single request, before the Worker ever fires.

Redirect Rules fire before Workers in Cloudflare's processing pipeline. Deleting the rule fixed the loop immediately.

## Why `go.mrdee.in` stayed broken

Even after fixing the redirect rule, `go.mrdee.in` was stuck. The DNS A records for it were Pages-managed and locked — created when an earlier project used `*.mrdee.in` as a wildcard custom domain. Locked records can't be edited or deleted through the dashboard or API.

The cleanest fix was to move to a new subdomain: `short.mrdee.in`. A Workers Custom Domain on `short.mrdee.in` created the right `AAAA 100::` DNS record (Cloudflare's null-routing record, carrying internal worker routing metadata in `meta.origin_worker_id`) and the Worker started receiving traffic.

## Restoring the blog

During cleanup, the `mrdee.in` apex temporarily lost its DNS records. Pages custom domains at the apex use a `AAAA 100::` record with internal routing metadata — not the usual kind you'd hand-edit. When we manually created the record, we got an empty `meta: {}` which Cloudflare's routing layer doesn't know how to handle:

```json
{ "type": "AAAA", "content": "100::", "meta": {} }
```

The fix: delete the bare record, delete the stale Pages domain entry, then let Pages re-add the domain itself — which creates the `AAAA 100::` with the correct routing metadata populated. For the apex, Pages also needs a `CNAME mrdee.in → curl-notes-blog.pages.dev` to pass its own domain verification check (Cloudflare flattens it at the edge for external queries). Once both were in place, the domain went `active` within 30 seconds.

## One `wrangler kv` note

KV is exactly the right storage for this — slug lookups are read-heavy, values are small, and eventual consistency on writes is fine for a personal shortener. The only limitation worth knowing: `wrangler kv key list` returns all keys but not values, so populating the admin UI requires a `GET` per key on first load. Fine at 37 slugs, would need rethinking at thousands.

## Slugs

All 37 short links are at `short.mrdee.in/<slug>`. The linktree at `short.mrdee.in/links` has the full list grouped and labelled. The admin UI at [go-admin-76o.pages.dev](https://go-admin-76o.pages.dev) lets me add or remove slugs without touching the code.

The ones I actually use most: `short.mrdee.in/blog` for the vibecoding series, `short.mrdee.in/argus` and `short.mrdee.in/juicesec` in talks, and `short.mrdee.in/now` in the Mastodon bio.
