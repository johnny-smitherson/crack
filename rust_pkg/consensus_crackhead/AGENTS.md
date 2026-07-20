# consensus_crackhead

**Placeholder crate.** `src/lib.rs` is empty apart from the test module —
no public API yet; consensus logic will land here later. Tests: `./test.sh`
runs native `cargo test` plus `wasm-pack test --node` (a single dual-target
link smoke test). See `README.md` for details.

## Auto-generated signatures
<!-- Updated by gen-context.js -->
# Code signatures

## SigMap commands

| When | Command |
|------|---------|
| Before answering a question about code | `sigmap ask "<your question>"` |
| To rank files by topic | `sigmap --query "<topic>"` |
| After changing config or source dirs | `sigmap validate` |
| To verify an AI answer is grounded | `sigmap judge --response <file>` |

Always run `sigmap ask` (or `sigmap --query`) before searching for files relevant to a task.
