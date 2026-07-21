The game is in folder `crack_demo/demo_resolution_selector_web_bevy`.

Base rust packages are under `rust_pkg`. 

Data/asset generation and pre-procesing is in `_data`.

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

## deps
```
.pi/crack/server/src/crack_server/pi_proc.py ← __future__, crack_server, shlex
```

## todos
```
rust_pkg/storage_crackhouse/src/models.rs:202  # TODO: ! Get existing model SQLs from the DB and only drop/create if changed
rust_pkg/api_asscrack/src/crack_worker/api_worker.rs:50  # TODO: get which is missing...
```

## .pi

### .pi/crack/server/src/crack_server/pi_proc.py
```
class PiError(RuntimeError)  :78-88
  def __init__(message: str, detail: str, over_budget: bool) → None
class PiStopped(RuntimeError)  :91-93
class _TurnAccumulator  :505-548
  def __init__() → None
  def apply(event: dict) → None
class _StreamSink  :551-597
  def __init__(p: _HopParams) → None
  def persist(turn: dict) → None
class _HopParams(NamedTuple)  :794-816
async def arun_pi_text(prompt: str, log_prefix: str, model: str, max_input_chars: int | None, record_prompt, pid_file: Path | None, stop_check: Callable[[], bool] | None, image_paths: list[Path] | None, record_error) → tuple[str, float]  :269-278
def run_pi_text(*args, **kwargs) → tuple[str, float]  :392-396  # Sync wrapper over :func:`arun_pi_text` for thread-based call
def kill_pid_file(pid_file: Path) → bool  :451-502  # Kill the process group named in ``pid_file`` (written by aru
async def arun_agent_hop(*, log_prefix: str, model: str, session_id: str, sessions_dir: Path, tools: str | None, message: str, start: float, sentinel: str | None, timeout_seconds: int, persist_turn, hop: int, pid_file: Path | None, stop_check, record_prompt, record_error, error_budget: Callable[[], int] | None, env_extra: dict[str, str] | None, waiting_check: Callable[[], bool] | None, append_system_prompt: str | None, swap_after_edit: bool, todo_already: bool) → str  :1183-1205
def run_agent_hop(**kwargs) → str  :1280-1284  # Sync wrapper over :func:`arun_agent_hop` for thread-based ca
```

## rust_pkg

### rust_pkg/net_crackpipe/src/chat/chat_ticket.rs
```
pub struct ChatTicket
impl ChatTicket
  pub fn new_str_bs(topic_id: &str, bs: BTreeSet<NodeId>) → Self
```

### rust_pkg/net_crackpipe/src/echo.rs
```
pub struct Echo
impl Echo
  pub fn new(own_endpoint_node_id: NodeId, sleep_manager: SleepManager) → Self
impl Echo
impl Echo
```

### rust_pkg/net_crackpipe/src/lib.rs
```
pub fn timestamp_micros() → u128
pub fn datetime_now() → DateTime<Utc>
```

### rust_pkg/net_crackpipe/src/signed_message.rs
```
pub struct SignedMessage
pub struct MessageSigner
pub struct WireMessage
pub struct ReceivedMessage
pub enum ChatMessage
pub trait AcceptableType
pub trait IChatRoomType
impl SignedMessage
  pub fn verify_and_decode(bytes: &[u8]) → Result<WireMessage<T>>
impl MessageSigner
  pub fn sign_and_encode(&self, message: T,) → Result<(Vec<u8>, WireMessag...
```

### rust_pkg/net_crackpipe/src/sleep.rs
```
pub struct SleepManager
impl SleepManager
  pub fn new() → Self
  pub async fn sleep(&self, duration: Duration)
  pub fn wake_up(&self)
impl SleepManagerInner
```

### rust_pkg/net_crackpipe/src/user_identity.rs
```
pub struct UserIdentity
pub struct UserIdentitySecrets
pub struct NodeIdentity
impl UserIdentity
  pub fn nickname(&self) → String
  pub fn user_id(&self) → &PublicKey
  pub fn html_color(&self) → String
  pub fn rgb_color(&self) → (u8, u8, u8)
impl UserIdentitySecrets
impl UserIdentitySecrets
  pub fn user_identity(&self) → &UserIdentity
  pub fn secret_key(&self) → &SecretKey
  pub fn generate() → Self
impl NodeIdentity
  pub fn nickname(&self) → String
  pub fn html_color(&self) → String
  pub fn rgb_color(&self) → (u8, u8, u8)
  pub fn user_id(&self) → &PublicKey
  pub fn node_id(&self) → &PublicKey
  pub fn user_identity(&self) → &UserIdentity
  pub fn bootstrap_idx(&self) → Option<u32>
  pub fn new(user_identity: UserIdentity, node_id: PublicKey, bootstrap_idx: Option<u32>,) → Self
```

### rust_pkg/storage_crackhouse/src/api.rs
```
pub async fn execute_sql2(sql: String) → anyhow::Result<SqlResultSet>
pub async fn execute_sql_params(req: SQLAndParams) → anyhow::Result<SqlResultSet>
```

### rust_pkg/storage_crackhouse/src/impl_rusqulite.rs
```
pub async fn sql_query(sql: SQLAndParams) → anyhow::Result<SqlResultSet>
```

### rust_pkg/storage_crackhouse/src/lib.rs
```
pub async fn install_opfs_sahpool() → anyhow::Result<()>
pub async fn install_relaxed_idb() → anyhow::Result<()>
```

### rust_pkg/storage_crackhouse/src/models.rs
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

### rust_pkg/storage_crackhouse/src/types.rs
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

### rust_pkg/web_serviceworker_crackslave/src/lib.rs
```
pub async fn _js_init_dedicated_worker() → Result<(), JsValue>
pub async fn _js_compute_payload_reply(msg: JsValue) → Result<JsValue, JsValue>
pub async fn web_worker_registration(mapping: Arc<ApiImplMapping>,) → std::result::Result<(), JsV...
```

### rust_pkg/web_serviceworker_crackloader/src/lib.rs
```
pub struct WebWorkerFactory
impl WebWorkerFactory
```

### rust_pkg/api_asscrack/src/api/api_client.rs
```
pub struct ApiClient
pub struct MessageLater
impl ApiClient
  pub fn new(pipe: WorkerPipe) → Self
  pub async fn call(&self, arg: T::Arg) → anyhow::Result<T::Ret>
```

### rust_pkg/api_asscrack/src/api/api_method_macros.rs
```
pub struct ApiGroupDeclStatic
pub struct ApiMethodInfo
pub struct ApiMethodImpl
pub trait ApiGroupDecl
pub trait ApiGroupMethods
pub trait ApiGroupImpls
pub trait ApiMethodDecl
impl ApiMethodImpl
  pub fn fullname(&self) → String
impl ApiMethodInfo
  pub fn fullname(&self) → String
```

### rust_pkg/api_asscrack/src/api/api_worker_declarations.rs
```
pub async fn worker_ping(_x: () → anyhow::Result<()>
```

### rust_pkg/api_asscrack/src/crack_worker/api_worker.rs
```
pub struct ApiImplMapping
pub fn make_api_mapping(groups: Vec<Arc<dyn ApiGroupImpls>>) → Arc<ApiImplMapping>
pub async fn compute_response_message(_request: WorkerMessage, mapping: Arc<ApiImplMapping>,) → WorkerMessage
```

### rust_pkg/api_asscrack/src/crack_worker/mod.rs
```
pub struct WorkerPipe
pub struct WorkerMessage
pub trait WorkerLoaderFactory
```

### rust_pkg/thread_crackworker/src/lib.rs
```
pub struct ThreadWorkerFactory
impl ThreadWorkerFactory
```

### rust_pkg/_crack_utils/src/lib.rs
```
pub fn get_timestamp_now_ms() → i64
pub fn spawn(f: F) → n0_future::task::JoinHandle...
pub fn random_u32() → u32
pub async fn sleep_ms(dt_ms: u32)
```
