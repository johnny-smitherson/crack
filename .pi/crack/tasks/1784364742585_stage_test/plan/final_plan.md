# Plan

## Initial build/check instructions

The server runs live in a Docker container at `http://localhost:9847` with auto-reload. No build step is needed — just edit Python files under `src/crack_server/` and changes are picked up in ~1 second.

```bash
# Verify server is responding
curl -s http://localhost:9847/ | head -20

# Verify task page renders
curl -s http://localhost:9847/api/tasks | jq -r '.[0].id' | xargs -I{} curl -s "http://localhost:9847/tasks/{}" | head -30
```

## Problem statement

The crack-pi-server task page (and other pages) currently lack a footer identifying the server. The HTML for all pages is assembled in `src/crack_server/app.py` — the `index()` function (home page), `task_page()` function (task page), and stage config pages all route through a shared `_render_base()` helper that wraps content in a common layout. Static assets (CSS/JS) are served from `src/crack_server/static/`. The goal is to add a small, muted footer note reading "crack-pi-server" at the bottom of every page, inside the `<main>` element, using existing Pico.css small/muted styling patterns already present in the codebase (`<small style="color: #666;">`).

## Changes

### 1. `src/crack_server/app.py` — `_render_base()` function (lines ~752-784)

Add a footer element inside the `<main>` tag, after the content block but before `</main>`.

**Current structure (sketched from signatures):**
```python
def _render_base(title: str, content: str, ...) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
      <head>...</head>
      <body>
        <main class="container">
          {content}
        </main>
      </body>
    </html>
    """
```

**After change:**
```python
def _render_base(title: str, content: str, ...) -> str:
    footer = '<footer style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee;"><small style="color: #666;">crack-pi-server</small></footer>'
    return f"""
    <!DOCTYPE html>
    <html>
      <head>...</head>
      <body>
        <main class="container">
          {content}
          {footer}
        </main>
      </body>
    </html>
    """
```

**Motivation:** `_render_base` is the single layout wrapper used by `index()`, `task_page()`, and stage config pages. Adding the footer here ensures it appears on all pages consistently, inside `<main>` as requested, using the existing muted small-text pattern.

---

### 2. `src/crack_server/static/app.css` — optional enhancement

No CSS change is strictly required since the inline style uses the existing pattern. However, if a reusable class is preferred, add:

```css
/* Add near line 8 */
.page-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
  text-align: center;
}
.page-footer small {
  color: #666;
}
```

Then update `_render_base` to use `<footer class="page-footer"><small>crack-pi-server</small></footer>`.

**Motivation:** Keeps styling maintainable and consistent with the existing `.prompt-row`, `.title-row` pattern in the same file.

---

## What NOT to change

- `src/crack_server/main.py` — server entry point, unrelated
- `src/crack_server/paths.py` — filesystem utilities, unrelated
- Any API route handlers (`api_create_task`, `api_delete_prompt`, etc.) — they return JSON/HTML fragments, not the base layout
- The `task_page()` function itself — it only provides the *content* portion; the footer belongs in the shared wrapper
- Static asset serving configuration — already works from `static/`

---

## Automatic verification

```bash
# 1. Home page has footer
curl -s http://localhost:9847/ | grep -c 'crack-pi-server'

# 2. Task page has footer (create a test task first)
TASK_ID=$(curl -s -X POST http://localhost:9847/api/tasks -d "title=Test Footer" | jq -r .id)
curl -s "http://localhost:9847/tasks/$TASK_ID" | grep -c 'crack-pi-server'

# 3. Stage config page has footer
curl -s http://localhost:9847/stages/plan | grep -c 'crack-pi-server'

# 4. Footer is inside <main> (not outside)
curl -s http://localhost:9847/ | grep -A5 '<main class="container">' | grep -c 'crack-pi-server'

# Cleanup
curl -s -X DELETE "http://localhost:9847/api/tasks/$TASK_ID"
```

All commands should return `1` (found exactly once per page).

---

## Manual verification

1. Open `http://localhost:9847/` in a browser — verify "crack-pi-server" appears at bottom of page, small and muted
2. Open any task page (e.g., `http://localhost:9847/tasks/<id>`) — verify same footer
3. Open stage config page (`http://localhost:9847/stages/plan`) — verify same footer
4. Inspect element — confirm footer is inside `<main class="container">`, not after `</main>`
5. Verify styling matches existing muted text (gray `#666`, small font)

---

## Overview / Summary

**Goal:** Add a consistent "crack-pi-server" footer note to all pages (home, task, stage config).

**Solution:** Modify the shared `_render_base()` function in `src/crack_server/app.py` to inject a `<footer>` element inside `<main>`, using the existing inline `<small style="color: #666;">` pattern. Optionally extract to a CSS class in `src/crack_server/static/app.css`.

**Main risks:** None — this is a pure presentational change to a single layout function. Auto-reload makes iteration instant. No API contracts, data models, or background jobs are affected.

Remember: DO NOT write or edit any files yet. This is a read-only exploration and planning phase.
