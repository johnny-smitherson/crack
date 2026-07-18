"""Stage s02: Plan — agent-driven clarifying Q&A, then a structured final plan.

Step-driven state machine persisted to tasks/<id>/plan.json (no long-lived
blocking threads): each "Submit answers" POST kicks the next background step.

Phases: draft_running → awaiting_answers → resuming → (more rounds) →
final_running → done | error. Rounds are agent-driven, hard-capped at
MAX_ROUNDS: after each answered round the draft agent emits either ≤5 more
questions (a fenced ```questions JSON block) or the READY_TO_PLAN sentinel.
"""

from __future__ import annotations

import json
import logging
import re
import shutil
import threading
import time

from crack_server import paths, pi_runner
from crack_server.stages.base import Part, Stage
from crack_server import app as _ui

logger = logging.getLogger("uvicorn.error")

ULTRA_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"

MAX_ROUNDS = 3
MAX_QUESTIONS_PER_ROUND = 5
READY_SENTINEL = "READY_TO_PLAN"
READ_ONLY_REMINDER = (
    "Remember: DO NOT write or edit any files yet. "
    "This is a read-only exploration and planning phase."
)
DRAFT_TURNS_PER_STEP = 10
DRAFT_MAX_HOPS_PER_STEP = 3
DRAFT_MAX_TURNS = 30
DRAFT_TIMEOUT_SECONDS = 300

RUNNING_PHASES = ("draft_running", "resuming", "final_running")

_QUESTIONS_BLOCK_RE = re.compile(r"```questions\s*\n(.*?)```", re.DOTALL)
_QUESTION_TYPES = ("single", "multiple", "open")


def _esc(text: str) -> str:
    return _ui._esc(text)


def _parse_questions(text: str) -> list[dict]:
    """Extract and validate the last fenced ```questions JSON block (≤5 items).

    Each question must be {id, text, type: single|multiple|open, options?[]}.
    Invalid blocks/questions are dropped; returns [] when nothing valid remains."""
    matches = _QUESTIONS_BLOCK_RE.findall(text)
    if not matches:
        return []
    try:
        raw = json.loads(matches[-1])
    except json.JSONDecodeError:
        logger.warning("plan: questions block is not valid JSON")
        return []
    if not isinstance(raw, list):
        return []

    questions: list[dict] = []
    for item in raw[:MAX_QUESTIONS_PER_ROUND]:
        if not isinstance(item, dict):
            continue
        qid = str(item.get("id", "")).strip()
        qtext = str(item.get("text", "")).strip()
        qtype = str(item.get("type", "")).strip()
        if not qid or not qtext or qtype not in _QUESTION_TYPES:
            continue
        question: dict = {"id": qid, "text": qtext, "type": qtype}
        if qtype in ("single", "multiple"):
            options = item.get("options")
            if not isinstance(options, list) or not options:
                continue
            question["options"] = [str(o) for o in options]
        questions.append(question)
    return questions


def _strip_control_blocks(text: str) -> str:
    """Remove questions blocks and the READY_TO_PLAN sentinel — what remains is
    the draft's prose ("lay of the land")."""
    text = _QUESTIONS_BLOCK_RE.sub("", text)
    text = text.replace(READY_SENTINEL, "")
    return text.strip()


def _format_qa(round_entry: dict) -> str:
    """Render one round's questions + answers as Q:/A: pairs for prompts."""
    lines = []
    answers = round_entry.get("answers", {})
    for q in round_entry.get("questions", []):
        answer = answers.get(q["id"], "")
        if isinstance(answer, list):
            answer = ", ".join(str(a) for a in answer)
        lines.append(f"Q: {q['text']}\nA: {answer or '(no answer)'}")
    return "\n\n".join(lines)


class S02Plan(Stage):
    slug = "plan"
    name = "Plan"
    parts = [
        Part("draft", "Draft agent (Q&A rounds)", "draft.md", ULTRA_MODEL),
        Part("final", "Final plan (single-shot)", "final_plan.md", ULTRA_MODEL),
    ]

    # -- lifecycle ------------------------------------------------------------

    def start(self, task_id: str) -> None:
        """(Re)start the plan draft. Idempotent while any phase is running."""
        state = paths.read_plan_state(task_id)
        if state.get("phase") in RUNNING_PHASES:
            return

        content = paths.read_all_prompts_joined(task_id)
        if not content:
            paths.write_plan_state(
                task_id, {"phase": "error", "error": "no prompt files to plan from"}
            )
            return

        explore_summary = paths.read_explore_state(task_id).get("summary_md", "")

        # Clear stale draft sessions so a fresh run chains from a clean slate.
        shutil.rmtree(paths.plan_sessions_dir(task_id), ignore_errors=True)

        paths.write_plan_state(
            task_id,
            {
                "phase": "draft_running",
                "round": 1,
                "rounds": [],
                "lay_of_the_land": "",
                "final_md": "",
                "error": "",
                "explore_summary": explore_summary,
                "started_at": time.time(),
                "finished_at": None,
            },
        )
        threading.Thread(target=self._run_draft_step, args=(task_id, True), daemon=True).start()

    def submit_answers(self, task_id: str, form) -> None:
        """Record the current round's answers and kick the resume step.

        ``form`` is a starlette FormData; question ids are the field names."""
        state = paths.read_plan_state(task_id)
        if state.get("phase") != "awaiting_answers" or not state.get("rounds"):
            return

        rnd = int(state.get("round", 1))
        current = state["rounds"][-1]
        answers: dict = {}
        for q in current.get("questions", []):
            values = [str(v) for v in form.getlist(q["id"]) if str(v).strip()]
            if q.get("type") == "multiple":
                answers[q["id"]] = values
            else:
                answers[q["id"]] = values[0] if values else ""
        current["answers"] = answers
        paths.write_plan_artefact(
            task_id, f"round_{rnd}_answers.json", json.dumps(answers, indent=2)
        )

        state["round"] = rnd + 1
        state["phase"] = "resuming"
        paths.write_plan_state(task_id, state)
        threading.Thread(target=self._run_draft_step, args=(task_id, False), daemon=True).start()

    # -- background steps -------------------------------------------------------

    def _run_draft_step(self, task_id: str, initial: bool) -> None:
        """One draft step: the initial draft prompt, or a follow-up carrying the
        latest round's answered Q&A. Resumes the same pi session across steps."""
        start = time.monotonic()
        try:
            state = paths.read_plan_state(task_id)
            rnd = int(state.get("round", 1))

            if initial:
                message = (
                    self.load_template("draft.md")
                    .replace("{content}", paths.read_all_prompts_joined(task_id))
                    .replace(
                        "{explore_summary}",
                        state.get("explore_summary") or "(no exploration summary available)",
                    )
                )
            else:
                qa = _format_qa(state["rounds"][-1])
                message = self.load_template("draft_followup.md").replace("{qa}", qa)

            turns: list[dict] = []

            def persist(current_turn: dict, hop: int) -> None:
                turns.append(
                    {
                        "hop": hop,
                        "text": current_turn.get("text", ""),
                        "thinking": current_turn.get("thinking", ""),
                        "tool_blocks": list(current_turn.get("tool_blocks", [])),
                    }
                )

            reason = "hop_cap"
            hop = 0
            while reason == "hop_cap" and hop < DRAFT_MAX_HOPS_PER_STEP:
                hop += 1
                reason = pi_runner.run_agent_hop(
                    log_prefix=f"plan-draft-r{rnd}",
                    model=self.model_for("draft"),
                    session_id=f"plan-{task_id}",
                    sessions_dir=paths.plan_sessions_dir(task_id),
                    tools="bash,read",
                    message=message,
                    start=start,
                    sentinel=None,
                    turns_per_hop=DRAFT_TURNS_PER_STEP,
                    max_turns=DRAFT_MAX_TURNS,
                    timeout_seconds=DRAFT_TIMEOUT_SECONDS,
                    total_turns=len(turns),
                    persist_turn=persist,
                    hop=hop,
                )
                logger.info(
                    "plan: draft step round=%d hop=%d finished reason=%s", rnd, hop, reason
                )
                if reason != "hop_cap":
                    break
                # The agent spent the whole hop on tool calls; resume the session with
                # a wrap-up instruction so it actually emits text (lay of the land +
                # questions block / READY_TO_PLAN) instead of being cut off mid-sweep.
                message = (
                    "Stop calling tools now. Based on what you have gathered so far, "
                    "write your Lay of the land, then emit either the ```questions "
                    f"JSON block (at most {MAX_QUESTIONS_PER_ROUND} questions) or "
                    f"{READY_SENTINEL} on its own line."
                )

            text = "\n\n".join(t["text"] for t in turns if t.get("text")).strip()
            if not text:
                raise RuntimeError("plan draft step produced no text")

            questions = _parse_questions(text)
            lay = _strip_control_blocks(text)

            state = paths.read_plan_state(task_id)
            if lay:
                state["lay_of_the_land"] = lay
                paths.write_plan_artefact(task_id, "draft.md", lay)

            if READY_SENTINEL in text or rnd >= MAX_ROUNDS or not questions:
                if not questions and READY_SENTINEL not in text and rnd < MAX_ROUNDS:
                    logger.warning(
                        "plan: no questions block and no sentinel in round %d; going to final",
                        rnd,
                    )
                state["phase"] = "final_running"
                paths.write_plan_state(task_id, state)
                self._run_final(task_id)
                return

            state.setdefault("rounds", []).append({"questions": questions, "answers": {}})
            state["phase"] = "awaiting_answers"
            paths.write_plan_state(task_id, state)
            paths.write_plan_artefact(
                task_id, f"round_{rnd}_questions.json", json.dumps(questions, indent=2)
            )
            logger.info("plan: round %d produced %d questions", rnd, len(questions))
        except Exception as e:
            logger.exception("plan draft step failed for %s", task_id)
            state = paths.read_plan_state(task_id)
            state["phase"] = "error"
            state["error"] = str(e)
            state["finished_at"] = time.time()
            paths.write_plan_state(task_id, state)

    def _run_final(self, task_id: str) -> None:
        """Fresh, tool-less single-shot call that writes the final plan markdown."""
        try:
            state = paths.read_plan_state(task_id)
            qa_all = "\n\n".join(
                f"Round {i}:\n{_format_qa(r)}"
                for i, r in enumerate(state.get("rounds", []), 1)
            )
            prompt = (
                self.load_template("final_plan.md")
                .replace("{content}", paths.read_all_prompts_joined(task_id))
                .replace(
                    "{explore_summary}",
                    state.get("explore_summary") or "(no exploration summary available)",
                )
                .replace("{lay_of_the_land}", state.get("lay_of_the_land") or "(none)")
                .replace("{qa}", qa_all or "(no clarifying Q&A — the draft agent had enough)")
            )
            final_md = pi_runner.run_pi_text(
                prompt,
                log_prefix="plan-final",
                model=self.model_for("final"),
            )
            # The template mandates this closing line; enforce it server-side so the
            # artefact always carries the read-only-phase reminder.
            if "DO NOT write or edit any files" not in final_md:
                final_md = final_md.rstrip() + "\n\n" + READ_ONLY_REMINDER + "\n"
            paths.write_plan_artefact(task_id, "final_plan.md", final_md)

            state = paths.read_plan_state(task_id)
            state["final_md"] = final_md
            state["phase"] = "done"
            state["finished_at"] = time.time()
            paths.write_plan_state(task_id, state)
            logger.info("plan: done for %s (%d chars)", task_id, len(final_md))
        except Exception as e:
            logger.exception("plan final failed for %s", task_id)
            state = paths.read_plan_state(task_id)
            state["phase"] = "error"
            state["error"] = str(e)
            state["finished_at"] = time.time()
            paths.write_plan_state(task_id, state)

    # -- rendering --------------------------------------------------------------

    def render_section(self, task_id: str) -> str:
        return (
            '<section class="plan" id="plan-section">\n'
            "  <h2>Plan</h2>\n"
            f"  {self.render_status(task_id)}\n"
            "</section>"
        )

    def render_status(self, task_id: str) -> str:
        """Render the Plan section content (the polling wrapper is `#plan-content`).

        Dispatches on phase: running → busy poller; awaiting_answers → the
        questions form (no polling — waiting on the human); done → rendered final
        plan; error → message. Idle/done/error get a (Re-)plan button."""
        safe_id = _esc(task_id)
        state = paths.read_plan_state(task_id)
        phase = state.get("phase", "idle")
        rnd = int(state.get("round", 1))
        lay = state.get("lay_of_the_land", "")

        polling_attrs = (
            ' hx-trigger="every 1.5s" hx-get="/tasks/{id}/plan-status" hx-swap="outerHTML"'.format(
                id=safe_id
            )
            if phase in RUNNING_PHASES
            else ""
        )

        parts = [f'<div id="plan-content" class="plan-content"{polling_attrs}>']

        if phase == "draft_running":
            parts.append('<p aria-busy="true">Drafting plan… round 1</p>')
        elif phase == "resuming":
            parts.append(f'<p aria-busy="true">Drafting plan… round {rnd}</p>')
        elif phase == "final_running":
            parts.append('<p aria-busy="true">Writing final plan…</p>')
        elif phase == "error":
            parts.append(f'<p style="color: #c44;">Error: {_esc(state.get("error", ""))}</p>')
        elif phase == "awaiting_answers":
            parts.append(self._render_questions_form(task_id, state))
        elif phase == "done":
            finished_at = state.get("finished_at")
            meta = f"planned {_ui._format_ago(finished_at)}" if finished_at else "planned"
            rounds = len(state.get("rounds", []))
            meta += f" · {rounds} Q&A round{'s' if rounds != 1 else ''}"
            parts.append(f'<p class="plan-meta"><small>{meta}</small></p>')
            final_md = state.get("final_md", "")
            if final_md:
                parts.append(f'<div class="plan-final">{_ui._render_markdown(final_md)}</div>')
            parts.append(
                f'<p><small style="color: #666;">On disk: <code>tasks/{safe_id}/plan/final_plan.md</code></small></p>'
            )

        if phase == "awaiting_answers" and lay:
            parts.append(
                '<details class="plan-draft"><summary>Lay of the land (draft)</summary>'
                f'<div class="turn-text">{_esc(lay)}</div></details>'
            )

        if phase in ("idle", "done", "error"):
            label = "Re-plan" if phase in ("done", "error") else "Plan"
            parts.append(
                f'<button hx-post="/api/tasks/{safe_id}/plan" '
                f'hx-target="#plan-content" hx-swap="outerHTML">{label}</button>'
            )

        parts.append("</div>")
        return "".join(parts)

    def _render_questions_form(self, task_id: str, state: dict) -> str:
        """The Q&A form for the current round: radios (single), checkboxes
        (multiple), textareas (open). Submits per-question-id form fields."""
        safe_id = _esc(task_id)
        rnd = int(state.get("round", 1))
        questions = state.get("rounds", [{}])[-1].get("questions", [])

        fields = []
        for q in questions:
            qid = str(q["id"])
            safe_qid = _esc(qid)
            qtype = q.get("type")
            if qtype in ("single", "multiple"):
                input_type = "radio" if qtype == "single" else "checkbox"
                required = " required" if qtype == "single" else ""
                options = "".join(
                    f'<label class="plan-option">'
                    f'<input type="{input_type}" name="{safe_qid}" value="{_esc(str(o))}"{required}> {_esc(str(o))}'
                    f"</label>"
                    for o in q.get("options", [])
                )
                control = f'<div class="plan-options">{options}</div>'
            else:  # open
                control = f'<textarea name="{safe_qid}" rows="2"></textarea>'
            fields.append(
                f'<fieldset class="plan-question">'
                f"<legend>{_esc(str(q['text']))}</legend>"
                f"{control}</fieldset>"
            )

        return f"""
        <form class="plan-questions" hx-post="/api/tasks/{safe_id}/plan/answers"
              hx-target="#plan-content" hx-swap="outerHTML">
          <p class="plan-meta"><small>Round {rnd}/{MAX_ROUNDS} — the planner needs clarification:</small></p>
          {"".join(fields)}
          <button type="submit">Submit answers</button>
        </form>
        """


STAGE = S02Plan()
