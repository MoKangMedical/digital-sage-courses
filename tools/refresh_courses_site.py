from __future__ import annotations

import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ROOT_INDEX = BASE_DIR / "index.html"
ROOT_CSS = "assets/course-theme.css"
SUB_CSS = "../assets/course-theme.css"

STYLE_RE = re.compile(r"<style>.*?</style>", re.S | re.I)
BODY_RE = re.compile(r"<body(?:\s+class=\"[^\"]*\")?>", re.I)
ROOT_NAV_RE = re.compile(r"<nav>.*?</nav>", re.S | re.I)
PERSON_BACK_RE = re.compile(r'<a href="[^"]*" class="back-link">.*?</a>', re.S)
LESSON_BACK_RE = re.compile(r'<a href="\.\/" class="back-link">', re.I)
THEME_LINK_RE = re.compile(r'<link rel="stylesheet" href="[^"]*course-theme\.css">', re.I)


def _replace_style_block(html: str, href: str) -> str:
    link = f'<link rel="stylesheet" href="{href}">'
    if THEME_LINK_RE.search(html):
        html = THEME_LINK_RE.sub(link, html, count=1)
        html = STYLE_RE.sub("", html, count=1)
        return html
    return STYLE_RE.sub(link, html, count=1)


def _replace_body_class(html: str, body_class: str) -> str:
    return BODY_RE.sub(f'<body class="{body_class}">', html, count=1)


def _rewrite_root_index() -> None:
    html = ROOT_INDEX.read_text(encoding="utf-8")
    html = _replace_style_block(html, ROOT_CSS)
    html = _replace_body_class(html, "catalog-page")
    html = ROOT_NAV_RE.sub(
        (
            '<nav>'
            '<a href="https://www.digitalsage.cloud/">主站首页</a>'
            '<a href="./index.html" class="active">思想课程</a>'
            '<a href="https://www.digitalsage.cloud/3d.html">3D 殿堂</a>'
            "</nav>"
        ),
        html,
        count=1,
    )
    ROOT_INDEX.write_text(html, encoding="utf-8")


def _rewrite_thinker_index(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = _replace_style_block(html, SUB_CSS)
    html = _replace_body_class(html, "thinker-page")
    html = PERSON_BACK_RE.sub(
        '<a href="../index.html" class="back-link">← 返回课程总目录</a>',
        html,
        count=1,
    )
    path.write_text(html, encoding="utf-8")


def _rewrite_lesson_page(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = _replace_style_block(html, SUB_CSS)
    html = _replace_body_class(html, "lesson-page")
    html = LESSON_BACK_RE.sub('<a href="./index.html" class="back-link">', html, count=1)
    path.write_text(html, encoding="utf-8")


def _cleanup_macos_artifacts() -> int:
    removed = 0
    for path in BASE_DIR.rglob("*"):
        if path.is_file() and (path.name == ".DS_Store" or path.name.startswith("._")):
            path.unlink()
            removed += 1
    return removed


def main() -> None:
    removed = _cleanup_macos_artifacts()
    _rewrite_root_index()

    thinker_indexes = sorted(path for path in BASE_DIR.glob("*/index.html"))
    lesson_pages = sorted(
        path
        for path in BASE_DIR.glob("*/*.html")
        if path.name != "index.html"
    )

    for path in thinker_indexes:
        _rewrite_thinker_index(path)

    for path in lesson_pages:
        _rewrite_lesson_page(path)

    print(
        f"Refreshed {1 + len(thinker_indexes) + len(lesson_pages)} HTML files "
        f"and removed {removed} macOS artifact files."
    )


if __name__ == "__main__":
    main()
