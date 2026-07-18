"""Stage base class: the interface every harness stage implements, plus shared
rendering for the per-stage config screen (/stages/<slug>).

A stage is a named, ordered pipeline step (Explore, Plan, …) with:
- ``parts``: the model-driven pieces of the stage, each with a prompt template
  in ``prompt_templates/<slug>/`` and a configurable model (harness/<slug>.json);
- ``start(task_id)``: kick the stage's background work (idempotent);
- ``render_section`` / ``render_status``: the task-page section and its htmx
  polling fragment.

HTML helpers (_esc, _format_time, _render_base) live in app.py; we import the
module (never names) so the app↔stages import cycle stays safe — attribute
access only ever happens at request time, after both modules are loaded.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from crack_server import models as models_mod
from crack_server import paths
from crack_server import app as _ui


@dataclass(frozen=True)
class Part:
    key: str            # "agent", "gate", "summary", "draft", "final", …
    label: str
    template: str       # template basename within the stage's template dir
    default_model: str


class Stage:
    slug: str = ""
    name: str = ""
    order: int = 0      # parsed from the sNN_ filename by the registry
    parts: list[Part] = []

    # -- config (harness/<slug>.json = {"models": {part_key: model_id}}) ------

    def part(self, part_key: str) -> Part:
        for p in self.parts:
            if p.key == part_key:
                return p
        raise KeyError(f"unknown part {part_key!r} for stage {self.slug!r}")

    def model_for(self, part_key: str) -> str:
        """Configured model override, else the Part's default_model."""
        part = self.part(part_key)
        config = paths.read_stage_config(self.slug)
        override = config.get("models", {}).get(part_key)
        return override or part.default_model

    def set_model(self, part_key: str, model_id: str) -> None:
        self.part(part_key)  # validate the part exists
        config = paths.read_stage_config(self.slug)
        config.setdefault("models", {})[part_key] = model_id
        paths.write_stage_config(self.slug, config)

    # -- templates / source ---------------------------------------------------

    def template_dir(self) -> Path:
        return paths.stage_templates_dir(self.slug)

    def source_path(self) -> Path:
        return Path(__file__).resolve().parent / f"s{self.order:02d}_{self.slug}.py"

    def load_template(self, name: str) -> str:
        """Read a template from the stage's template dir fresh on every call."""
        path = self.template_dir() / Path(name).name
        if not path.is_file():
            raise RuntimeError(f"missing prompt template: {path}")
        return path.read_text(encoding="utf-8")

    # -- task-page interface (implemented by subclasses) ----------------------

    def start(self, task_id: str) -> None:
        raise NotImplementedError

    def render_section(self, task_id: str) -> str:
        raise NotImplementedError

    def render_status(self, task_id: str) -> str:
        raise NotImplementedError

    # -- config screen (/stages/<slug>) ----------------------------------------

    def render_part_row(self, part: Part) -> str:
        """One config row: part label, its template, and a model <select> that
        saves on change (target: the row itself, outerHTML)."""
        esc = _ui._esc
        current = self.model_for(part.key)
        options = models_mod.get_models()
        if current not in options:
            options = [current] + options
        opts = "".join(
            f'<option value="{esc(m)}"{" selected" if m == current else ""}>{esc(m)}</option>'
            for m in options
        )
        return f"""
        <div class="part-row">
          <span class="part-label">{esc(part.label)}</span>
          <code>{esc(part.template)}</code>
          <select name="model" hx-post="/api/stages/{esc(self.slug)}/parts/{esc(part.key)}/model"
                  hx-trigger="change" hx-target="closest .part-row" hx-swap="outerHTML">
            {opts}
          </select>
        </div>
        """

    def render_template_row(self, filename: str, editing: bool = False) -> str:
        """Prompt-row style view/edit toggle for one of the stage's templates."""
        esc = _ui._esc
        content = paths.read_stage_template(self.slug, filename)  # raises FileNotFoundError
        stat = (self.template_dir() / filename).stat()
        size = stat.st_size
        mtime = _ui._format_time(stat.st_mtime)

        safe_slug = esc(self.slug)
        safe_name = esc(filename)
        safe_content = esc(content)

        if editing:
            return f"""
            <article class="prompt-row">
              <form hx-put="/api/stages/{safe_slug}/templates/{safe_name}" hx-target="closest article" hx-swap="outerHTML">
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;">
                  <label style="flex: 1;">Filename <input type="text" value="{safe_name}" readonly></label>
                  <small style="color: #666;">{size} bytes • {mtime}</small>
                </div>
                <label>Content
                  <textarea name="content" rows="12" required>{safe_content}</textarea>
                </label>
                <div class="actions">
                  <button type="submit">Save</button>
                  <button type="button" hx-get="/stages/{safe_slug}/template-row/{safe_name}" hx-target="closest article" hx-swap="outerHTML" class="secondary">Cancel</button>
                </div>
              </form>
            </article>
            """

        return f"""
        <article class="prompt-row">
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;">
            <span class="name">{safe_name}</span>
            <small style="color: #666;">{size} bytes • {mtime}</small>
          </div>
          <textarea readonly rows="4">{safe_content}</textarea>
          <div class="actions">
            <button hx-get="/stages/{safe_slug}/template-row/{safe_name}?editing=true" hx-target="closest article" hx-swap="outerHTML">Edit</button>
          </div>
        </article>
        """

    def render_config_body(self) -> str:
        """Body of the /stages/<slug> page: part model dropdowns, editable
        templates, and the stage's .py source (read-only)."""
        esc = _ui._esc
        part_rows = "".join(self.render_part_row(p) for p in self.parts)

        template_rows = []
        for t in paths.list_stage_templates(self.slug):
            try:
                template_rows.append(self.render_template_row(str(t["name"])))
            except FileNotFoundError:
                continue

        try:
            source = self.source_path().read_text(encoding="utf-8")
        except OSError as e:
            source = f"(could not read source: {e})"

        return f"""
        <header style="margin-bottom: 1.5rem;">
          <h1>Stage: {esc(self.name)}</h1>
          <p style="color: #666; margin: 0;">
            slug <code>{esc(self.slug)}</code> • order {self.order} •
            config <code>harness/{esc(self.slug)}.json</code>
          </p>
          <p><a href="/">← All tasks</a></p>
        </header>

        <section>
          <h2>Parts &amp; models</h2>
          {part_rows}
        </section>

        <section>
          <h2>Prompt templates</h2>
          {"".join(template_rows)}
        </section>

        <section>
          <h2>Source <small style="color: #666;">(read-only)</small></h2>
          <pre class="stage-source">{esc(source)}</pre>
        </section>
        """
