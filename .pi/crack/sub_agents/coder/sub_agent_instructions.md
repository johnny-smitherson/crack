- You may spawn helper coder sub-agents (`spawn_coder`) when a piece of work is
  large or independent; pass `plan=false` for small mechanical sub-tasks.
- After `spawn_coder`, call `wait_join` to block until the sub-agent(s) finish —
  their reports arrive as the tool result. Waiting is free (no tokens burned).
  NEVER poll report files with bash `sleep` loops.
