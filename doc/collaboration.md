# Team Collaboration & Infrastructure Plan

**Status:** v0.1 proposal (2026-08-19) — for review, nothing deployed yet.
**Scope:** How a 5–10 person team communicates, tracks work, and hands work over on this
project. The documentation standard itself is a separate document:
[documentation_standard.md](documentation_standard.md).

**Assumptions this plan is built on** (correct them and the recommendations change):

| Assumption | Value |
| --- | --- |
| Team size | 5–10, distributed, part-time |
| Canonical repo & CI | GitHub `Landflier/LinHT-rfic` — stays canonical |
| Hosting available | Home server / self-managed box, residential connection |
| Domain | `landflier.com`, subdomains free to allocate |
| Hard deadline | Chipalooza tapeout 2026-11-09 (≈11 weeks) — infrastructure must not eat design time |
| Project nature | Open source (Apache-2.0 WITH SHL-2.1), non-commercial |

---

## 0. Decisions at a glance

| Need | Recommendation | Where it runs | Effort |
| --- | --- | --- | --- |
| Chat, per-block discussion, async troubleshooting | **Zulip** (self-hosted) | `colab.landflier.com` on the home server | ~4 h setup, ~1 h/month |
| Bi-weekly calls | **Hosted Jitsi** (`meet.jit.si`) launched from the Zulip topic | nothing to run | 0 |
| Task/progress tracking | **GitHub Issues + Projects** on the existing repo | github.com | ~3 h configuration |
| Public documentation site | **Quarto → GitHub Pages** (`docs.landflier.com`) | GitHub CI | see doc standard |
| Access control / join–leave | **GitHub organisation membership** as the single identity anchor; Zulip logs in via GitHub OAuth | — | ~1 h |
| Exposure of the home server | **Cloudflare Tunnel** (no forwarded ports) + **Tailscale** for admin/SSH | home server | ~2 h |
| Large binaries (measurement data, datasheets) | Git LFS on the existing repo; Nextcloud only if that proves insufficient | — | defer |

**The one recommendation that contradicts the original request:** do *not* self-host the task
tracker (JIRA/Plane/OpenProject). Reasoning in §2. If the argument does not convince you, §2.3
gives the concrete self-hosted answer instead — this is a preference, not a blocker.

**The second thing to cut:** self-hosted video conferencing. 26 calls a year does not justify
running an SFU/TURN stack on a residential uplink (§1.4).

---

## 1. Chat and calls

### 1.1 What the tool actually has to do

Derived from the requirement "track chats for different parts of the IC, troubleshoot issues":

1. **One conversation per problem, not one firehose per block.** Analog debugging threads run
   for days ("CP current mismatch across corners") while five other threads run in parallel in
   the same block. Flat channels (Slack/Mattermost/Discord/Matrix) mix them.
2. **Searchable, permanent history.** This is the onboarding/offboarding requirement. A new
   person must be able to read *why* the loop filter is what it is without asking anyone.
   → Immediately disqualifies Slack free (90-day history) and, in practice, Discord (search is
   poor, no threading discipline, and it is not self-hostable).
3. **Circuit-shaped content:** LaTeX math, code blocks, drag-and-drop waveform screenshots.
4. **Low admin burden**, because the admin is also the lead designer.

### 1.2 Recommendation: Zulip

Zulip's model is **channel → topic**: a channel per subsystem, a *named topic* per problem
inside it. That maps one-to-one onto "different parts of the IC", and it is the reason to pick
it over the Slack-shaped alternatives.

Concretely, what onboarding looks like with it: a new person joining the PLL work opens
`#pll_top`, sees a list of ~30 topic titles, and reads the three that concern the charge pump.
With a flat channel they would scroll a year of interleaved messages instead.

Other properties that matter here:

- LaTeX (`$$...$$`) and syntax-highlighted code render natively — usable for design discussion.
- Native GitHub integration: pushes, PRs, issues and CI failures post into a `#github` channel,
  each PR getting its own topic. Chat and repo stay in one timeline.
- Self-hostable via the official `zulip/docker-zulip` compose stack; ~2 vCPU / 4 GB RAM.
- **Mobile push notifications** for self-hosted servers go through Zulip's push service:
  free for ≤10 users, and the free *Community plan* covers larger non-commercial/open-source
  organisations — this project qualifies; register at setup time.
  ([self-hosted billing](https://zulip.com/help/self-hosted-billing),
  [push service docs](https://zulip.readthedocs.io/en/10.3/production/mobile-push-notifications.html))
- Backup is a documented one-liner (`zulip-backup`), which matters because this database becomes
  the project's institutional memory.

### 1.3 Alternatives, and why they lose here

| Option | Verdict |
| --- | --- |
| **Mattermost** (self-hosted) | Closest runner-up. Slack-like, mature, and it bundles calls + screen sharing (unlimited participants per docs, ~50 recommended) — which would remove the Jitsi dependency. But channels are flat with bolt-on threads, so the "one thread per block issue" discipline has to be enforced socially, and calls need the separate `rtcd` service plus an open UDP port — exactly the exposure we are trying to avoid on a home connection. Pick this only if the team already knows Slack and refuses topics. ([calls deployment](https://docs.mattermost.com/administration-guide/configure/calls-deployment.html)) |
| **Matrix (Synapse) + Element** | Federation and E2EE are irrelevant to this use case, and both actively hurt: E2EE breaks server-side search, which is the whole onboarding argument. Highest operational burden of the three. |
| **Slack (free)** | 90-day history. Deletes exactly the artifact we need. Not self-hosted. |
| **Discord** | Not self-hosted, weak search, no data ownership; fine for a public user community, wrong for engineering records. |
| **Nextcloud Talk** | Chat is an afterthought around a file-sync product. |
| **GitHub Discussions** | Zero infrastructure and it already exists — a legitimate minimal answer if you want to run *nothing*. Loses real-time presence and mobile immediacy; too slow for live debugging. Worth keeping in mind as the fallback if the home server turns into a burden. |

### 1.4 Calls

**Do not self-host video.** Bi-weekly means ~26 calls per year; an SFU + TURN stack is a
continuous maintenance and upstream-bandwidth commitment on a residential line for that.

- Use **`meet.jit.si`** (free, no accounts, works from a browser). Zulip has a built-in video-call
  button that generates and posts a Jitsi link into the current topic.
- Google Meet / Whereby are equally acceptable; the choice is not load-bearing.
- Revisit only if a real requirement appears (recording policy, confidentiality of unpublished
  tapeout material).

### 1.5 Meeting ritual (this is where onboarding actually lives)

The tool matters less than the ritual. Proposed:

1. A permanent Zulip channel `#meetings` with one topic per call: `2026-09-02 sync`.
2. Agenda is posted in that topic ≥24 h before; anyone can append items.
3. **Minutes are committed to the repo**, not left in chat: `doc/meetings/2026-09-02.md`
   (attendees, decisions, action items with owner + issue link). Ten lines is enough.
4. Every *decision* that changes the design becomes an ADR under `doc/adr/` in the same week
   (see the documentation standard, §4). Chat is never the record of truth.
5. Every *action item* becomes a GitHub issue with an assignee before the call ends.

Rule of thumb to state explicitly to the team: **if it is not in git, it did not happen.**

### 1.6 Proposed channel layout

| Channel | Purpose |
| --- | --- |
| `#general` | Announcements, scheduling, non-technical |
| `#meetings` | One topic per call: agenda → notes → link to committed minutes |
| `#pll_top` | Chipalooza PLL (CMOS5L): VCO, MASH, CP, PFD, MMD — one topic per issue |
| `#rx-chain` | LNA, mixers, TIA/LPF, PGA, RX ΣΔ ADC |
| `#tx-chain` | TX filter, FIR-DAC, digital ΣΔ, drivers |
| `#digital` | RTL, SPI/I2S, LibreLane flow, cocotb |
| `#flow-and-tools` | Container, PDK, xschem/ngspice/VACASK/KLayout breakage — the "why does my tool not work" channel |
| `#layout-and-signoff` | Floorplan, DRC/LVS/PEX, padframe |
| `#github` | Automated: pushes, PRs, issues, CI results |
| `#random` | Keeps the rest clean |

Convention: topic names are **problem statements**, not categories — `cp: 12 % Iup/Idn mismatch
at ss/-40 °C`, not `charge pump`. Resolved topics get ✔ prefixed so the channel list doubles as
a solved-problems index.

---

## 2. Task and progress tracking

### 2.1 Recommendation: GitHub Issues + Projects, not a self-hosted tracker

Given that GitHub stays canonical for code, CI and reviews, putting the tracker elsewhere buys
one thing (self-hosting) and costs several:

- Issues lose their automatic link to PRs, commits, branches and CI status. `Fixes #42` stops
  working; someone has to maintain the mapping by hand, and within two months nobody does.
- Two accounts per person instead of one — directly against the join/leave requirement.
- One more service on the home server whose downtime blocks the team.
- GitHub Projects is free and unlimited for public repositories, with board/table/roadmap views,
  custom fields and issue automation. Feature-wise it is not the limitation.

The honest framing: with a tapeout ~11 weeks out, **every self-hosted service is maintenance
stolen from the PLL**. Self-hosting the chat has a concrete payoff (permanent, searchable,
owned project memory that Slack would delete). Self-hosting the tracker has no payoff that
GitHub does not already provide, because the code is on GitHub anyway.

### 2.2 What to actually configure (the real work)

Tool choice is 10 % of this; the taxonomy is the other 90 %.

**Labels**
- `macro:pll_top`, `macro:rx_adc`, `macro:tx_dac`, … — one per macro, matching directory names
- `stage:spec`, `stage:sizing`, `stage:schematic`, `stage:sim`, `stage:layout`, `stage:signoff`, `stage:docs`
- `type:bug`, `type:task`, `type:decision`, `type:doc`
- `blocked`, `good-first-task`, `needs-owner`

**Issue templates** (`.github/ISSUE_TEMPLATE/`)
- *Block bring-up* — pre-filled checklist mirroring the exit criteria in the doc standard:
  specs written → sizing report committed → schematic → testbenches → CACE green → doc page →
  layout → DRC/LVS → PEX re-sim.
- *Bug / spec miss* — what was measured, at which corner, which testbench reproduces it,
  which figure shows it.
- *Decision request* — becomes an ADR when resolved (options, constraints, deadline).

**Project board fields:** Owner, Macro, Stage, Target milestone, Definition-of-Done ✅.

**Milestones** = the tapeout gates already written in `doc/design_plan.md` §11, plus the
Chipalooza date (2026-11-09).

**Definition of Done** — non-negotiable, identical to the doc standard's exit criteria:
> simulated headless + numbers reproduced by a committed script + doc page section filled +
> report regenerated and committed.

An issue with a passing simulation and no doc page is *not* done. This is the mechanism that
makes "documentation is key" actually bind, instead of being a wish.

**Onboarding / offboarding procedure** (write it down once, in `doc/onboarding.md`):
- *Join:* add to GitHub org → automatic Zulip access (§3.3) → assign one `good-first-task` →
  point at `doc/design_plan.md` + the docs site + the macro doc page they are inheriting.
- *Leave:* reassign open issues, change `owner:` in the frontmatter of their macro doc pages,
  remove from the GitHub org (which also removes chat access), and require a **handover note**
  appended to each of their doc pages: current state, what is known broken, what they would do
  next. This is the single highest-value offboarding artifact and it costs 20 minutes.

### 2.3 If you want the tracker self-hosted anyway

Legitimate reasons to override §2.1: teammates who will not create GitHub accounts, or work
that must stay off a US-hosted platform.

| Option | RAM | Notes |
| --- | --- | --- |
| **Plane** | ~4 GB | Closest to JIRA (cycles, modules, sprints), docker-compose, actively developed. Bidirectional GitHub issue sync is a paid/Enterprise feature — verify before relying on it. |
| **Forgejo** | ~0.5 GB | Single binary: git + issues + PRs + wiki + CI. The cheapest self-hosted option by far. Best used as a *full* mirror if you ever decide to leave GitHub, not as an issues-only sidecar. |
| **OpenProject** | ~4 GB | Gantt/work-breakdown, heavier and more corporate than this project needs. |
| **Vikunja / Focalboard** | ~0.3 GB | Lightweight kanban. Fine for personal tracking, too thin for multi-person engineering. |

If you go this route, pick **Plane** for the JIRA feel and accept that PR↔issue linkage becomes
manual, or pick **Forgejo** and plan to eventually make it canonical.

---

## 3. Home-server hosting and security

### 3.1 Never forward a port from the residential connection

Exposing a home IP directly means: your home address-adjacent IP is public, you own DDoS
mitigation, dynamic-IP churn breaks DNS, and one unpatched service is a foothold on the same
LAN as everything personal. Two safe patterns instead:

1. **Cloudflare Tunnel (`cloudflared`)** — the daemon makes an *outbound* connection to
   Cloudflare; no inbound ports, no port-forwarding, home IP never published, free TLS,
   works with a dynamic IP. Requires `landflier.com` DNS to be on Cloudflare.
   Optionally put **Cloudflare Access** in front of admin URLs.
2. **Tailscale / WireGuard** — nothing public at all; the team installs a VPN client. Maximum
   security, but real friction for a casual contributor on a phone.

**Recommended combination:** Cloudflare Tunnel for Zulip (must work in any browser for 5–10
people) + **Tailscale for SSH, the Docker socket, monitoring and backups**. SSH is never
reachable from the internet. Zero forwarded ports on the router.

### 3.2 Host layout

```
router  ──(no forwarded ports)──   home server
                                    ├─ cloudflared        → outbound tunnel to Cloudflare
                                    ├─ caddy (internal)   → routes colab.landflier.com → zulip
                                    ├─ zulip (docker-zulip: app, postgres, redis, rabbitmq, memcached)
                                    ├─ restic (cron)      → off-site repo (Backblaze B2 / rsync.net)
                                    └─ uptime-kuma        → Tailscale-only, alerts to Zulip
```

DNS / subdomain allocation:

| Name | Points to | Public? |
| --- | --- | --- |
| `colab.landflier.com` | Zulip, via Cloudflare Tunnel | yes, login-gated |
| `docs.landflier.com` | GitHub Pages (CNAME) — the generated docs site | yes, public |
| everything else (SSH, monitoring, backups) | Tailscale addresses only | no |

Keeping the docs site on GitHub Pages rather than the home server is deliberate: it is the one
service that must never be down when an external reviewer, a Chipalooza judge, or a prospective
contributor looks at the project, and it costs nothing there.

### 3.3 Identity: make GitHub the single anchor

The join/leave requirement is best solved by having exactly **one** membership list.

- Create a GitHub **organisation** (e.g. `Landflier` → move the repo under it) and add the team.
- Configure Zulip to authenticate via **GitHub OAuth restricted to that organisation**.
- Result: adding someone to the GitHub org grants chat + repo + issues; removing them revokes
  all three. No per-service account cleanup, nothing forgotten.

Do **not** deploy Authentik/Keycloak yet. A dedicated SSO provider pays for itself at 2+
self-hosted apps; with only Zulip self-hosted it is a second service to patch and a second thing
that can lock everyone out. Revisit if a self-hosted tracker or Nextcloud is ever added.

### 3.4 Hardening and operations checklist

- [ ] Server on an isolated VLAN, no reachability to personal machines/NAS shares
- [ ] SSH: keys only, `PasswordAuthentication no`, listening on the Tailscale interface only
- [ ] `unattended-upgrades` for the OS; pinned image tags + a monthly manual `docker compose pull`
- [ ] **Backups: nightly `zulip-backup` → restic → off-site, encrypted.** Automate a *restore*
      test monthly — an untested backup is not a backup. The chat archive is project memory.
- [ ] `uptime-kuma` monitoring `colab.landflier.com`, alerting into Zulip and to e-mail
- [ ] Zulip org set to **invite-only**; new-user default role = Member (not Admin); at least two
      owners so a single lost laptop does not orphan the org
- [ ] Message retention: **unlimited** (deliberately — this is the onboarding archive)
- [ ] UPS on the server, and accept that a home connection means occasional outages; nothing
      release-critical (CI, docs site, git) lives there

### 3.5 Effort estimate

| Item | Setup | Ongoing |
| --- | --- | --- |
| Cloudflare Tunnel + Tailscale | 2 h | ~0 |
| Zulip (docker-compose, OAuth, channels, integrations) | 3–4 h | ~30 min/month |
| Backups + monitoring | 2 h | 15 min/month (restore test) |
| GitHub labels, templates, project board | 3 h | ~0 |
| **Total** | **~1.5 days** | **~1 h/month** |

---

## 4. Documentation

The full specification is in [documentation_standard.md](documentation_standard.md). Summary of
what it proposes, since it is the load-bearing part of this whole plan:

- Standardised, scaffolded doc page per cell, created automatically by
  `make init-macro` / `make init-submodule` — fixed sections, machine-readable frontmatter.
- Numbers are **generated, never typed**: the existing `specs_<cell>.py` + `sizing_<cell>.py` →
  `sizing_<cell>.md` mechanism is extended, not replaced (and no notebooks — see its §1.5).
- Decisions live in ADRs under `doc/adr/`, referenced from the cell pages.
- A Quarto site aggregates all of it into `docs.landflier.com`, including an auto-generated
  **status dashboard** (cell, owner, stage, last update) that doubles as the project's progress
  view.
- A CI **doc gate** fails PRs whose doc pages are missing required sections.

One defect found while surveying the repo, worth fixing this week regardless of everything else:
`tutorial/_quarto.yml` and `.github/workflows/quarto-publish.yml` are inherited verbatim from
the upstream JKU template. `site-url`, `repo-url` and the injected "Edit this page" / "Report an
issue" link rewrites all point at `iic-jku/ihp-sg13g2-ams-chip-template`, so the published site
currently sends any contributor's issue report to a *different project's* tracker.

---

## 5. Open decisions

| # | Decision | Default if unanswered |
| --- | --- | --- |
| C1 | Zulip | Zulip |
| C2 | GitHub Projects as the tracker | GitHub Projects |
| C3 | Move the repo to a GitHub **organisation** (needed for the identity anchor in §3.3) | Yes |
| C4 | Fully public domain  |  Assume fully public |
| C5 | Domain DNS moved to Cloudflare (prerequisite for the tunnel) | Yes |
| C6 | `docs.landflier.com` CNAME to GitHub Pages, or keep the `github.io` URL | CNAME |
| C7 | Who owns which macro — needed before the doc pages can list owners | Vasil owns all until assigned |

---

### Sources

- [Self-hosted Zulip billing](https://zulip.com/help/self-hosted-billing) ·
  [Zulip mobile push notification service](https://zulip.readthedocs.io/en/10.3/production/mobile-push-notifications.html) ·
  [New plans for self-hosted Zulip customers](https://blog.zulip.com/2023/12/15/new-plans-for-self-hosted-customers/)
- [Mattermost Calls self-hosted deployment](https://docs.mattermost.com/administration-guide/configure/calls-deployment.html) ·
  [Mattermost product limits](https://docs.mattermost.com/administration-guide/manage/product-limits.html)
