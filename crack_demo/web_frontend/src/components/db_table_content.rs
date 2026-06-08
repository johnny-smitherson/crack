use crack::storage_crackhouse::{
    api::{ExecuteSQL2, ExecuteSQLParams},
    types::{DbValue, SQLAndParams},
};
use dioxus::{logger::tracing, prelude::*};

use crate::{
    components::display_table::{DefaultTableRenderer, DisplayTable},
    crack::use_crack,
};

#[component]
pub fn TableContentPane(table: ReadSignal<String>) -> Element {
    let result = use_resource(move || {
        let select_star = format!("SELECT * FROM {} LIMIT 100", table.read().clone());

        let sql = "SELECT name FROM pragma_table_info(?);";
        let param = DbValue::Text(table.read().clone());
        tracing::info!("TableContentPane {param:?}");

        async move {
            let api = use_crack();
            (
                api.call::<ExecuteSQLParams>(SQLAndParams {
                    sql: sql.to_string(),
                    params: vec![param],
                })
                .await,
                api.call::<ExecuteSQL2>(select_star.clone()).await,
            )
        }
    });

    let result = result.read();
    let Some(result) = result.as_ref() else {
        return rsx! {"Loading"};
    };

    let (_r1, r2) = match result {
        (Ok(r1), Ok(r2)) => (r1, r2),
        _ => return rsx! {pre{"Error in TableContentPane!"}},
    };
    let cols: Vec<_> = _r1
        .rows
        .iter()
        .filter_map(|r| {
            if let Some(DbValue::Text(txt)) = r.cols.get(0) {
                Some(txt.to_string())
            } else {
                None
            }
        })
        .collect();
    let mut r2 = r2.clone();
    if r2.column_names.is_empty() {
        r2.column_names = cols;
    }

    rsx! {
        div {
            style: "
                flex-grow: 1;
                height: 100%;
                border: 1px solid red;
            ",
                    DisplayTable::<DefaultTableRenderer> {
                        data: r2.clone(),
                        renderer: DefaultTableRenderer,
                    }

        }
        div {
            style: "
                width: 400px;
                border: 1px solid red;
            ",

            DisplayTable::<DefaultTableRenderer> {
                data: _r1.clone(),
                renderer: DefaultTableRenderer,
            }
        }
    }
}
