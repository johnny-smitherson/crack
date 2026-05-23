
use crate::declare_api_group2;
use crate::implement_api_group2;


declare_api_group2! {
    WorkerApiGroup2,
    [
        (WorkerPing, (), ()),
        (RunSql, String, Vec<String>),
    ]
}

implement_api_group2! {
    WorkerApiGroup2,
    [
        (WorkerPing, worker_ping),
        (RunSql, worker_run_sql),
    ]
}



pub async fn worker_run_sql(_x: String) -> anyhow::Result<Vec<String>> {
    Ok(vec![])
}

pub async fn worker_ping(_x: ()) -> anyhow::Result<()> {
    Ok(())
}