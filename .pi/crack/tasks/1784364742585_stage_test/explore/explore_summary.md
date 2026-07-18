## Overview  

The HTML for a task page is built entirely in Python within **`src/crack_server/app.py`**.  
The `task_page` function (lines **451‑482**) constructs the full page response and
includes a small footer fragment that can be used to display a server‑name note.
All dynamic sections (prompts, title, explore status, etc.) are rendered as
separate HTML fragments that are swapped in by htmx, so adding a footer only
requires updating the markup returned from this function.

Static assets such as CSS and JavaScript are served from the **`static/`**
directory under the server package. The relevant stylesheet is
**`src/crack_server/static/app.css`**; its first eight lines define classes
used for layout components, including the class that styles the footer note.
Because the server loads these files directly from the `static/` folder,
any change to the CSS (or addition of a new stylesheet) will be reflected
immediately in the rendered task page without a rebuild.

### Where to edit  

- **Task‑page HTML** – modify the `task_page` function in `src/crack_server/app.py`
  to inject the desired footer markup (e.g., a `<footer>` element with the
  server name).  
- **Static assets** – adjust `src/crack_server/static/app.css` (or add new
  static files) and reference them in the HTML fragment returned by
  `task_page` or its sub‑templates.

## File references  

- `src/crack_server/app.py:451-482`  
- `src/crack_server/static/app.css:1-8`