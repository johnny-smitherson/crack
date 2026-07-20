# storage_crackhouse

SQLite storage layer for the workspace, built on `rusqlite` natively and on
`sqlite-wasm-rs`/`sqlite-wasm-vfs` in the browser. Key pieces:

- `types` — wire types shared by both platforms: `DbValue`/`DbValueType`
  (a serde-friendly mirror of `rusqlite::types::Value`), `SQLAndParams`,
  `SqlResultSet`/`SqlResultRow`.
- `impl_rusqulite::sql_query` — runs a `SQLAndParams` against the single
  process-wide `CONN` (a `lazy_static` `Mutex<Result<Connection>>`) and
  collects the result into a `SqlResultSet`.
- `models` — `declare_model_group!` generates `ModelDef`/`ModelSerial` impls
  (table name, columns, PKs) for plain structs, plus
  `sql_for_insert_row_or_ignore` / `sql_for_upsert_row` / `sql_for_delete_row`
  and `run_migrate_tables` (drop + recreate; no incremental migration yet).
- `api` — exposes `execute_sql2`/`execute_sql_params` as an
  `api_asscrack` `declare_api_group2!`/`implement_api_group2!` group
  (`StorageCrackhouseApiGroup`), so a worker can run SQL over the typed RPC
  framework instead of linking rusqlite directly.
- `install_opfs_sahpool` / `install_relaxed_idb` (wasm-only) — register the
  two available wasm SQLite VFS backends before any connection is opened.

## Gotchas

- **The wasm VFS must be installed before the first query.** `CONN` is a
  `lazy_static`, so it opens its `Connection` lazily on first use. On wasm,
  `impl_rusqulite::_new_connection` always opens
  `file:/assets/scripts/post3.db?vfs=opfs-sahpool` — call
  `install_opfs_sahpool()` first (see `web_serviceworker_crackslave`'s worker
  init) or every query on `CONN` fails.
- **`install_opfs_sahpool`'s SAH-pool VFS needs `createSyncAccessHandle`**,
  which browsers only grant on a cross-origin-isolated page (COOP/COEP
  headers). The plain `wasm-pack test` harness does not serve those headers,
  so the wasm test here exercises `install_relaxed_idb` (IndexedDB-backed,
  no isolation required) directly against a `rusqlite::Connection` instead —
  it does not go through `CONN`/`sql_query`, which are hard-wired to the
  SAH-pool VFS.
- `run_migrate_tables` always drops and recreates every table (see the
  `TODO` in `models.rs`); it is not an incremental migration.

## Tests

`./test.sh` runs `cargo test` (native, against a real file-backed
`post3.db`) and `wasm-pack test --headless --firefox --chrome` (OPFS/IndexedDB
are browser-only APIs; `--node` cannot exercise them). One smoke test per
module: `types` (serde round-trips, already existed), `impl_rusqulite` and
`api` (a literal `SELECT` through `sql_query`/`execute_sql2`, native-only —
both hit the same shared `CONN`), `models` (the pre-existing native
`test_migrate`, now gated `not(target_arch = "wasm32")`), plus a wasm-only
`install_relaxed_idb` + `rusqlite::Connection` smoke test in `lib.rs`.
