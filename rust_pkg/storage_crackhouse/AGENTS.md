SQLite storage: `rusqlite` natively, `sqlite-wasm-rs`/`sqlite-wasm-vfs` on
wasm. `CONN` (in `impl_rusqulite.rs`) is a `lazy_static` that opens its
connection lazily on first use — on wasm it always opens through the
`opfs-sahpool` VFS, so `install_opfs_sahpool()` must run before any query or
every call on `CONN` fails. `install_opfs_sahpool`'s SAH-pool VFS needs
`createSyncAccessHandle`, which requires a cross-origin-isolated page
(COOP/COEP); the plain `wasm-pack test` harness doesn't serve those headers,
so this crate's wasm test exercises `install_relaxed_idb` (IndexedDB-backed,
no isolation needed) directly, bypassing `CONN`. `run_migrate_tables` always
drops + recreates tables (no incremental migration — see the `TODO` at
`models.rs:182`). See `README.md` and `./test.sh`.
