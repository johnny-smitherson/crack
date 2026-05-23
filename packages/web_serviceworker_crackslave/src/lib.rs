mod register_web_worker;

use std::sync::Arc;

use api_asscrack::{api::api_worker_declarations::*, crack_worker::api_worker::make_api_mapping};
use wasm_bindgen::prelude::*;

// Called when the wasm module is instantiated
#[wasm_bindgen(start)]
fn init_worker() -> std::result::Result<(), JsValue> {
    // unsafe {
    //     __wasm_call_ctors();
    // }

    use tracing::Level;

    dioxus_logger::init(Level::INFO).expect("logger failed to init");
    tracing::info!("tracing...");
    use dioxus_logger::tracing;

    tracing::debug!("{:?}", WorkerPing);

    register_web_worker::do_worker_registration(make_api_mapping(vec![
        Arc::new(WorkerApiGroup2),
    ]))?;

    tracing::info!("init_worker() finished! WORKER IS RUNNING!!!");

    Ok(())
}

// unsafe extern "C" {
//     fn __wasm_call_ctors();
// }
