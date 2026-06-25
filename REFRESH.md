# Weekly Refresh Playbook — The Statler Property Dashboard

This file lets **any** Claude Code session (manual or scheduled) update
`statler-dashboard.html` from the latest files in Google Drive. The process is
deterministic so it survives the ephemeral cloud environment and the 7-day cron
limit. To run it, start a session on this repo and say:

> **"Refresh the Statler dashboard"**

## Inputs (Google Drive folder "NWO", id `1U74SNydmBLMxMAp3jExwRugXJdambJj6`)
Pick the **most recent** of each by `modifiedTime`:
1. **CoStar underwriting report** — PDF, title contains `The Statler`.
   → unit-mix grid (page 2), 5 rent comps, asking/effective rents, concessions.
2. **Rent roll** — `.xlsx`, title contains `Statler Rent Roll`.
   → occupancy & leased: read the by-type Occupancy/Vacant **summary totals**
     (the `Total` row: occupied / vacant of 240) and count `NTV` rows for "on notice".
     `% Leased` = active-lease units ÷ total (vacant-but-pre-leased only if the roll
     shows applicant/future-lease data; the standard financial roll does not).
3. **Marketing photo** — image; save into the repo as `statler.jpg`.

## Steps
1. Read the three inputs from Drive (use the Google Drive MCP). If Drive is
   unavailable in a headless run, stop and leave a note — do not guess.
2. Recompute: `% occupied`, `% leased`, on-notice, vacant, unit mix, comps, rents.
3. **Month-over-month rent:** compare this week's avg in-place / asking rent to the
   previous entry in `data/statler-history.json`. If only one snapshot exists, label
   MoM as "baseline — first data point".
4. Update the `DATA` object near the top of the `<script>` in
   `statler-dashboard.html` (the only block that needs editing) and the `asOf` date.
5. Append a new snapshot to `data/statler-history.json` (newest last).
6. Validate the page renders (no JS errors) and unit counts still sum to 240.
7. Commit to branch `claude/adoring-planck-ctcfzo` and push.

## Notes
- Map pin coordinates are approximate (geocoders are blocked in this environment);
  comp **distances** come straight from CoStar.
- Keep the dashboard's "Sources" note accurate to whatever dates you used.
- Live site (once Pages is enabled): repo Settings → Pages → Deploy from branch
  `claude/adoring-planck-ctcfzo`, root → `…github.io/development-model/statler-dashboard.html`.
