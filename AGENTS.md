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
.pi/crack/server/tests/test_error_rows.py ← __future__, crack_server
.pi/crack/server/tests/test_model_latency.py ← __future__, crack_server, pytest
.pi/crack/server/tests/test_model_switch.py ← __future__, crack_server, tests
.pi/crack/server/tests/test_render_ui.py ← __future__, crack_server
.pi/crack/server/tests/test_stop_durable.py ← __future__, crack_server, tests, pytest
.pi/crack/server/tests/test_trajectory_view.py ← __future__, crack_server, pytest
.pi/crack/server/tests/test_vision_media.py ← __future__, fastapi, starlette, crack_server, tests
```

## changes (last 5 commits — 21 minutes ago)
```
.pi/crack/server/tests/test_error_rows.py     +test_render_error_stop_row_includes_duration  +test_errored_chat_emits_stopped_error_line  ~test_render_fatal_error_banner
.pi/crack/server/tests/test_model_latency.py  +latency_root  +test_record_latency_first_value_is_clamped  +test_record_latency_ema_and_clamp  +test_latencies_tolerates_missing_and_corrupt
.pi/crack/server/tests/test_model_switch.py   ~test_reason_note_shown_for_notable_reasons
.pi/crack/server/tests/test_render_ui.py      +test_text_row_renders_markdown_clamp_and_collapse  +test_think_row_uses_same_clamped_markdown  +test_time_column_on_first_row_only  ~test_render_actions_table_has_colgroup
.pi/crack/server/tests/test_trajectory_view.py +test_merge_exchange_sidecars_duration_falls_back_to_turn_span  ~test_merge_exchange_sidecars_appends_terminal_reason
.pi/crack/server/tests/test_vision_media.py   ~test_render_exchanges_shows_prompt_thumbs_from_exchange_media  ~test_chat_post_message_stashes_media_onto_the_exchange
```

## .pi

### .pi/crack/server/tests/test_error_rows.py
```
def test_error_recorder_appends_timestamped_rows_and_counts(tmp_path)  :27-39
def test_error_recorder_subpath_targets_nested_exchange(tmp_path)  :42-47
def test_grant_error_budget_extends_by_max_and_keeps_rows()  :50-59
def test_make_turn_stamps_at()  :62-64
def test_render_turn_msgs_interleaves_errors_by_timestamp()  :72-86
def test_render_turn_msgs_legacy_turns_keep_list_order()  :89-101
def test_render_turn_msgs_without_errors_is_unchanged()  :104-106
def test_render_error_row_shows_attempt_detail_and_time()  :109-118
def test_render_fatal_error_banner()  :121-133
def test_render_error_stop_row_includes_duration()  :136-139
def test_errored_chat_emits_stopped_error_line(tmp_path, monkeypatch)  :142-168  # Errored chats (phase idle + error set) show the red runtime 
```

### .pi/crack/server/tests/test_model_latency.py
```
def latency_root(tmp_path, monkeypatch)  :14-16
async def test_record_latency_first_value_is_clamped(latency_root)  :20-22
async def test_record_latency_ema_and_clamp(latency_root)  :26-36
def test_latencies_tolerates_missing_and_corrupt(latency_root)  :39-44
async def test_concurrent_record_latency_does_not_corrupt(latency_root)  :48-59
async def test_flush_latencies_no_double_count_across_per_hop_persisters(latency_root, tmp_path)  :63-64  # The sub-agent path builds a fresh TurnPersister each hop (ex
async def test_flush_latencies_ignores_compiled_prompt_entries(latency_root, tmp_path)  :87-103  # Compiled-prompt entries (carry ``template``) sit in the turn
```

### .pi/crack/server/tests/test_model_switch.py
```
def test_make_turn_records_model_when_set()  :27-29
def test_make_turn_omits_model_when_empty()  :32-34
def test_persister_stamps_current_model(tmp_path)  :37-46
def test_persister_stamp_reason_on_last_turn(tmp_path)  :49-58
def test_persister_stamp_reason_noop_when_empty(tmp_path)  :61-66
def test_reason_note_shown_for_notable_reasons()  :69-74
def test_terminal_reason_row_labels()  :77-84
def test_prep_timing_row_shows_elapsed()  :87-93
def test_model_tag_shown_per_turn()  :105-110
def test_prewalk_swap_divider_after_todo()  :113-121
def test_user_switch_divider_without_todo()  :124-128
def test_no_divider_when_model_stable()  :131-134
def test_model_state_threads_across_calls()  :137-144
def test_tool_output_short_has_no_expand_toggle()  :152-155
def test_tool_output_long_has_single_icon_toggle()  :158-163
def test_plan_chat_form_editor_before_first_message(chat_root)  :175-182
def test_plan_chat_form_locked_before_graduation(chat_root)  :185-191
def test_plan_chat_form_dropdown_after_graduation(chat_root)  :194-204
def test_nonplan_chat_form_has_dropdown(chat_root)  :207-212
def test_run_display_model_uses_planner_while_planning()  :220-225
def test_run_display_model_uses_implementer_after_swap()  :228-237
def test_chat_display_model_planning_then_graduated()  :240-248
def test_graduation_gate_matches_prewalk_swap()  :251-259
def test_post_message_locks_config_on_first_message(chat_root)  :262-275
def test_dirty_git_gate_preserves_plan_config(chat_root, monkeypatch)  :278-294
def test_config_editor_emits_config_hidden_field()  :297-304
def test_nonplan_model_resolution_ignores_implementer_until_graduated()  :307-324  # Plan 24 Issue 4: implementer_model must not shadow the locke
def test_chat_display_model_prefers_cached(chat_root)  :327-331
def test_image_models_filters_to_image_capable(chat_root)  :339-347
def test_image_models_fallback_when_no_info(chat_root)  :350-356
```

### .pi/crack/server/tests/test_render_ui.py
```
def test_render_actions_table_has_colgroup()  :11-18
def test_text_row_renders_markdown_clamp_and_collapse()  :21-32
def test_think_row_uses_same_clamped_markdown()  :35-40
def test_time_column_on_first_row_only()  :43-55
def test_spawn_coder_row_pretty_renders()  :58-68
def test_todo_row_renders_markdown()  :71-78
def test_session_usage_estimates_for_cursor_driver(tmp_path, monkeypatch)  :109-118
def test_session_usage_exact_when_input_reported(tmp_path)  :121-147
def test_session_usage_caches_unchanged_session(tmp_path, monkeypatch)  :150-188
def test_render_context_line_cursor_estimated_no_dollar(tmp_path, monkeypatch)  :191-209
def test_render_context_line_shows_cost_when_nonzero(tmp_path, monkeypatch)  :212-243
```

### .pi/crack/server/tests/test_stop_durable.py
```
def noop_enqueue(monkeypatch)  :13-14
def test_stop_chat_sets_stop_requested(chat_root, monkeypatch)  :17-20
def test_stop_chat_stamps_terminal_reason_and_clears_phase(chat_root, monkeypatch)  :23-38
def test_pop_pending_drains_queue_while_stopped(chat_root)  :41-53
def test_enqueue_system_message_preserves_stop(chat_root, noop_enqueue)  :56-62
def test_merge_child_inbox_preserves_stop(chat_root, noop_enqueue)  :65-84
def test_post_message_clears_stop(chat_root, noop_enqueue)  :87-91
def test_answer_chat_question_clears_stop(chat_root, noop_enqueue)  :94-102
async def test_exchange_finish_preserves_stop_requested(chat_root)  :106-132
def test_subagent_stop_does_not_clear_parent_stop(chat_root, fake_pi, monkeypatch)  :135-153
def test_subagent_retry_clears_only_run_stop(chat_root, fake_pi, monkeypatch)  :156-181
```

### .pi/crack/server/tests/test_trajectory_view.py
```
def test_project_unknown_event_has_expand_row(tmp_path: Path)  :13-45
def test_project_merges_tool_results(tmp_path: Path)  :48-80
def test_ansi_to_html_preserves_colour()  :83-88
def test_merge_exchange_sidecars_interleaves_errors_by_time()  :91-139  # Errors with ``at`` between turn timestamps appear in order, 
def test_merge_exchange_sidecars_appends_terminal_reason()  :142-168
def test_merge_exchange_sidecars_duration_falls_back_to_turn_span()  :171-183
def test_host_worktree_dirty_detects_untracked(tmp_path: Path)  :186-196
```

### .pi/crack/server/tests/test_vision_media.py
```
def root(tmp_path, monkeypatch)  :36-38
def test_run_pi_text_image_args(fake_pi)  :70-82
def test_run_pi_text_no_image_args_unchanged(fake_pi)  :85-89
async def test_vision_analyze_rejects_missing_and_invalid(root)  :98-118
async def test_vision_analyze_happy_path(root, monkeypatch)  :122-130
async def test_vision_analyze_resolves_relative_paths(root, monkeypatch)  :134-142
def test_chat_media_route(root)  :151-157
def test_run_media_route(root)  :160-170
def test_persister_attaches_media_only_for_valid_images(root)  :178-208
def test_persister_without_media_dir_leaves_blocks_alone(root)  :211-216
def test_add_attachment_validates_and_describes(root, monkeypatch)  :224-240
async def test_attachment_upload_route(root, monkeypatch)  :244-273
def test_format_block_shape()  :276-290
def test_chat_post_message_weaves_then_clears(root)  :294-310
def test_chat_post_message_stashes_media_onto_the_exchange(root)  :318-334
def test_render_user_prompt_msg_renders_media_thumbs()  :337-351
def test_prompt_recorder_attaches_media_list_and_callable(tmp_path)  :354-372
```
