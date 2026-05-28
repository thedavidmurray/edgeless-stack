---

name: soul-extraction
description: >
  Builds a SOUL.md persona and voice profile from a person's public social
  profiles (X/Twitter, Instagram, TikTok, LinkedIn, YouTube). Gathers public
  profile + post data, then synthesizes how they write, what they care about,
  and who they engage with -- every trait tied to a cited post.
metadata:
  tags: [soul, persona, voice, profiling, social-media, osint, research]
  tier: task-specific
  domain: knowledge
when_to_apply: >
  When the user gives one or more social handles/URLs and asks to build a
  soul.md, extract someone's voice/persona, or profile a creator.
---
# Soul Extraction

Turn a person's **public** social presence into a single `SOUL.md` -- a grounded
persona and voice profile. It **gathers and synthesizes**; it does not
impersonate. Every trait is tied to evidence (specific posts/profile fields), and
it works from public data only.

## Procedure

1. **Resolve handles.** Given one handle/name, optionally run `maigret <username>`
   to find matching accounts across platforms. Confirm matches with the user --
   same username does not mean same person.
2. **Gather public data.** For each platform, pull the profile (bio, links,
   counts) and a recent sample of posts/captions (plus video transcripts where
   available). The simplest source is the ScrapeCreators API (one key,
   `SCRAPECREATORS_API_KEY`, `curl` with an `x-api-key` header):
   ```bash
   curl -s -G "https://api.scrapecreators.com/v1/twitter/profile" \
     -H "x-api-key: $SCRAPECREATORS_API_KEY" --data-urlencode "handle=jack"
   ```
   Record dates and permalinks for everything you pull.
3. **Synthesize the SOUL.md** (structure below). Write each section from the
   evidence -- quote representative posts and cite source/date. Separate what is
   **well-grounded** (stated plainly, repeatedly) from what is **inferred**.
4. **Write the file** to the requested path (default `./SOUL.md`) and report the
   sources used plus confidence caveats.

## SOUL.md structure

```markdown
# {Name} (@{handle})
## Snapshot          -- one paragraph: who they are, where they're active
## Voice & Tone      -- sentence length, register, humor, emoji, signature
                        phrases; each backed by a quoted example + date
## Themes & Interests-- recurring topics, roughly by frequency
## Values & Worldview-- stances, marked stated vs inferred
## Communication Style-- formats they favor, how they engage their audience
## Audience & Relationships -- who they talk to/about, collaborators
## Do / Don't        -- guidance for writing as them
## Sources           -- profiles + posts used, with dates/permalinks
## Confidence & Caveats -- well-grounded vs inferred; sample size; recency
```

## Grounding rules (do not skip)

- **Cite or cut.** No trait without a supporting post/profile field -- otherwise
  label it inference or drop it. Never fabricate quotes, stats, or biography.
- **Voice != truth.** You model how they *present*, not facts about them. Keep
  claims hedged and sourced.
- **Recency matters.** Prefer recent posts for voice; flag thin/stale samples.

## Pitfalls

- ScrapeCreators charges credits per call -- sample posts, don't exhaustively
  paginate unless asked.
- Handles are not identities; verify cross-platform matches before merging.
- Private/gated accounts return little -- say so rather than inventing.
- This profiles real people from public data. Use it for collaborators,
  creators, and public figures with a legitimate reason; get consent beyond
  public-figure research, and respect each platform's terms of service.
