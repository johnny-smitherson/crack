use api_asscrack::declare_api_group2;
use api_asscrack::implement_api_group2;

use crate::types::SQLAndParams;
use crate::types::SqlResultSet;

declare_api_group2! {
    StorageCrackhouseApiGroup,
    [
        (ExecuteSQLParams, SQLAndParams, SqlResultSet),
        (ExecuteSQL2, String, SqlResultSet),
    ]
}

implement_api_group2! {
    StorageCrackhouseApiGroup,
    [
        (ExecuteSQLParams, execute_sql_params),
        (ExecuteSQL2, execute_sql2),
    ]
}

pub async fn execute_sql2(sql: String) -> anyhow::Result<SqlResultSet> {
    crate::impl_rusqulite::sql_query(SQLAndParams {
        sql,
        params: vec![],
    })
    .await
}

pub async fn execute_sql_params(req: SQLAndParams) -> anyhow::Result<SqlResultSet> {
    crate::impl_rusqulite::sql_query(req).await
}
