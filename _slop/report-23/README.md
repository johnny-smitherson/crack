# report-23 — execution reports for plans-23

Each plan in `_slop/plans-23/<N>_*.md` writes its report here as `<N>_<name>.md` when it runs.
A later, smarter review agent reads these reports **together with the run trajectories**
(under `/crack-harness-data/unscripted_chats/<chat_id>/`) to judge whether each step landed.

Report must cover: files changed + why, exact commands run, the nemotron sample-chat id(s)
and their trajectory paths, what passed, what could not be verified, and what the next plan's
agent must know. Be concrete and honest about gaps.
