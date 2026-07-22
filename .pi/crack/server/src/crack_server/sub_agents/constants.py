"""Sub-agent package constants (leaf module — no internal imports)."""

SUBAGENT_JOB_SLUG = "__subagent__"
MAX_DEPTH = 1
MAX_PARALLEL_SUBAGENTS = 3  # max concurrently-running children per parent (main agent)
SUBAGENT_TIMEOUT_SECONDS = 3600
# Grace before a running phase with no queued job is flagged orphaned.
ORPHAN_PHASE_GRACE_SECONDS = 10.0
