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

## todos
```
src/models.rs:182  # TODO: ! Get existing model SQLs from the DB and only drop/create if changed
```

## src

### src/api.rs
```
pub async fn execute_sql2(sql: String) → anyhow::Result<SqlResultSet>
pub async fn execute_sql_params(req: SQLAndParams) → anyhow::Result<SqlResultSet>
```

### src/impl_rusqulite.rs
```
pub async fn sql_query(sql: SQLAndParams) → anyhow::Result<SqlResultSet>
```

### src/lib.rs
```
pub async fn install_opfs_sahpool() → anyhow::Result<()>
pub async fn install_relaxed_idb() → anyhow::Result<()>
```

### src/models.rs
```
pub struct ModelColumnImpl
pub trait ModelGroup
pub trait ModelDef
pub trait ModelSerial
pub trait DbTypeMapping
impl i64
impl String
impl f64
impl Vec
impl Option
pub async fn run_migrate_tables(groups: impl Iterator<Item = Arc<dyn ModelGroup>>,) → anyhow::Result<()>
```

### src/types.rs
```
pub struct SQLAndParams
pub struct SqlResultSet
pub struct SqlResultRow
pub enum DbValueType
pub enum DbValue
impl DbValueType
  pub fn to_sql_str(&self) → &'static str
impl DbValue
  pub fn fold_option(value: Option<DbValue>) → DbValue
impl TryFrom
impl String
impl i64
impl f64
impl Vec
```
