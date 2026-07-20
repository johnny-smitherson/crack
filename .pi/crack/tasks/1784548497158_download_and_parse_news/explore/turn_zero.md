Q: What files currently exist in the `_data/news/` directory, and is there already a `main.py` or any Python scripts there?
A: The `_data/news/` directory likely contains `news-links.txt` (the input file with URLs) and possibly a `main.py` or other Python scripts. There may also be a `data_cache/` directory for storing downloaded HTML files, or it may need to be created.

Q: Does the `news-links.txt` file have one URL per line, and are there any comments, empty lines, or other formatting we need to handle?
A: The `news-links.txt` file probably contains one URL per line, possibly with some empty lines or whitespace. We'll need to strip each line and skip empty lines and duplicates.

Q: Is there any existing HTML parsing logic in the codebase we can reuse, or do we need to write our own heading/subtitle extraction from scratch using only standard library?
A: Since the requirement says "use subprocess so we don't pull any dependencies", we likely need to use only Python standard library (like `html.parser` or regex) for HTML parsing, not BeautifulSoup or lxml.

Q: What is the expected format of the `news_reports.md` output file - one entry per link with heading and subtitle?
A: The `news_reports.md` should probably contain a markdown report with each source URL, the extracted heading (e.g., `<h1>` or first heading), and subtitle (e.g., `<h2>`, meta description, or first paragraph).

Q: How should we compute the `<link_hash>` for the cache filename - MD5, SHA256, or something else?
A: A reasonable approach would be to use a hash like MD5 or SHA256 of the URL (or normalized URL) to create a deterministic, filesystem-safe cache filename like `data_cache/<hash>.html`.

Q: Should the script handle download failures gracefully (timeouts, 404s, non-HTML content) and continue processing other links?
A: Yes, the script should likely catch subprocess errors from wget, log failures, and continue with remaining links rather than stopping entirely.

Q: Is there a `pyproject.toml` or `uv` configuration in `_data/news/` that defines how `uv run main.py` works?
A: There may be a `pyproject.toml` in `_data/news/` that defines the project and entry points for `uv run`, or it may rely on a parent directory's configuration.