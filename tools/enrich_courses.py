from __future__ import annotations

import json
import re
import subprocess
import sys
from html import escape
from pathlib import Path

try:
    from course_reference_library import (
        CURATED_ENGLISH_PROFILES,
        CURATED_PILLAR_GLOSSES,
        PRIORITY_THINKER_IDS,
        REFERENCE_LIBRARY,
    )
except ModuleNotFoundError:
    from tools.course_reference_library import (  # type: ignore
        CURATED_ENGLISH_PROFILES,
        CURATED_PILLAR_GLOSSES,
        PRIORITY_THINKER_IDS,
        REFERENCE_LIBRARY,
    )


BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
CATALOG_PATH = ASSETS_DIR / "course-catalog.json"
ROOT_INDEX = BASE_DIR / "index.html"
MAIN_REPO_DIR = BASE_DIR.parent / "digital-sage"
COURSE_DOCS_DIR = MAIN_REPO_DIR / "docs" / "courses"

if MAIN_REPO_DIR.exists():
    sys.path.insert(0, str(MAIN_REPO_DIR))

try:
    from ai_engine.thought_profiles import get_all_celebrities  # type: ignore
except Exception:
    get_all_celebrities = None


CELEB_META_BY_ID = {
    item["id"]: item
    for item in (get_all_celebrities() if get_all_celebrities else [])
}


LANGUAGE_SWITCH_SCRIPT = """
<script>
(() => {
  const storageKey = "digital-sage-course-lang";
  const body = document.body;
  const buttons = Array.from(document.querySelectorAll("[data-lang-target]"));
  const applyLang = (lang) => {
    body.dataset.lang = lang;
    buttons.forEach((button) => {
      button.classList.toggle("active", button.dataset.langTarget === lang);
    });
    try { localStorage.setItem(storageKey, lang); } catch (err) {}
  };
  let initial = "dual";
  try { initial = localStorage.getItem(storageKey) || "dual"; } catch (err) {}
  if (!["zh", "en", "dual"].includes(initial)) initial = "dual";
  applyLang(initial);
  buttons.forEach((button) => {
    button.addEventListener("click", () => applyLang(button.dataset.langTarget));
  });
})();
</script>
"""


CATEGORY_LABEL_EN = {
    "商业领袖": "Business Leaders",
    "科技思想家": "Technology Thinkers",
    "设计大师": "Design Masters",
    "科学家": "Scientists",
    "医学专家": "Medical Experts",
    "思想家": "Philosophers",
    "文化创作者": "Cultural Creators",
    "公共治理": "Public Governance",
}


SOURCE_TRACKS = {
    "business": [
        {
            "label": "Primary operating record",
            "title_zh": "原始经营记录",
            "title_en": "Primary operating record",
            "body_zh": "优先回看股东信、致投资者信、年度信、产品发布稿和创始人长访谈，用来验证其长期配置和取舍逻辑。",
            "body_en": "Start with shareholder letters, annual letters, investor notes, launch memos, and long-form founder interviews to verify how capital allocation and trade-offs were framed over time.",
        },
        {
            "label": "Decision cases",
            "title_zh": "关键决策案例",
            "title_en": "Decision cases",
            "body_zh": "把并购、定价、聚焦、裁撤、国际化这些节点当作证据场，看他在高压时到底守住了什么。",
            "body_en": "Use acquisitions, pricing moves, focus decisions, restructurings, and expansion moments as evidence windows for what was protected under pressure.",
        },
        {
            "label": "Secondary biographies",
            "title_zh": "权威传记与商业史",
            "title_en": "Secondary biographies",
            "body_zh": "最后再用权威传记、商业史和案例研究补上下文，避免只读语录。",
            "body_en": "Then add biographies, business histories, and case studies to restore context and avoid reading the person as a quote machine.",
        },
    ],
    "technology": [
        {
            "label": "Technical statements",
            "title_zh": "技术原话与产品记录",
            "title_en": "Technical statements",
            "body_zh": "优先看技术演讲、产品发布、内部备忘录和长访谈，验证其对平台、分发和工程约束的判断。",
            "body_en": "Prioritize technical talks, launches, memos, and long interviews to verify how platform bets, distribution, and engineering constraints were described.",
        },
        {
            "label": "Architecture shifts",
            "title_zh": "路线迁移节点",
            "title_en": "Architecture shifts",
            "body_zh": "重点回看模型升级、平台迁移、开放封闭取舍等节点，因为真正的方法论通常在换轨时最清楚。",
            "body_en": "Focus on model shifts, platform migrations, and open-versus-closed decisions, because methods become clearest when the track changes.",
        },
        {
            "label": "Independent reporting",
            "title_zh": "独立报道与口述史",
            "title_en": "Independent reporting",
            "body_zh": "再用权威科技媒体、口述史和行业分析补充结果与争议。",
            "body_en": "Then add reporting, oral histories, and industry analysis to understand outcomes, contradictions, and contested interpretations.",
        },
    ],
    "design": [
        {
            "label": "Works and exhibitions",
            "title_zh": "作品、展览与设计阐释",
            "title_en": "Works and exhibitions",
            "body_zh": "优先看代表作品、展览文本、设计说明和公开演讲，而不是只看成品照片。",
            "body_en": "Start with works, exhibition texts, design notes, and talks instead of relying only on finished visuals.",
        },
        {
            "label": "Material decisions",
            "title_zh": "材料与删减决策",
            "title_en": "Material decisions",
            "body_zh": "把材料选择、删减动作、空间秩序和用户感知当作方法论的真正证据。",
            "body_en": "Treat material choices, subtraction, spatial order, and user perception as the real evidence of method.",
        },
        {
            "label": "Critical interpretation",
            "title_zh": "评论与设计史补充",
            "title_en": "Critical interpretation",
            "body_zh": "最后用评论文章、设计史和同行回顾补足背景与争议。",
            "body_en": "Then add criticism, design history, and peer retrospectives for context and debate.",
        },
    ],
    "science": [
        {
            "label": "Primary papers",
            "title_zh": "论文与原始研究",
            "title_en": "Primary papers",
            "body_zh": "优先回到论文、讲座、实验报告和诺奖演讲，确认真正的假设、方法和结论边界。",
            "body_en": "Return to papers, lectures, reports, and Nobel or academy talks to check the real hypothesis, method, and limits of the conclusion.",
        },
        {
            "label": "Breakthrough episodes",
            "title_zh": "突破性发现节点",
            "title_en": "Breakthrough episodes",
            "body_zh": "把关键发现、复现实验和学术争论节点当作高价值证据，而不是只看结果标签。",
            "body_en": "Use breakthrough moments, replication attempts, and scientific disputes as evidence instead of only consuming the final label of success.",
        },
        {
            "label": "Scientific biographies",
            "title_zh": "科学史与传记",
            "title_en": "Scientific biographies",
            "body_zh": "再用科学史、实验室回忆录和传记补足时代背景与同行网络。",
            "body_en": "Then add biographies, lab memoirs, and histories of science to recover time, context, and peer networks.",
        },
    ],
    "medical": [
        {
            "label": "Clinical record",
            "title_zh": "临床与公共卫生原始材料",
            "title_en": "Clinical record",
            "body_zh": "优先看指南、临床论文、公开通报、病例讨论和权威访谈，验证风险排序和证据口径。",
            "body_en": "Start with guidelines, clinical papers, public briefings, case discussions, and authoritative interviews to verify risk ranking and evidence standards.",
        },
        {
            "label": "Crisis decisions",
            "title_zh": "危机与救治节点",
            "title_en": "Crisis decisions",
            "body_zh": "重点回看疫情、救治、筛查和沟通节点，因为方法论在高压环境下最容易显形。",
            "body_en": "Focus on outbreak, treatment, screening, and communication decisions, because methods are most visible under pressure.",
        },
        {
            "label": "Medical history",
            "title_zh": "医学史与人物回顾",
            "title_en": "Medical history",
            "body_zh": "最后再用人物回顾、医学史和机构档案来补充长期影响。",
            "body_en": "Then use retrospective profiles, institutional archives, and medical history to understand longer-term impact.",
        },
    ],
    "philosophy": [
        {
            "label": "Primary texts",
            "title_zh": "原典文本",
            "title_en": "Primary texts",
            "body_zh": "优先回到原典、章句、论辩文本和课堂讲授整理，而不是先看二手鸡汤。",
            "body_en": "Start with the primary text, dialogues, aphorisms, and lecture notes instead of beginning with motivational paraphrases.",
        },
        {
            "label": "Commentaries",
            "title_zh": "经典注疏与思想史",
            "title_en": "Commentaries",
            "body_zh": "再用权威注疏、思想史和学术评论厘清概念差异、时代背景和翻译争议。",
            "body_en": "Use commentaries, intellectual history, and academic interpretation to clarify context, conceptual differences, and translation disputes.",
        },
        {
            "label": "Applied transfer",
            "title_zh": "现实应用对照",
            "title_en": "Applied transfer",
            "body_zh": "把原典原则对照到政治、商业、教育、个人修身等现实场景，确认可迁移性。",
            "body_en": "Then test the principle against politics, business, education, and self-cultivation to see what actually transfers.",
        },
    ],
    "culture": [
        {
            "label": "Works and scripts",
            "title_zh": "作品、剧本与访谈",
            "title_en": "Works and scripts",
            "body_zh": "优先回看作品本身、导演手记、脚本、长访谈和创作笔记。",
            "body_en": "Start with the works themselves, scripts, notebooks, director commentary, and long interviews.",
        },
        {
            "label": "Narrative choices",
            "title_zh": "叙事与形式选择",
            "title_en": "Narrative choices",
            "body_zh": "把镜头、节奏、留白、角色关系和母题反复出现的地方当作证据节点。",
            "body_en": "Treat recurring choices in rhythm, framing, silence, character tension, and motif as evidence nodes.",
        },
        {
            "label": "Critical reception",
            "title_zh": "评论史与时代回声",
            "title_en": "Critical reception",
            "body_zh": "最后再用评论史、影评、展览文字和时代回声补足解释空间。",
            "body_en": "Then add criticism, exhibition texts, and reception history to widen interpretation.",
        },
    ],
    "policy": [
        {
            "label": "Policy record",
            "title_zh": "政策原文与公开讲话",
            "title_en": "Policy record",
            "body_zh": "优先看政策原文、公开讲话、回忆录和机构档案，而不是只看后来的评价。",
            "body_en": "Start with policy texts, speeches, memoirs, and institutional archives rather than only later commentary.",
        },
        {
            "label": "Governance episodes",
            "title_zh": "制度落地节点",
            "title_en": "Governance episodes",
            "body_zh": "把关键改革、危机管理、协商和妥协节点作为制度判断的主要证据。",
            "body_en": "Use reform episodes, crises, negotiations, and compromise decisions as the main evidence for governance logic.",
        },
        {
            "label": "Historical evaluation",
            "title_zh": "历史评价与比较研究",
            "title_en": "Historical evaluation",
            "body_zh": "最后再用政治史、比较研究和传记来判断长期效果与代价。",
            "body_en": "Then add political history, comparative analysis, and biographies to assess long-run effects and trade-offs.",
        },
    ],
}


CATEGORY_INFO = {
    "商业领袖": {
        "id": "business",
        "theme": "资本配置、增长纪律与组织杠杆",
        "theme_en": "Capital allocation, growth discipline, and organizational leverage",
        "signal": "用现金流、护城河和长期配置去看真正的企业质量。",
        "signal_en": "Read real business quality through cash flow, moats, and long-horizon allocation.",
        "accent": "#2563eb",
    },
    "科技思想家": {
        "id": "technology",
        "theme": "技术路线、平台势能与工程判断",
        "theme_en": "Technical direction, platform advantage, and engineering judgment",
        "signal": "从底层技术演进、分发与规模化约束去看产品机会。",
        "signal_en": "Evaluate product opportunities through technical evolution, distribution, and scaling constraints.",
        "accent": "#0f766e",
    },
    "设计大师": {
        "id": "design",
        "theme": "体验秩序、材料语言与审美取舍",
        "theme_en": "Experience order, material language, and aesthetic trade-offs",
        "signal": "把抽象理念压缩成可触达、可感知、可复用的设计语言。",
        "signal_en": "Compress abstract ideas into design language that can be sensed, touched, and reused.",
        "accent": "#7c3aed",
    },
    "科学家": {
        "id": "science",
        "theme": "假设、证据与长期发现",
        "theme_en": "Hypothesis, evidence, and long-horizon discovery",
        "signal": "从问题定义、实验设计和证据质量出发搭建认知。",
        "signal_en": "Build understanding from problem definition, experiment design, and evidence quality.",
        "accent": "#0891b2",
    },
    "医学专家": {
        "id": "medical",
        "theme": "风险识别、临床判断与系统防控",
        "theme_en": "Risk recognition, clinical judgment, and systemic prevention",
        "signal": "先排危险，再看证据，再决定行动优先级。",
        "signal_en": "Rule out danger first, weigh evidence second, and decide action priority last.",
        "accent": "#db2777",
    },
    "思想家": {
        "id": "philosophy",
        "theme": "价值系统、意义建构与判断框架",
        "theme_en": "Value systems, meaning-making, and judgment frameworks",
        "signal": "把复杂现实压缩成能反复调用的原则与提问方式。",
        "signal_en": "Compress complex reality into reusable principles and repeatable questions.",
        "accent": "#b45309",
    },
    "文化创作者": {
        "id": "culture",
        "theme": "叙事张力、审美结构与人性观察",
        "theme_en": "Narrative tension, aesthetic structure, and human observation",
        "signal": "把经验转译成作品，把作品再转译成理解世界的方法。",
        "signal_en": "Turn experience into works, then turn works into methods for understanding the world.",
        "accent": "#c2410c",
    },
    "公共治理": {
        "id": "policy",
        "theme": "制度设计、协同治理与长期稳定",
        "theme_en": "Institution design, cooperative governance, and long-term stability",
        "signal": "看清利益结构、执行路径和长期秩序的代价。",
        "signal_en": "See the interest structure, execution path, and long-run cost of order.",
        "accent": "#475569",
    },
}


COURSE_BLUEPRINT = [
    {"number": 1, "title": "思想体系总览", "title_en": "System Overview", "focus": "建立全局图谱", "focus_en": "Build the whole map", "deliverable": "一张可复述的总地图", "deliverable_en": "A reusable map you can explain aloud"},
    {"number": 2, "title": "核心概念①", "title_en": "Core Concept I", "focus": "抓第一根支柱", "focus_en": "Study the first pillar", "deliverable": "识别最重要的概念变量", "deliverable_en": "Identify the most important conceptual variable"},
    {"number": 3, "title": "核心概念②", "title_en": "Core Concept II", "focus": "抓第二根支柱", "focus_en": "Study the second pillar", "deliverable": "理解概念之间如何联动", "deliverable_en": "Understand how the concepts interact"},
    {"number": 4, "title": "核心概念③", "title_en": "Core Concept III", "focus": "抓第三根支柱", "focus_en": "Study the third pillar", "deliverable": "补齐这套系统的边界条件", "deliverable_en": "Recover the boundary conditions of the system"},
    {"number": 5, "title": "判断框架", "title_en": "Judgment Framework", "focus": "学会怎么判断", "focus_en": "Learn how judgment is ordered", "deliverable": "一套可迁移的决策顺序", "deliverable_en": "A transferable order for decision-making"},
    {"number": 6, "title": "实践案例", "title_en": "Practice Cases", "focus": "看思想如何落地", "focus_en": "See how the thinking lands in reality", "deliverable": "把抽象原则映射到真实场景", "deliverable_en": "Map abstract principles to real situations"},
    {"number": 7, "title": "思维模型工具箱", "title_en": "Mental Models Toolkit", "focus": "提炼可复用工具", "focus_en": "Extract reusable tools", "deliverable": "一组随时可调用的模型", "deliverable_en": "A set of models you can call on quickly"},
    {"number": 8, "title": "价值体系与信仰", "title_en": "Values and Belief System", "focus": "回到底层信念", "focus_en": "Return to the base beliefs", "deliverable": "分清原则与技巧的层级", "deliverable_en": "Separate principles from techniques"},
    {"number": 9, "title": "方法论·可操作系统", "title_en": "Method as Operating System", "focus": "把理解变成动作", "focus_en": "Turn understanding into action", "deliverable": "一套 30 天可执行的方法", "deliverable_en": "A 30-day executable method"},
    {"number": 10, "title": "整合与行动", "title_en": "Integration and Action", "focus": "完成知识闭环", "focus_en": "Close the knowledge loop", "deliverable": "形成自己的行动版公式", "deliverable_en": "Form your own action formula"},
]


CATEGORY_SCENARIOS = {
    "business": [
        "当利润、增长和现金流无法同时满足时，先守什么。",
        "当市场很热但组织跟不上时，应该扩张还是收缩。",
        "当你必须在少数机会里下注时，怎样辨认长期杠杆。",
    ],
    "technology": [
        "当新技术刚冒头、叙事很大但工程现实很硬时，如何判断是否跟进。",
        "当产品增长依赖平台红利时，怎么判断红利是不是快结束了。",
        "当团队被功能堆砌拖慢时，如何回到底层技术与分发主线。",
    ],
    "design": [
        "当功能很多但体验杂乱时，应该先删哪里。",
        "当审美与成本冲突时，怎样守住最重要的感知质量。",
        "当一个作品要服务更大用户群时，什么该保留，什么该重做。",
    ],
    "science": [
        "当证据还不充分时，如何区分大胆假设和过度想象。",
        "当一个结果很好看但复现实验不稳定时，先怀疑哪里。",
        "当研究方向太多时，如何把精力收束到最值得验证的问题。",
    ],
    "medical": [
        "当信息不全但必须快速决策时，先排哪类风险。",
        "当公众情绪很高时，如何把复杂专业判断翻译成普通人能执行的话。",
        "当资源有限时，怎样决定优先救治、优先沟通和优先预防的顺序。",
    ],
    "philosophy": [
        "当一个问题看起来像情绪问题时，背后真正的价值冲突是什么。",
        "当你在两个都不错的选项之间摇摆时，应该先问哪一个定义问题。",
        "当现实很吵时，如何回到能长期稳定自己的原则。",
    ],
    "culture": [
        "当作品要表达复杂主题时，怎样避免只剩姿态没有结构。",
        "当你想打动人时，先处理故事、节奏还是人物。",
        "当经验很多却表达不出时，如何把观察转成稳定的创作方法。",
    ],
    "policy": [
        "当局部效率与长期秩序冲突时，应该先稳哪里。",
        "当一个制度短期有效但长期副作用很大时，如何提早识别。",
        "当多方利益难以同时满足时，怎样设计可持续的协同方案。",
    ],
}


ROOT_CARD_RE = re.compile(
    r'<a href="?\.?/([^/]+)/"? class="?tc"?>\s*<div><b>(.*?)</b><br>\s*<small>(.*?)</small><br>\s*(.*?)<br>\s*<small[^>]*>10门课程.*?</small>\s*</div>\s*</a>',
    re.S,
)
SECTION_RE = re.compile(r"<h2>(.*?)</h2><div class=\"thinker-grid\">", re.S)
H1_RE = re.compile(r"<h1>(.*?)</h1>", re.S)
SUBTITLE_RE = re.compile(r'<p class="subtitle">(.*?)</p>', re.S)
SIGNATURE_RE = re.compile(r'<p class="signature">"(.*?)"</p>', re.S)
TAG_RE = re.compile(r'<span class="tag">(.*?)</span>')
LESSON_CARD_RE = re.compile(
    r'<a href="(\d+)\.html" class="ci-card">\s*<div class="ci-num">第\d+课</div>\s*<div>\s*<div class="ci-title">(.*?)</div>\s*<div class="ci-sub">(.*?)</div>\s*</div>\s*</a>',
    re.S,
)


def strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).replace("&nbsp;", " ").strip()


def sentence(text: str) -> str:
    cleaned = text.strip().strip("。")
    return f"{cleaned}。"


def first_clean_line(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return lines[0] if lines else text.strip()


def parse_signature_question(summary: str) -> str:
    match = re.search(r"通过[“\"'‘]?(.+?)[”\"'’]?贯穿始终", summary)
    if match:
        return match.group(1).strip("。")
    return "面对复杂问题时，真正应该先看什么"


def parse_formula(summary: str, tags: list[str]) -> str:
    match = re.search(r"核心公式：([^。]+)", summary)
    if match:
        return match.group(1).strip()
    return f"{tags[0]} × {tags[1]} × {tags[2]}"


def load_bootstrap_root_html() -> str:
    current_html = ROOT_INDEX.read_text(encoding="utf-8")
    current_cards = len(ROOT_CARD_RE.findall(current_html))
    if "<h2>" in current_html and "thinker-grid" in current_html and current_cards >= 50:
        return current_html
    try:
        return subprocess.check_output(
            ["git", "show", "HEAD:index.html"],
            cwd=BASE_DIR,
            text=True,
        )
    except Exception:
        return current_html


def load_seed_catalog() -> dict:
    candidate_paths = [CATALOG_PATH]
    for path in candidate_paths:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("thinkers"):
                return data
        except Exception:
            pass

    try:
        historical = subprocess.check_output(
            ["git", "show", "HEAD:assets/course-catalog.json"],
            cwd=BASE_DIR,
            text=True,
        )
        data = json.loads(historical)
        if data.get("thinkers"):
            return data
    except Exception:
        pass

    return {}


def iter_root_sections(root_html: str) -> list[tuple[str, str]]:
    matches = list(SECTION_RE.finditer(root_html))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        label = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else root_html.find("</div></body>", start)
        if end == -1:
            end = len(root_html)
        grid_html = root_html[start:end]
        if grid_html.endswith("</div>"):
            grid_html = grid_html[:-6]
        sections.append((label, grid_html))
    return sections


def build_lesson_cards(thinker_dir: Path, thinker_html: str, audio_texts: dict, seed_lessons: list[dict] | None = None) -> list[dict]:
    if seed_lessons:
        return [
            {
                "number": lesson["number"],
                "title": first_clean_line(lesson["title"]),
                "subtitle": first_clean_line(lesson.get("focus") or lesson.get("subtitle") or COURSE_BLUEPRINT[lesson["number"] - 1]["focus"]),
                "summary": audio_texts.get(str(lesson["number"])) or audio_texts.get(lesson["number"]) or lesson.get("summary", ""),
            }
            for lesson in seed_lessons
        ]

    cards = sorted(
        (
            {
                "number": int(number),
                "title": strip_html(title_text),
                "subtitle": first_clean_line(strip_html(subtitle_text)),
                "summary": audio_texts.get(number, ""),
            }
            for number, title_text, subtitle_text in LESSON_CARD_RE.findall(thinker_html)
        ),
        key=lambda item: item["number"],
    )
    if cards:
        return cards

    cards = []
    for blueprint in COURSE_BLUEPRINT:
        lesson_number = blueprint["number"]
        lesson_file = thinker_dir / f"{lesson_number}.html"
        lesson_html = lesson_file.read_text(encoding="utf-8") if lesson_file.exists() else ""
        title_match = H1_RE.search(lesson_html)
        subtitle_match = SUBTITLE_RE.search(lesson_html)
        cards.append(
            {
                "number": lesson_number,
                "title": strip_html(title_match.group(1)) if title_match else blueprint["title"],
                "subtitle": first_clean_line(strip_html(subtitle_match.group(1))) if subtitle_match else blueprint["focus"],
                "summary": audio_texts.get(str(lesson_number), ""),
            }
        )
    return cards


def slug_to_title(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("_"))


def render_lang_switch() -> str:
    return """
    <div class="lang-switch">
      <button type="button" class="lang-pill" data-lang-target="dual">ZH + EN</button>
      <button type="button" class="lang-pill" data-lang-target="zh">中文</button>
      <button type="button" class="lang-pill" data-lang-target="en">EN</button>
    </div>
    """


def dual_block(tag: str, zh_text: str, en_text: str, class_name: str = "") -> str:
    class_attr = f' class="{class_name}"' if class_name else ""
    return (
        f"<{tag}{class_attr}><span class=\"copy-zh\">{escape(zh_text)}</span>"
        f"<span class=\"copy-en\">{escape(en_text)}</span></{tag}>"
    )


def dual_label_block(zh_label: str, en_label: str, zh_body: str, en_body: str) -> str:
    return (
        "<div class=\"dual-copy-block\">"
        f"<strong class=\"copy-zh\">{escape(zh_label)}</strong>"
        f"<strong class=\"copy-en\">{escape(en_label)}</strong>"
        f"<p class=\"copy-zh\">{escape(zh_body)}</p>"
        f"<p class=\"copy-en\">{escape(en_body)}</p>"
        "</div>"
    )


def parse_course_doc(slug: str) -> dict:
    path = COURSE_DOCS_DIR / f"{slug}.md"
    if not path.exists():
        return {
            "core_values": [],
            "positions": [],
            "decision_steps": [],
            "cases": [],
            "quote": "",
        }

    text = path.read_text(encoding="utf-8")

    def section_slice(title: str) -> str:
        match = re.search(rf"### {re.escape(title)}\n(.*?)(?=\n### |\n---|\Z)", text, re.S)
        return match.group(1) if match else ""

    values_block = section_slice("核心价值观")
    positions_block = section_slice("关键立场")
    steps_block = section_slice("决策框架")
    cases_block = section_slice("经验案例")
    quote_block = section_slice("经典语录")

    values = re.findall(r"^\d+\.\s+(.+)$", values_block, re.M)
    positions = [
        {"label": label.strip(), "body": body.strip()}
        for label, body in re.findall(r"^- \*\*(.+?)\*\*：(.+)$", positions_block, re.M)
    ]
    steps = [item.strip() for item in re.findall(r"^- \*\*step\d+\*\*：(.+)$", steps_block, re.M)]
    quote_match = re.search(r"> (.+)", quote_block)

    case_pattern = re.compile(
        r"\*\*案例\d+：(.+?)\*\*\n- 教训：(.+?)\n- 结果：(.+?)(?:\n|$)",
        re.S,
    )
    cases = [
        {
            "title": title.strip(),
            "lesson": lesson.strip(),
            "result": result.strip(),
        }
        for title, lesson, result in case_pattern.findall(cases_block)
    ]
    return {
        "core_values": [item.strip() for item in values[:6]],
        "positions": positions[:6],
        "decision_steps": steps[:5],
        "cases": cases[:3],
        "quote": quote_match.group(1).strip() if quote_match else "",
    }


def thinker_reference_bundle(thinker: dict) -> dict | None:
    return REFERENCE_LIBRARY.get(thinker["id"])


def thinker_is_priority_curated(thinker: dict) -> bool:
    return thinker["id"] in PRIORITY_THINKER_IDS


def english_pillars(thinker: dict) -> list[str]:
    return CURATED_PILLAR_GLOSSES.get(thinker["id"], thinker["tags"])


def render_reference_cards(items: list[dict], kind_zh: str, kind_en: str) -> str:
    return "".join(
        f"""
        <article class="reference-card">
          <span class="reference-kind copy-zh">{escape(kind_zh)}</span>
          <span class="reference-kind copy-en">{escape(kind_en)}</span>
          <strong>{escape(item['title'])}</strong>
          <small class="reference-meta">{escape(item['creator'])} · {escape(item['meta'])}</small>
          <p class="copy-zh">{escape(item['note_zh'])}</p>
          <p class="copy-en">{escape(item['note_en'])}</p>
        </article>
        """
        for item in items
    )


def render_reference_shelf(thinker: dict, context: str = "index") -> str:
    bundle = thinker_reference_bundle(thinker)
    if not bundle:
        return ""

    if context == "lesson":
        intro_zh = f"这节课建议优先以 {thinker['name']} 的原典、公开记录和权威书单为准，再回来看本课的判断结构。"
        intro_en = (
            f"Treat these texts as the trusted shelf for {thinker['name_en']}. "
            "Start with the primary record, then return to the lesson structure."
        )
        heading_zh = f"{thinker['name']} 的原典与书单"
        heading_en = f"Primary texts and reading shelf for {thinker['name_en']}"
    else:
        intro_zh = bundle["intro_zh"]
        intro_en = bundle["intro_en"]
        heading_zh = f"{thinker['name']} 的原典与书单"
        heading_en = f"Trusted texts for {thinker['name_en']}"

    primary_cards = render_reference_cards(bundle["primary_sources"], "原典 / 一手记录", "Primary text / public record")
    reading_cards = render_reference_cards(bundle["core_reading"], "核心书单 / 研究入口", "Core reading / study entry")

    return f"""
    <section class="reference-shelf">
      <div class="section-head">
        <div>
          <div class="eyebrow">Reference Shelf</div>
          <h3><span class="copy-zh">{escape(heading_zh)}</span><span class="copy-en">{escape(heading_en)}</span></h3>
        </div>
        <div>
          <p class="copy-zh">{escape(intro_zh)}</p>
          <p class="copy-en">{escape(intro_en)}</p>
        </div>
      </div>
      <div class="reference-group">
        <h4><span class="copy-zh">原典与公开记录</span><span class="copy-en">Primary texts and public record</span></h4>
        <div class="reference-grid">{primary_cards}</div>
      </div>
      <div class="reference-group">
        <h4><span class="copy-zh">核心书单与研究入口</span><span class="copy-en">Core reading shelf</span></h4>
        <div class="reference-grid">{reading_cards}</div>
      </div>
    </section>
    """


def curated_english_brief(thinker: dict, lesson_number: int, context: dict, profile: dict) -> dict:
    blueprint = COURSE_BLUEPRINT[lesson_number - 1]
    name_en = thinker["name_en"]
    tags = english_pillars(thinker)
    question_en = profile["question_en"]
    concept = tags[min(max(lesson_number - 2, 0), 2)]
    supporting = [tag for tag in tags if tag != concept]

    if lesson_number == 1:
        summary = (
            f"This opening lesson maps {name_en} as a complete decision system. "
            f"{profile['throughline']} The task is to see how {tags[0]}, {tags[1]}, and {tags[2]} reinforce one another before you start borrowing isolated moves."
        )
        cards = [
            ("System spine", profile["throughline"]),
            ("Question underneath the work", f"Keep returning to this question: {question_en}"),
            ("What you should leave with", f"A working map of how {tags[0]}, {tags[1]}, and {tags[2]} interact in {name_en}'s best decisions."),
        ]
        takeaways = [
            f"Name the three pillars before you quote {name_en}.",
            f"Notice which pillar carries the most weight when {name_en} makes a difficult trade-off.",
            "Do not confuse public mythology with the deeper order of judgment underneath it.",
            "Leave this lesson with a system map, not a scrapbook of memorable lines.",
        ]
        misreads = [
            f"Reducing {name_en} to temperament or style instead of structure.",
            f"Treating {tags[0]}, {tags[1]}, and {tags[2]} as separate tricks rather than a coordinated system.",
            "Borrowing conclusions without learning what gets examined first.",
        ]
        actions = [
            f"Write a four-sentence map of {name_en}'s system in your own words.",
            f"Take one current problem and ask how each pillar changes your reading of it.",
            "Mark the single pillar you personally underuse most and why.",
        ]
        lesson_note = "Lesson one is a map-building lesson. If you cannot explain the structure back clearly, move more slowly before proceeding."
    elif lesson_number in (2, 3, 4):
        summary = (
            f"{profile['concept_frame'].format(concept=concept, support_one=supporting[0], support_two=supporting[1])} "
            f"This lesson is about learning when {concept} deserves to lead and when it has to be balanced by {supporting[0]} and {supporting[1]}."
        )
        cards = [
            ("What this concept really does", profile["concept_frame"].format(concept=concept, support_one=supporting[0], support_two=supporting[1])),
            ("What it must be paired with", f"Read {concept} together with {supporting[0]} and {supporting[1]}, or it turns into a slogan."),
            ("Where readers usually slip", f"The mistake is treating {concept} as a universal virtue instead of a contextual judgment tool."),
        ]
        takeaways = [
            f"Ask what breaks first if {concept} is ignored in a live decision.",
            f"Test whether your current use of {concept} is structural or merely rhetorical.",
            f"Check what {supporting[0]} or {supporting[1]} would add before you become one-dimensional.",
            f"Translate {concept} into one observable indicator in your own context.",
        ]
        misreads = [
            f"Treating {concept} as a permanent answer rather than a conditional lens.",
            f"Using {concept} in easy situations but abandoning it under pressure.",
            f"Talking about {concept} elegantly without changing decision order or measurement.",
        ]
        actions = [
            f"Revisit one recent decision and ask whether {concept} was explicitly examined or only implied.",
            f"Write one argument for leaning harder into {concept} and one argument for restraint.",
            f"Use {concept} to re-read a choice you were about to settle by intuition alone.",
        ]
        lesson_note = f"This stage is about one pillar at a time. The goal is not definition-memorization but better diagnostic use of {concept}."
    elif lesson_number == 5:
        summary = (
            f"{profile['judgment_frame']} This lesson is where the course shifts from 'what matters' to 'in what order should it be examined.'"
        )
        cards = [
            ("Order before opinion", profile["judgment_frame"]),
            ("First question", f"The opening question is still the anchor: {question_en}"),
            ("What changes after this lesson", "You should become better at sequencing judgment before debating solutions."),
        ]
        takeaways = [
            "The best framework reduces noise before it produces answers.",
            "When teams disagree loudly, they are often tracking different primary variables.",
            "A strong judgment order survives low information and high pressure.",
            "Do not let action outrun problem definition.",
        ]
        misreads = [
            "Treating a framework as presentation theater rather than a real filter on attention.",
            "Jumping to solutions before naming the governing constraint.",
            "Using the framework in meetings but not in private decision-making.",
        ]
        actions = [
            "Rewrite one current problem as sequence: definition, constraint, action.",
            f"Name which of {tags[0]}, {tags[1]}, or {tags[2]} is carrying most of the weight in your current debate.",
            "Set a rule for yourself: write the judgment order before you allow solution discussion.",
        ]
        lesson_note = "This is the lesson where the thinker becomes operational. If the order is wrong, the later action layer will also be wrong."
    elif lesson_number == 6:
        summary = (
            f"{profile['case_frame']} Use the cases to inspect what stays stable when pressure, ambiguity, or limited resources force prioritization."
        )
        cards = [
            ("Why the cases matter", profile["case_frame"]),
            ("What to watch for", "Track what the thinker protects first when the environment becomes noisy or constrained."),
            ("What you are extracting", "You are not collecting stories. You are extracting reusable judgment moves."),
        ]
        takeaways = [
            "A case is valuable only if you can recover the structure underneath the outcome.",
            "Pay attention to what was protected, delayed, or refused under pressure.",
            "Good case-reading turns biography into decision pattern.",
            "Always finish by asking what changes in your own work after the case.",
        ]
        misreads = [
            "Copying the visible move without checking whether your constraints match.",
            "Reading a success story as luck instead of structure and sequence.",
            "Remembering the anecdote but not the governing principle.",
        ]
        actions = [
            "Pick the case closest to your current pressure pattern and rewrite it in your own operating language.",
            "State what the thinker would likely protect first in your current situation and why.",
            "Write one decision rule that survives even if the surface details differ.",
        ]
        lesson_note = "Cases are the reality test for the curriculum. If the principles disappear under pressure, they were never really learned."
    elif lesson_number == 7:
        summary = (
            f"{profile['toolkit_frame']} This lesson compresses experience into tools you can call on quickly when the situation changes."
        )
        cards = [
            ("What belongs in the toolkit", profile["toolkit_frame"]),
            ("What a real tool does", "A real tool changes where you look, what you ignore, and how fast you detect the key variable."),
            ("How to know it is working", "The best tools make hard decisions cleaner before they make them easier."),
        ]
        takeaways = [
            "Collect fewer tools, but make sure they survive contact with pressure.",
            "Keep at least one tool for amplification and one for restraint.",
            "A tool is learned only when it changes an actual decision this week.",
            "If the tool never reaches the operating layer, it is still trivia.",
        ]
        misreads = [
            "Collecting labels instead of building fast retrieval under stress.",
            "Keeping only tools that flatter your instincts while ignoring the braking tools.",
            "Mistaking conceptual familiarity for operating ability.",
        ]
        actions = [
            "Reduce the toolkit to three moves you can actually remember in the room.",
            "Run those three moves across one live project and compare what each one reveals.",
            "Name the cognitive mistake you make most often and attach a counter-tool to it.",
        ]
        lesson_note = "This lesson is about portability. The point is not more theory; it is faster access to the right lens in live work."
    elif lesson_number == 8:
        summary = (
            f"{profile['values_frame']} This lesson returns beneath technique to the moral and strategic commitments the thinker refuses to trade away casually."
        )
        cards = [
            ("Why values matter here", profile["values_frame"]),
            ("What values actually do", "Values are not decorative statements. They are what determine what will not be sacrificed first."),
            ("What this lesson changes", "You should start seeing which trade-offs the thinker would refuse even under short-term pressure."),
        ]
        takeaways = [
            "A real principle becomes visible in what it is willing to cost you.",
            "Values matter most when incentives tempt you to reorder them quietly.",
            "Technique becomes unstable when it is detached from a value hierarchy.",
            "The deeper question is not what the thinker admires, but what the thinker protects.",
        ]
        misreads = [
            "Treating values as branding language rather than decision infrastructure.",
            "Talking about principles in calm periods and abandoning them in hard ones.",
            "Naming a principle without naming the sacrifice it requires.",
        ]
        actions = [
            "Write the three principles from this thinker that you would be most reluctant to violate in your own work.",
            "Review one recent compromise and ask whether it was strategic necessity or quiet value drift.",
            "Compress the value system into language you could actually remember under stress.",
        ]
        lesson_note = "This lesson explains why the thinker's choices still hang together over time instead of dissolving into clever opportunism."
    elif lesson_number == 9:
        summary = (
            f"{profile['system_frame']} This is the operating-systems lesson: inputs, review loops, and decision rhythms that keep the philosophy alive after the page is closed."
        )
        cards = [
            ("What an operating system changes", profile["system_frame"]),
            ("Where it lives", "A real operating system appears in calendars, information diets, review loops, and decision thresholds."),
            ("What it prevents", "Without the operating layer, insight evaporates and the course collapses back into admiration."),
        ]
        takeaways = [
            "A method becomes real only when it has a repeatable cadence.",
            "Inputs, decisions, and review must reinforce one another rather than live in separate files.",
            "Good systems reduce dependence on mood and increase dependence on order.",
            "The goal is not complexity. It is repeatability under real load.",
        ]
        misreads = [
            "Turning method into a task list with no rhythm.",
            "Building action steps without a review loop.",
            "Redesigning the system so often that nothing compounds.",
        ]
        actions = [
            "Design a seven-day operating version of this thinker's system.",
            "Choose one recurring decision and attach a fixed review question to it.",
            "Identify the point where your current workflow most often breaks the philosophy you claim to admire.",
        ]
        lesson_note = "If the course is ever going to survive real life, it happens here: in rhythm, not in inspiration."
    else:
        summary = (
            f"{profile['integration_frame']} The final lesson is about transfer: moving from understanding the thinker to running a version of the system yourself."
        )
        cards = [
            ("What integration really means", profile["integration_frame"]),
            ("The test of transfer", f"You can explain when to lead with {tags[0]}, when {tags[1]} should pull you back, and when {tags[2]} sets the boundary."),
            ("The real end point", f"The goal is not imitation of {name_en}, but a version of the system that has become your own."),
        ]
        takeaways = [
            "Integration means compression: ten lessons turned into one reusable workflow.",
            "If you cannot restate the system in your own work language, it is not integrated yet.",
            "The strongest learning result is continued self-upgrading after the formal course ends.",
            "By now the thinker should feel less like a hero and more like an internal order of attention.",
        ]
        misreads = [
            "Ending the course with admiration but no personal operating formula.",
            "Repeating the thinker's language without rewriting it for your own environment.",
            "Failing to turn the first nine lessons into one review template.",
        ]
        actions = [
            "Write your own three-sentence version of the full system.",
            "Choose one 30-day project and assign lessons to moments in the project life cycle.",
            "Run a weekly review asking whether you are becoming more derivative or more distinct in your own use of the framework.",
        ]
        lesson_note = "The course ends only when the framework starts changing your own decisions without needing the page in front of you."

    return {
        "headline": blueprint["title_en"],
        "focus": blueprint["focus_en"],
        "deliverable": blueprint["deliverable_en"],
        "summary": summary,
        "cards": cards,
        "takeaways": takeaways,
        "misreads": misreads,
        "actions": actions,
        "lesson_note": lesson_note,
    }


def english_brief(thinker: dict, lesson_number: int, context: dict) -> dict:
    profile = CURATED_ENGLISH_PROFILES.get(thinker["id"])
    if profile:
        return curated_english_brief(thinker, lesson_number, context, profile)

    blueprint = COURSE_BLUEPRINT[lesson_number - 1]
    tags = thinker["tags"]
    name_en = thinker["name_en"]
    question = thinker["guiding_question_en"]
    summary = (
        f"This lesson uses {name_en} to train a repeatable way of seeing {tags[0]}, {tags[1]}, and {tags[2]} as one system. "
        f"The point is not to imitate the tone, but to learn the order of judgment behind the voice."
    )
    cards = [
        ("Core lens", f"Read the issue through {tags[0]} before chasing noise or surface-level activity."),
        ("Question to start with", f"Begin with: {question}"),
        ("Learning outcome", f"By the end, you should be able to restate the lesson in your own work context."),
    ]
    takeaways = [
        f"Track {tags[0]} as a structural variable instead of a slogan.",
        f"Use {tags[1]} to inspect compounding, rhythm, or second-order effects.",
        f"Let {tags[2]} define the boundary conditions and timing of action.",
        f"Translate the lesson into one choice you are facing this week.",
    ]
    misreads = [
        "Confusing a memorable quote with the real decision process behind it.",
        "Copying the style of the thinker without checking the constraints of your own context.",
        "Using a single principle too rigidly instead of letting the system of principles interact.",
    ]
    actions = [
        f"Write one paragraph on how {tags[0]} changes the way you see your current decision.",
        f"List the main constraint that {name_en} would inspect before acting.",
        "Turn the lesson into one concrete operating rule you can test within seven days.",
    ]
    return {
        "headline": blueprint["title_en"],
        "focus": blueprint["focus_en"],
        "deliverable": blueprint["deliverable_en"],
        "summary": summary,
        "cards": cards,
        "takeaways": takeaways,
        "misreads": misreads,
        "actions": actions,
        "lesson_note": f"This lesson belongs to the {blueprint['title_en']} stage of the curriculum and should end in a visible operating takeaway.",
    }


def thinker_source_tracks(thinker: dict) -> list[dict]:
    return SOURCE_TRACKS.get(thinker["category"], SOURCE_TRACKS["philosophy"])


def lesson_title_zh(thinker: dict, lesson_number: int) -> str:
    name = thinker["name"]
    tags = thinker["tags"]
    if lesson_number == 1:
        return f"{name}思想体系总览"
    if lesson_number == 2:
        return f"核心概念：{tags[0]}"
    if lesson_number == 3:
        return f"核心概念：{tags[1]}"
    if lesson_number == 4:
        return f"核心概念：{tags[2]}"
    if lesson_number == 5:
        return f"{name}的判断框架"
    if lesson_number == 6:
        return f"从经验中学习：{name}的实践案例"
    if lesson_number == 7:
        return f"{name}的思维模型工具箱"
    if lesson_number == 8:
        return f"价值体系：{name}的信仰与原则"
    if lesson_number == 9:
        return f"方法论：{name}的可操作系统"
    return f"整合与行动：成为{name}式的思考者"


def bootstrap_catalog() -> dict:
    thinkers: list[dict] = []
    category_counts: dict[str, int] = {}
    seed_catalog = load_seed_catalog()
    seed_thinkers = seed_catalog.get("thinkers") or []

    if seed_thinkers:
        for seed in seed_thinkers:
            slug = seed["id"]
            thinker_dir = BASE_DIR / slug
            thinker_index = thinker_dir / "index.html"
            audio_texts_path = thinker_dir / "audio_texts.json"
            if not thinker_index.exists() or not audio_texts_path.exists():
                continue

            thinker_html = thinker_index.read_text(encoding="utf-8")
            audio_texts = json.loads(audio_texts_path.read_text(encoding="utf-8"))
            lesson_cards = build_lesson_cards(thinker_dir, thinker_html, audio_texts, seed.get("lessons"))
            signature_match = SIGNATURE_RE.search(thinker_html)
            signature = strip_html(signature_match.group(1)) if signature_match else ""
            tags = seed.get("tags") or []
            category_label = seed.get("category_label") or next(
                (label for label, info in CATEGORY_INFO.items() if info["id"] == seed["category"]),
                "思想家",
            )
            category_meta = CATEGORY_INFO.get(category_label, CATEGORY_INFO["思想家"])
            guiding_question = seed.get("guiding_question") or parse_signature_question(audio_texts.get("1", ""))
            formula = seed.get("formula") or parse_formula(audio_texts.get("10", ""), tags)
            course_doc = parse_course_doc(slug)
            meta = CELEB_META_BY_ID.get(slug, {})
            name_en = meta.get("name_en") or seed.get("name_en") or slug_to_title(slug)
            signature = course_doc.get("quote") or meta.get("signature") or seed.get("quote") or signature

            profile = CURATED_ENGLISH_PROFILES.get(slug, {})
            thinker = {
                "id": slug,
                "name": seed["name"],
                "name_en": name_en,
                "title": seed["title"],
                "quote": signature,
                "guiding_question": guiding_question,
                "guiding_question_en": profile.get("question_en")
                or seed.get("guiding_question_en")
                or "What should be examined first when this problem becomes complex?",
                "formula": formula,
                "category": category_meta["id"],
                "category_label": category_label,
                "category_label_en": seed.get("category_label_en") or CATEGORY_LABEL_EN[category_label],
                "category_theme": seed.get("category_theme") or category_meta["theme"],
                "category_theme_en": seed.get("category_theme_en") or category_meta["theme_en"],
                "category_signal": seed.get("category_signal") or category_meta["signal"],
                "category_signal_en": seed.get("category_signal_en") or category_meta["signal_en"],
                "accent": seed.get("accent") or category_meta["accent"],
                "tags": tags[:3],
                "course_doc": course_doc,
                "priority_curated": slug in PRIORITY_THINKER_IDS,
                "lessons": lesson_cards,
            }
            for lesson in thinker["lessons"]:
                lesson["title"] = lesson_title_zh(thinker, lesson["number"])
                lesson["subtitle"] = COURSE_BLUEPRINT[lesson["number"] - 1]["focus"]
            thinkers.append(thinker)
            category_counts[category_meta["id"]] = category_counts.get(category_meta["id"], 0) + 1
    else:
        root_html = load_bootstrap_root_html()
        for category_label, grid_html in iter_root_sections(root_html):
            category_meta = CATEGORY_INFO[category_label]
            cards = ROOT_CARD_RE.findall(grid_html)
            for slug, name, title, tags_html in cards:
                thinker_dir = BASE_DIR / slug
                thinker_index = thinker_dir / "index.html"
                audio_texts_path = thinker_dir / "audio_texts.json"
                if not thinker_index.exists() or not audio_texts_path.exists():
                    continue

                thinker_html = thinker_index.read_text(encoding="utf-8")
                audio_texts = json.loads(audio_texts_path.read_text(encoding="utf-8"))
                lesson_cards = build_lesson_cards(thinker_dir, thinker_html, audio_texts)
                tags = [strip_html(tag) for tag in re.findall(r"<span class=tt>(.*?)</span>", tags_html)]
                signature_match = SIGNATURE_RE.search(thinker_html)
                signature = strip_html(signature_match.group(1)) if signature_match else ""
                guiding_question = parse_signature_question(audio_texts.get("1", ""))
                formula = parse_formula(audio_texts.get("10", ""), tags)
                course_doc = parse_course_doc(slug)
                meta = CELEB_META_BY_ID.get(slug, {})
                name_en = meta.get("name_en") or slug_to_title(slug)
                signature = course_doc.get("quote") or meta.get("signature") or signature

                profile = CURATED_ENGLISH_PROFILES.get(slug, {})
                thinker = {
                    "id": slug,
                    "name": strip_html(name),
                    "name_en": name_en,
                    "title": strip_html(title),
                    "quote": signature,
                    "guiding_question": guiding_question,
                    "guiding_question_en": profile.get("question_en")
                    or "What should be examined first when this problem becomes complex?",
                    "formula": formula,
                    "category": category_meta["id"],
                    "category_label": category_label,
                    "category_label_en": CATEGORY_LABEL_EN[category_label],
                    "category_theme": category_meta["theme"],
                    "category_theme_en": category_meta["theme_en"],
                    "category_signal": category_meta["signal"],
                    "category_signal_en": category_meta["signal_en"],
                    "accent": category_meta["accent"],
                    "tags": tags[:3],
                    "course_doc": course_doc,
                    "priority_curated": slug in PRIORITY_THINKER_IDS,
                    "lessons": lesson_cards,
                }
                for lesson in thinker["lessons"]:
                    lesson["title"] = lesson_title_zh(thinker, lesson["number"])
                    lesson["subtitle"] = COURSE_BLUEPRINT[lesson["number"] - 1]["focus"]
                thinkers.append(thinker)
                category_counts[category_meta["id"]] = category_counts.get(category_meta["id"], 0) + 1

    categories = []
    for label, info in CATEGORY_INFO.items():
        categories.append(
            {
                "id": info["id"],
                "label": label,
                "label_en": CATEGORY_LABEL_EN[label],
                "theme": info["theme"],
                "theme_en": info["theme_en"],
                "signal": info["signal"],
                "signal_en": info["signal_en"],
                "accent": info["accent"],
                "count": category_counts.get(info["id"], 0),
            }
        )

    featured_ids = []
    preferred = ["buffett", "sam_altman", "steve_jobs", "confucius", "laozi", "alan_turing", "zhongnanshan", "lee_kuan_yew"]
    for thinker_id in preferred:
        if any(item["id"] == thinker_id for item in thinkers):
            featured_ids.append(thinker_id)

    return {
        "version": 6,
        "stats": {
            "thinkers": len(thinkers),
            "lessons": len(thinkers) * len(COURSE_BLUEPRINT),
            "categories": len(categories),
        },
        "blueprint": COURSE_BLUEPRINT,
        "categories": categories,
        "featured_ids": featured_ids,
        "thinkers": sorted(thinkers, key=lambda item: (item["category_label"], item["name"])),
    }


def load_catalog() -> dict:
    if CATALOG_PATH.exists():
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        thinkers = data.get("thinkers") or []
        has_lessons = bool(thinkers and thinkers[0].get("lessons"))
        if data.get("version", 0) >= 6 and thinkers and has_lessons:
            return data
    return bootstrap_catalog()


def course_contexts(thinker: dict, lesson_number: int) -> dict:
    name = thinker["name"]
    title = thinker["title"]
    tags = thinker["tags"]
    quote = thinker["quote"]
    question = thinker["guiding_question"]
    category = thinker["category"]
    scenarios = CATEGORY_SCENARIOS[category]
    lesson = thinker["lessons"][lesson_number - 1]
    blueprint = COURSE_BLUEPRINT[lesson_number - 1]

    concept = tags[min(max(lesson_number - 2, 0), 2)]
    supporting = [tag for tag in tags if tag != concept]

    if lesson_number == 1:
        intro = (
            f"这节课先不急着记定义，而是先把 {name} 这套方法论的整体骨架搭起来。"
            f"你会看到 {tags[0]}、{tags[1]}、{tags[2]} 如何彼此配合，以及 {question} 为什么会成为 {name} 反复回到的起点。"
        )
        cards = [
            ("系统核心", f"{name} 并不是靠单一技巧取胜，而是靠 {tags[0]}、{tags[1]}、{tags[2]} 三根支柱协同工作。"),
            ("首要追问", f"进入任何复杂问题之前，{name} 会先问：{question}。"),
            ("学习结果", f"学完这课，你应该能用自己的话复述 {name} 的总地图，而不是只记住几句名言。"),
        ]
        bullets = [
            f"{name} 最看重的并不是表面效率，而是 {tags[0]} 背后的真实质量。",
            f"{tags[1]} 决定了这套方法为什么能拉开长期差距。",
            f"{tags[2]} 不是附加项，而是帮助你判断边界和节奏的关键条件。",
            f"如果只学一个技巧而不理解三者的配合，你会把 {name} 的方法学成碎片。 ",
        ]
        misreads = [
            f"把 {name} 误解成只会输出结论，而忽略他如何定义问题。",
            f"只盯住 {tags[0]} 的表面形式，却没有看它为什么在这个领域成立。",
            f"把 {name} 的成功归因于天赋，而不是长期重复的判断纪律。",
        ]
        actions = [
            f"先用一张纸写下 {name} 的三根支柱：{tags[0]}、{tags[1]}、{tags[2]}。",
            f"把你当前最难的一个问题，改写成 {question} 这种提问方式。",
            f"尝试说明这三根支柱里，哪一根是你现在最弱的一环，以及为什么。",
        ]
        memory = f"{name} 的系统不是一招制胜，而是围绕“{question}”组织出来的三支柱结构。"
    elif lesson_number in (2, 3, 4):
        intro = (
            f"这节课单独拆 {concept}。对 {name} 来说，{concept} 不是一个口号，"
            f"而是决定资源如何流动、判断如何排序、风险如何暴露的关键变量。"
        )
        cards = [
            ("概念定义", f"在 {name} 的语境里，{concept} 关注的是“先看什么、再做什么”，而不是漂亮表达。"),
            ("与其他支柱的关系", f"{concept} 必须和 {supporting[0]}、{supporting[1]} 一起看，否则很容易变成片面执念。"),
            ("边界条件", f"当 {concept} 看起来正确但结果不对时，通常说明约束不在概念本身，而在场景判断或执行节奏。"),
        ]
        bullets = [
            f"如果去掉 {concept}，{name} 的整套方法会先失去哪一块判断力。",
            f"在你的领域里，{concept} 对应的真实观测指标是什么，而不只是情绪上的“感觉”。",
            f"{concept} 和 {supporting[0]} 出现冲突时，应该先看结构性约束还是短期表现。",
            f"什么时候必须坚持 {concept}，什么时候要承认它只是局部最优。 ",
        ]
        misreads = [
            f"把 {concept} 当成永远正确的答案，而不是一种带条件的判断工具。",
            f"只会在顺风局谈 {concept}，一到高压环境就退回短期直觉。",
            f"把 {concept} 简化成风格偏好，没有落实到决策顺序和指标观察上。",
        ]
        actions = [
            f"找出你最近一个决策，复盘当时有没有明确把 {concept} 作为主变量。",
            f"列出两个支持 {concept} 的证据，和一个提醒你别走极端的反证。",
            f"在接下来 24 小时里，用 {concept} 重看一个你原本准备凭直觉决定的选择。",
        ]
        memory = f"学 {concept} 的重点，不是背定义，而是知道它何时该成为第一判断变量。"
    elif lesson_number == 5:
        intro = (
            f"如果前四课解决的是“看什么”，这节课解决的是“怎么判断”。"
            f"{name} 的强大之处，不在于他总有答案，而在于他有一套稳定的排序顺序。"
        )
        cards = [
            ("第一步", f"先定义问题：{question}。"),
            ("第二步", f"再确认真正约束，是 {tags[0]}、{tags[1]} 还是 {tags[2]} 没有到位。"),
            ("第三步", f"最后才决定资源、节奏和动作，不让执行先于判断。"),
        ]
        bullets = [
            f"任何复杂判断先回到问题定义，而不是直接讨论方案优劣。",
            f"如果争论越来越大，通常不是意见不同，而是每个人盯的主变量不同。",
            f"{name} 的框架擅长做减法，先砍掉不关键的动作，再谈放大关键投入。",
            f"真正的判断框架应该能在低信息和高压力场景里重复使用。 ",
        ]
        misreads = [
            "以为判断框架只是写在纸上的流程，实际没有配套信息筛选规则。",
            "一上来讨论解决方案，跳过了问题定义和约束识别。",
            "把判断框架当成开会语言，没有落实到个人决策节奏。",
        ]
        actions = [
            "拿你正在处理的一件复杂问题，按“问题定义 → 约束 → 动作”重写一遍。",
            f"把当前讨论中最吵的一项意见，翻译成它究竟更偏向 {tags[0]}、{tags[1]} 还是 {tags[2]}。",
            "给自己设一个规则：以后先写出判断顺序，再允许自己开会讨论方案。",
        ]
        memory = f"{name} 的判断力，本质上来自先定义问题、再识别约束、最后才出手。"
    elif lesson_number == 6:
        intro = (
            f"案例课不追求背历史，而是训练你看到：{name} 在真实局面里到底怎样把原则落地。"
            f"下面三个场景，分别对应高压、模糊和资源有限时的应用方式。"
        )
        cards = [
            ("场景一", f"{scenarios[0]} 在这种局面里，{name} 不会先求全面，而会先守住最关键的结构。"),
            ("场景二", f"{scenarios[1]} 这时重要的不是热度，而是识别哪个变量会在 12 个月后反噬你。"),
            ("场景三", f"{scenarios[2]} 真正的差距通常来自下注顺序，而不是动作数量。"),
        ]
        bullets = [
            f"案例的意义不是替你决定，而是帮你看到 {name} 的原则在什么压力下仍然成立。",
            f"把案例拆成“问题定义、约束识别、动作选择”三步，你就能迁移到自己的环境里。",
            f"如果你只记故事，不抽出结构，案例就只会变成谈资。",
            f"高质量案例复盘，最后一定要落到“我以后会怎么做得不同”。 ",
        ]
        misreads = [
            "把案例当成模板照搬，忽略自己的约束条件和资源差异。",
            "只看结果，不看当时为何这样排序。",
            "把成功故事理解成运气，而非一套可重复的判断动作。",
        ]
        actions = [
            "从三个场景里挑一个最像你现状的，把对应做法改写成自己的版本。",
            "如果你团队正在争论，试着先说清楚你们目前属于哪一种压力场景。",
            "复盘最近一个失误：如果当时用这节课的结构，会不会更早发现真正问题。",
        ]
        memory = f"案例课的重点不是抄答案，而是看清 {name} 在压力下如何仍然守住原则排序。"
    elif lesson_number == 7:
        intro = (
            f"这节课要把 {name} 的经验压缩成可反复调用的工具箱。"
            f"工具箱的价值在于：当场景变化时，你不用重新发明方法，只需要判断该调用哪一个模型。"
        )
        cards = [
            ("模型一", f"用 {question} 做问题筛选器，先把噪音挡在门外。"),
            ("模型二", f"用 {tags[0]} 作为主透镜，看事情真正创造价值的部分在哪里。"),
            ("模型三", f"用 {tags[1]} 和 {tags[2]} 检查节奏与边界，避免局部最优。"),
        ]
        bullets = [
            "模型的价值不在名词，而在它能否让你更快看见关键变量。",
            "高质量工具箱通常同时包含“放大器”和“刹车器”，防止你一路冲偏。",
            f"如果一个模型不能帮助你解释 {category} 场景中的真实约束，它就还不算真正被你掌握。",
            "好工具不是越多越好，而是越容易在高压时被调用越好。 ",
        ]
        misreads = [
            "收藏很多模型名词，却从未在真实问题中实际调用。",
            "把工具箱做成知识清单，而不是决策清单。",
            "只保留让自己舒服的模型，没有保留提醒自己踩刹车的模型。",
        ]
        actions = [
            f"从今天开始，把 {name} 的工具箱先压缩成 3 个：提问器、主透镜、边界检查器。",
            "选一个正在推进的项目，强迫自己用这三个工具各扫一遍。",
            "把最常让你犯错的偏差写下来，给它绑定一个对应的检查动作。",
        ]
        memory = f"真正的工具箱不是知识仓库，而是你在高压环境里也能随手调用的判断器。"
    elif lesson_number == 8:
        intro = (
            f"技巧决定一时表现，价值系统决定长期方向。"
            f"这节课要回到 {name} 最底层的信念：什么值得守，什么必须放，什么绝不能为了短期结果而牺牲。"
        )
        cards = [
            ("原则一", f"{tags[0]} 对 {name} 来说不是策略偏好，而是判断什么值得长期投入的尺度。"),
            ("原则二", f"{tags[1]} 代表他面对不确定性时的秩序感，帮助他不被短期波动带偏。"),
            ("原则三", f"{tags[2]} 决定了边界和底线，告诉他哪些增长、成绩或话术其实不该要。"),
        ]
        bullets = [
            f"{name} 的价值观不是抽象美德，而是具体到日常选择的优先级顺序。",
            f"当外部压力很大时，真正能让人稳定下来的，不是技巧，而是你是否知道自己在守什么。",
            "长期主义真正难的地方，不是时间长，而是在短期回报诱惑里依然不改排序。",
            f"如果一个原则不能指导你放弃某些东西，那它大概率还不算真正的原则。 ",
        ]
        misreads = [
            "把价值观理解成个人风格，而不是决策底盘。",
            "平时讲原则，一到高压节点就完全放弃。",
            "把原则说得很满，但没有对应的取舍动作。",
        ]
        actions = [
            f"把 {name} 这套价值观翻译成你自己的三条“绝不轻易打折”的原则。",
            "检查你最近一次妥协：那是现实约束，还是价值顺序出了问题。",
            "给团队写一版更短的原则表述，确保大家在忙的时候也记得住。",
        ]
        memory = f"价值系统的作用，不是让你显得正确，而是让你在诱惑和压力里仍然知道该守什么。"
    elif lesson_number == 9:
        intro = (
            f"如果不把方法拆成日常动作，再好的理解都会蒸发。"
            f"这节课把 {name} 的思想压成一个可执行系统：你每天看什么、每周复盘什么、每月该调整什么。"
        )
        cards = [
            ("输入规则", f"先把信息入口改成围绕 {tags[0]} 与 {question} 的筛选方式。"),
            ("决策规则", f"做判断时先看 {tags[1]} 的结构约束，再看 {tags[2]} 的节奏要求。"),
            ("复盘规则", f"每次行动之后，都回到“我究竟有没有守住主变量”这个问题。"),
        ]
        bullets = [
            "方法论之所以能落地，是因为它把抽象原则转译成固定节奏和固定动作。",
            "如果你的系统里没有复盘环节，它最终只会退化成一套激情表态。",
            "真正可执行的方法不复杂，但会要求你反复做同样的减法。",
            "高质量系统应该让你越来越少依赖临场灵感，越来越多依赖稳定顺序。 ",
        ]
        misreads = [
            "把方法论做成待办事项清单，结果没有形成节奏。",
            "只建立输入和行动，没有建立复盘闭环。",
            "每次都想重新设计系统，导致没有任何东西持续足够久。",
        ]
        actions = [
            "先设计一个 7 天版系统：每日输入、每周判断、每周复盘。",
            f"给自己设一个问题：本周有没有任何动作真正服务于 {tags[0]}。",
            "把你现在最重要的项目，套进这套系统里跑一周，看哪里最容易崩。",
        ]
        memory = f"方法论真正生效，不在懂，而在你是否把它压成可重复的输入、判断和复盘节奏。"
    else:
        intro = (
            f"最后一课不是复述，而是整合。你要从“我知道 {name} 在想什么”，"
            f"走到“我已经能在自己的场景里调动这套系统”。"
        )
        cards = [
            ("整合公式", f"{name} 式思考的核心不是一句名言，而是 {thinker['formula']}。"),
            ("迁移能力", f"当你能把 {tags[0]}、{tags[1]}、{tags[2]} 带进自己的领域，这套课才真正变成你的系统。"),
            ("下一阶段", f"最终目标不是模仿 {name}，而是让你形成属于自己的版本和节奏。"),
        ]
        bullets = [
            "整合课的重点不是学更多，而是把前面九课压成一个能随时调用的工作流。",
            f"如果你已经能说清楚：什么场景先看 {tags[0]}，什么时候要被 {tags[1]} 拉回来，什么时候由 {tags[2]} 定边界，你就真正学会了。",
            "真正成熟的学习结果，是你能在没有教材的时候也继续升级这套系统。",
            f"从现在开始，{name} 不应该只是一个名字，而应该成为你判断时的一种内部顺序。 ",
        ]
        misreads = [
            "以为课程结束就代表学习完成，没有留下自己的行动版公式。",
            "只会引用别人的语言，不能用自己的业务和处境重写。",
            "没有把前面九课收束成一个稳定的复盘模板。",
        ]
        actions = [
            "写出你自己的版本：我会如何用三句话解释这套系统。",
            "选一个 30 天项目，把十课内容分别挂到不同阶段上。",
            "每周复盘一次：我在什么地方开始越来越像自己，而不是像在背别人的答案。",
        ]
        memory = f"课程真正的终点，不是学会复述 {name}，而是形成你自己的行动版公式。"

    return {
        "intro": sentence(intro),
        "cards": cards,
        "bullets": bullets,
        "misreads": misreads,
        "actions": actions,
        "memory": sentence(memory),
        "blueprint": blueprint,
        "lesson": lesson,
        "quote": quote,
        "scenarios": scenarios,
        "question": question,
        "name": name,
        "title": title,
        "tags": tags,
    }


def render_tags(tags: list[str], class_name: str = "tag") -> str:
    return "".join(f'<span class="{class_name}">{escape(tag)}</span>' for tag in tags)


def lesson_title_en(thinker: dict, lesson_number: int) -> str:
    name_en = thinker["name_en"]
    tags = english_pillars(thinker)
    if lesson_number == 1:
        return f"{name_en} System Overview"
    if lesson_number == 2:
        return f"Core Concept I: {tags[0]}"
    if lesson_number == 3:
        return f"Core Concept II: {tags[1]}"
    if lesson_number == 4:
        return f"Core Concept III: {tags[2]}"
    if lesson_number == 5:
        return f"{name_en} Judgment Framework"
    if lesson_number == 6:
        return f"Practice Cases with {name_en}"
    if lesson_number == 7:
        return f"{name_en} Mental Models Toolkit"
    if lesson_number == 8:
        return f"Values and Beliefs of {name_en}"
    if lesson_number == 9:
        return f"{name_en} as an Operating System"
    return f"Integrate {name_en} into Action"


def lesson_subtitle_en(thinker: dict, lesson_number: int) -> str:
    blueprint = COURSE_BLUEPRINT[lesson_number - 1]
    return blueprint["focus_en"]


def render_root_index(catalog: dict) -> str:
    thinkers_by_category: dict[str, list[dict]] = {}
    for thinker in catalog["thinkers"]:
        thinkers_by_category.setdefault(thinker["category_label"], []).append(thinker)

    category_cards = []
    for category in catalog["categories"]:
        category_cards.append(
            f"""
            <article class="domain-card" style="--domain-accent:{category['accent']}">
              <div class="domain-top">
                <div>
                  <strong class="copy-zh">{escape(category['label'])}</strong>
                  <strong class="copy-en">{escape(category['label_en'])}</strong>
                </div>
                <span>{category['count']} minds</span>
              </div>
              <p class="copy-zh">{escape(category['theme'])}</p>
              <p class="copy-en">{escape(category['theme_en'])}</p>
              <small class="copy-zh">{escape(category['signal'])}</small>
              <small class="copy-en">{escape(category['signal_en'])}</small>
            </article>
            """
        )

    blueprint_cards = []
    for item in catalog["blueprint"]:
        blueprint_cards.append(
            f"""
            <article class="blueprint-card">
              <span class="badge">第{item['number']}课</span>
              <strong class="copy-zh">{escape(item['title'])}</strong>
              <strong class="copy-en">{escape(item['title_en'])}</strong>
              <p class="copy-zh">{escape(item['focus'])}</p>
              <p class="copy-en">{escape(item['focus_en'])}</p>
              <small class="copy-zh">{escape(item['deliverable'])}</small>
              <small class="copy-en">{escape(item['deliverable_en'])}</small>
            </article>
            """
        )

    category_sections = []
    for category_label, thinkers in thinkers_by_category.items():
        cards = []
        for thinker in thinkers:
            tags = render_tags(thinker["tags"], "tt")
            cards.append(
                f"""
                <a href="./{thinker['id']}/" class="tc">
                  <div>
                    <b>{escape(thinker['name'])}</b><br>
                    <small class="copy-zh">{escape(thinker['title'])}</small>
                    <small class="copy-en">{escape(thinker['name_en'])}</small><br>
                    {tags}<br>
                    <small class="course-note copy-zh">10门课程 · 1 套完整判断系统</small>
                    <small class="course-note copy-en">10 lessons · one reusable judgment system</small>
                  </div>
                </a>
                """
            )
        category_sections.append(
            f"<h2><span class=\"copy-zh\">{escape(category_label)}</span><span class=\"copy-en\">"
            f"{escape(CATEGORY_LABEL_EN[category_label])}</span></h2><div class=\"thinker-grid\">{''.join(cards)}</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>智者思想课程 — Digital Sage</title>
<link rel="stylesheet" href="assets/course-theme.css">
</head>
<body class="catalog-page" data-lang="dual">
<nav>
  <a href="https://www.digitalsage.cloud/">主站首页</a>
  <a href="./index.html" class="active">思想课程</a>
  <a href="https://www.digitalsage.cloud/3d.html">3D 殿堂</a>
  {render_lang_switch()}
</nav>
<div class="c">
  <section class="hero">
    <h1><span class="copy-zh">🏛️ 智者思想课程</span><span class="copy-en">🏛️ Digital Sage Curriculum</span></h1>
    <p class="copy-zh">100 位智者 × 10 门系统课程。不是碎片摘录，而是从总览、概念、框架、案例到行动的完整学习路径。</p>
    <p class="copy-en">100 minds × 10 structured lessons each. This is not a pile of quotes. It is a full learning arc from overview to concepts, frameworks, cases, and action.</p>
    <div class="stats">
      <div class="stat"><div class="sn">{catalog['stats']['thinkers']}</div><div class="sl"><span class="copy-zh">位思想家</span><span class="copy-en">minds</span></div></div>
      <div class="stat"><div class="sn">{catalog['stats']['lessons']}</div><div class="sl"><span class="copy-zh">门课程</span><span class="copy-en">lessons</span></div></div>
      <div class="stat"><div class="sn">{catalog['stats']['categories']}</div><div class="sl"><span class="copy-zh">大领域</span><span class="copy-en">domains</span></div></div>
    </div>
  </section>

  <section class="spark-system">
    <div class="section-head">
      <div>
        <div class="eyebrow">Spark 2 Curriculum</div>
        <h3><span class="copy-zh">每一位智者，都被拆成同一套 10 课学习系统。</span><span class="copy-en">Every thinker is broken into the same 10-lesson learning system.</span></h3>
      </div>
      <p class="copy-zh">先建立全局地图，再拆三根支柱，接着进入判断框架、实践案例、工具箱、价值系统和行动闭环。课程之间能横向比较，课程内部能纵向深入。</p>
      <p class="copy-en">Start with the whole map, then study the three pillars, then move into judgment order, live cases, mental tools, values, and action. The format stays comparable across all 100 minds.</p>
    </div>
    <div class="blueprint-grid">{''.join(blueprint_cards)}</div>
    <div class="domain-grid">{''.join(category_cards)}</div>
  </section>

  {''.join(category_sections)}
</div>
{LANGUAGE_SWITCH_SCRIPT}
</body>
</html>
"""


def thinker_summary_cards(thinker: dict) -> list[tuple[str, str, str, str]]:
    scenarios = CATEGORY_SCENARIOS[thinker["category"]]
    profile = CURATED_ENGLISH_PROFILES.get(thinker["id"])
    tags_en = english_pillars(thinker)
    return [
        (
            "适合带着什么问题来学",
            "What problem should you bring into the course?",
            f"优先带着这类问题进入：{scenarios[0]}",
            f"Start with a live problem such as this: {scenarios[0]}",
        ),
        (
            "这一套课真正训练什么",
            "What does this curriculum actually train?",
            f"训练你把 {thinker['guiding_question']} 变成稳定的判断起点。",
            profile["throughline"] if profile else f"It trains you to turn this question into a stable starting point: {thinker['guiding_question_en']}",
        ),
        (
            "学完之后能迁移到哪里",
            "Where does it transfer?",
            f"最终不是模仿 {thinker['name']}，而是把 {', '.join(thinker['tags'])} 迁移到你自己的业务和选择。",
            profile["integration_frame"] if profile else f"The goal is not imitation. It is to move {', '.join(tags_en)} into your own work, decisions, and operating rhythm.",
        ),
    ]


def render_thinker_index(thinker: dict) -> str:
    summary_cards = "".join(
        f"""
        <article class="learning-card">
          <strong class="copy-zh">{escape(title_zh)}</strong>
          <strong class="copy-en">{escape(title_en)}</strong>
          <p class="copy-zh">{escape(body_zh)}</p>
          <p class="copy-en">{escape(body_en)}</p>
        </article>
        """
        for title_zh, title_en, body_zh, body_en in thinker_summary_cards(thinker)
    )
    source_cards = "".join(
        f"""
        <article class="source-card">
          <strong class="copy-zh">{escape(item['title_zh'])}</strong>
          <strong class="copy-en">{escape(item['title_en'])}</strong>
          <p class="copy-zh">{escape(item['body_zh'])}</p>
          <p class="copy-en">{escape(item['body_en'])}</p>
        </article>
        """
        for item in thinker_source_tracks(thinker)
    )
    reference_shelf = render_reference_shelf(thinker, "index")
    case_cards = "".join(
        f"""
        <article class="case-card">
          <strong>{escape(case['title'])}</strong>
          <p class="copy-zh">{escape(case['lesson'])}</p>
          <p class="copy-en">{escape('Lesson: ' + case['lesson'])}</p>
          <small class="copy-zh">{escape(case['result'])}</small>
          <small class="copy-en">{escape('Outcome: ' + case['result'])}</small>
        </article>
        """
        for case in thinker["course_doc"]["cases"]
    )
    module_cards = "".join(
        f"""
        <article class="module-card">
          <span class="badge">第{lesson['number']}课</span>
          <strong class="copy-zh">{escape(lesson['title'])}</strong>
          <strong class="copy-en">{escape(lesson_title_en(thinker, lesson['number']))}</strong>
          <p class="copy-zh">{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['focus'])}</p>
          <p class="copy-en">{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['focus_en'])}</p>
          <small class="copy-zh">{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['deliverable'])}</small>
          <small class="copy-en">{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['deliverable_en'])}</small>
        </article>
        """
        for lesson in thinker["lessons"]
    )
    course_cards = "".join(
        f"""
        <a href="{lesson['number']}.html" class="ci-card">
          <div class="ci-num">第{lesson['number']}课</div>
          <div>
            <div class="ci-title copy-zh">{escape(lesson['title'])}</div>
            <div class="ci-title copy-en">{escape(lesson_title_en(thinker, lesson['number']))}</div>
            <div class="ci-sub copy-zh">{escape(lesson['subtitle'])}</div>
            <div class="ci-sub copy-en">{escape(lesson_subtitle_en(thinker, lesson['number']))}</div>
            <div class="mini-note copy-zh">{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['deliverable'])}</div>
            <div class="mini-note copy-en">{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['deliverable_en'])}</div>
          </div>
        </a>
        """
        for lesson in thinker["lessons"]
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(thinker['name'])} · 10门思想课程 — Digital Sage</title>
<link rel="stylesheet" href="../assets/course-theme.css">
</head>
<body class="thinker-page" data-lang="dual">
<div class="container">
  <a href="../index.html" class="back-link">← 返回课程总目录</a>
  {render_lang_switch()}

  <section class="header">
    <h1><span class="copy-zh">{escape(thinker['name'])} · 思想体系</span><span class="copy-en">{escape(thinker['name_en'])} · Curriculum</span></h1>
    <p class="subtitle copy-zh">{escape(thinker['title'])} · 10 门系统课程</p>
    <p class="subtitle copy-en">{escape(thinker['category_label_en'])} · 10 structured lessons</p>
    <div class="tags">{render_tags(thinker['tags'])}</div>
    <p class="signature">"{escape(thinker['quote'])}"</p>
  </section>

  <section class="learning-grid">{summary_cards}</section>

  <section class="spark-system thinker-system">
    <div class="section-head">
      <div>
        <div class="eyebrow">Curriculum Arc</div>
        <h3><span class="copy-zh">{escape(thinker['name'])} 的 10 课，不是知识点列表，而是一条递进学习弧线。</span><span class="copy-en">The 10 lessons for {escape(thinker['name_en'])} form a progression, not a list of quotes.</span></h3>
      </div>
      <p class="copy-zh">前四课建立图谱与三根支柱，第 5 到 7 课把判断框架和工具箱拆开，第 8 到 10 课回到价值系统、可执行方法和个人行动整合。</p>
      <p class="copy-en">The first four lessons build the map and three pillars. Lessons five to seven open up judgment order and tools. The final three return to values, operating method, and integration.</p>
    </div>
    <div class="module-ladder">{module_cards}</div>
  </section>

  {reference_shelf if reference_shelf else f'<section class="source-grid">{source_cards}</section>'}
  <section class="case-grid">{case_cards}</section>

  <div class="course-grid">{course_cards}</div>
</div>
{LANGUAGE_SWITCH_SCRIPT}
</body>
</html>
"""


def render_lesson_page(thinker: dict, lesson_number: int) -> str:
    context = course_contexts(thinker, lesson_number)
    brief_en = english_brief(thinker, lesson_number, context)
    tags_en = english_pillars(thinker)
    lesson = context["lesson"]
    prev_link = f'{lesson_number - 1}.html' if lesson_number > 1 else ""
    next_link = f'{lesson_number + 1}.html' if lesson_number < 10 else ""
    cards = "".join(
        f"""
        <article class="spark-card">
          <strong class="copy-zh">{escape(title)}</strong>
          <strong class="copy-en">{escape(title_en)}</strong>
          <p class="copy-zh">{escape(body)}</p>
          <p class="copy-en">{escape(body_en)}</p>
        </article>
        """
        for (title, body), (title_en, body_en) in zip(context["cards"], brief_en["cards"])
    )
    bullets = "".join(
        f"<li><span class=\"copy-zh\">{escape(item.strip())}</span><span class=\"copy-en\">{escape(en_item.strip())}</span></li>"
        for item, en_item in zip(context["bullets"], brief_en["takeaways"])
    )
    misreads = "".join(
        f"<li><span class=\"copy-zh\">{escape(item.strip())}</span><span class=\"copy-en\">{escape(en_item.strip())}</span></li>"
        for item, en_item in zip(context["misreads"], brief_en["misreads"])
    )
    actions = "".join(
        f"<li><span class=\"copy-zh\">{escape(item.strip())}</span><span class=\"copy-en\">{escape(en_item.strip())}</span></li>"
        for item, en_item in zip(context["actions"], brief_en["actions"])
    )
    scenario_cards = "".join(
        f"""
        <article class="capsule">
          <strong class="copy-zh">应用场景 {index + 1}</strong>
          <strong class="copy-en">Use case {index + 1}</strong>
          <p class="copy-zh">{escape(text)}</p>
          <p class="copy-en">{escape('Translate the framework into a live operating situation and inspect the constraint before moving.')}</p>
        </article>
        """
        for index, text in enumerate(context["scenarios"])
    )
    case_cards = "".join(
        f"""
        <article class="case-card">
          <strong>{escape(case['title'])}</strong>
          <p class="copy-zh">{escape(case['lesson'])}</p>
          <p class="copy-en">{escape('Lesson: ' + case['lesson'])}</p>
          <small class="copy-zh">{escape(case['result'])}</small>
          <small class="copy-en">{escape('Outcome: ' + case['result'])}</small>
        </article>
        """
        for case in thinker["course_doc"]["cases"]
    )
    source_cards = "".join(
        f"""
        <article class="source-card">
          <strong class="copy-zh">{escape(item['title_zh'])}</strong>
          <strong class="copy-en">{escape(item['title_en'])}</strong>
          <p class="copy-zh">{escape(item['body_zh'])}</p>
          <p class="copy-en">{escape(item['body_en'])}</p>
        </article>
        """
        for item in thinker_source_tracks(thinker)
    )
    reference_shelf = render_reference_shelf(thinker, "lesson")
    evidence_items = "".join(
        f"<li><span class=\"copy-zh\">{escape(step)}</span><span class=\"copy-en\">{escape('Verification path: ' + step)}</span></li>"
        for step in thinker["course_doc"]["decision_steps"][:5]
    )
    values_items = "".join(
        f"<li><span class=\"copy-zh\">{escape(value)}</span><span class=\"copy-en\">{escape('Core value: ' + value)}</span></li>"
        for value in thinker["course_doc"]["core_values"][:5]
    )
    positions_items = "".join(
        f"<li><span class=\"copy-zh\">{escape(item['label'])}：{escape(item['body'])}</span>"
        f"<span class=\"copy-en\">{escape(item['label'] + ': ' + item['body'])}</span></li>"
        for item in thinker["course_doc"]["positions"][:5]
    )
    progress_cards = (
        f"""
        <article class="kpi-card">
          <span class="copy-zh">课程定位</span>
          <span class="copy-en">Lesson role</span>
          <strong class="copy-zh">{escape(context['blueprint']['focus'])}</strong>
          <strong class="copy-en">{escape(brief_en['focus'])}</strong>
          <p class="copy-zh">{escape(context['blueprint']['deliverable'])}</p>
          <p class="copy-en">{escape(brief_en['deliverable'])}</p>
        </article>
        <article class="kpi-card">
          <span class="copy-zh">关键追问</span>
          <span class="copy-en">Key opening question</span>
          <strong class="copy-zh">{escape(context['question'])}</strong>
          <strong class="copy-en">{escape(thinker['guiding_question_en'])}</strong>
          <p class="copy-zh">这是 {escape(thinker['name'])} 在复杂问题前会先回到的起点。</p>
          <p class="copy-en">This is the question {escape(thinker['name_en'])} would return to before rushing into action.</p>
        </article>
        <article class="kpi-card">
          <span class="copy-zh">底层支柱</span>
          <span class="copy-en">Core pillars</span>
          <strong class="copy-zh">{escape(' / '.join(thinker['tags']))}</strong>
          <strong class="copy-en">{escape(' / '.join(tags_en))}</strong>
          <p class="copy-zh">课程内容始终围绕这三根支柱组织，而不是零散知识点。</p>
          <p class="copy-en">The lesson is organized around these three pillars rather than isolated quotations.</p>
        </article>
        """
    )
    index_links = "".join(
        f'<a href="{item["number"]}.html" class="{"current" if item["number"] == lesson_number else ""}">第{item["number"]}课</a>'
        for item in thinker["lessons"]
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(lesson['title'])} — {escape(thinker['name'])} · Digital Sage</title>
<link rel="stylesheet" href="../assets/course-theme.css">
</head>
<body class="lesson-page" data-lang="dual">
<div class="container">
  <a href="./index.html" class="back-link">← 返回{escape(thinker['name'])}课程目录</a>
  {render_lang_switch()}

  <section class="course-header">
    <div class="badge">第{lesson_number}课 / 共10课</div>
    <h1><span class="copy-zh">{escape(lesson['title'])}</span><span class="copy-en">{escape(lesson_title_en(thinker, lesson_number))}</span></h1>
    <p class="subtitle copy-zh">{escape(lesson['subtitle'])}</p>
    <p class="subtitle copy-en">{escape(lesson_subtitle_en(thinker, lesson_number))}</p>
    <div class="header-tags">{render_tags([thinker['category_label'], *thinker['tags'][:2]])}</div>
  </section>

  <div class="audio-player">
    <span class="audio-label">🎙️ 语音讲解</span>
    <audio controls preload="none" src="audio/{lesson_number}.mp3"></audio>
  </div>

  <section class="lesson-kpis">{progress_cards}</section>

  <section class="section">
    <h2><span class="copy-zh">本课解决什么问题</span><span class="copy-en">What this lesson solves</span></h2>
    <p class="copy-zh">{escape(context['intro'])}</p>
    <p class="copy-en">{escape(brief_en['summary'])}</p>
    <p class="copy-zh">{escape(lesson['summary'])}</p>
    <p class="copy-en">{escape(brief_en['lesson_note'])}</p>
  </section>

  <section class="spark-grid">{cards}</section>

  <section class="section">
    <h2><span class="copy-zh">判断清单</span><span class="copy-en">Judgment checklist</span></h2>
    <ul class="bullet-list">{bullets}</ul>
  </section>

  <section class="capsule-grid">{scenario_cards}</section>

  <section class="section">
    <h2><span class="copy-zh">常见误区</span><span class="copy-en">Common misreads</span></h2>
    <ul class="bullet-list subtle-list">{misreads}</ul>
  </section>

  {reference_shelf if reference_shelf else f'<section class="source-grid">{source_cards}</section>'}
  <section class="case-grid">{case_cards}</section>

  <section class="detail-dual-grid">
    <article class="section">
      <h2><span class="copy-zh">证据锚点</span><span class="copy-en">Evidence anchors</span></h2>
      <ul class="bullet-list">{evidence_items}</ul>
    </article>
    <article class="section">
      <h2><span class="copy-zh">价值与原则</span><span class="copy-en">Values and principles</span></h2>
      <ul class="bullet-list">{values_items}</ul>
    </article>
    <article class="section">
      <h2><span class="copy-zh">关键立场</span><span class="copy-en">Core positions</span></h2>
      <ul class="bullet-list">{positions_items}</ul>
    </article>
  </section>

  <section class="section memory-line">
    <h2><span class="copy-zh">一句话记住</span><span class="copy-en">Memory line</span></h2>
    <p class="copy-zh">{escape(context['memory'])}</p>
    <p class="copy-en">{escape('Remember the operating sentence, not just the quote. The lesson works only when it changes how you order attention.')}</p>
  </section>

  <section class="section">
    <h2><span class="copy-zh">课后动作</span><span class="copy-en">Next actions</span></h2>
    <ol class="action-list">{actions}</ol>
  </section>

  <div class="course-nav">
    {f'<a href="{prev_link}">← 上一课</a>' if prev_link else '<span class="disabled">← 上一课</span>'}
    <div class="course-index">{index_links}</div>
    {f'<a href="{next_link}">下一课 →</a>' if next_link else '<span class="disabled">下一课 →</span>'}
  </div>
</div>
{LANGUAGE_SWITCH_SCRIPT}
</body>
</html>
"""


def render_catalog_json(catalog: dict) -> dict:
    categories = {item["id"]: item for item in catalog["categories"]}
    featured_ids = set(catalog.get("featured_ids", []))
    thinkers = []
    for thinker in catalog["thinkers"]:
        thinkers.append(
            {
                "id": thinker["id"],
                "name": thinker["name"],
                "name_en": thinker["name_en"],
                "title": thinker["title"],
                "quote": thinker["quote"],
                "guiding_question": thinker["guiding_question"],
                "guiding_question_en": thinker["guiding_question_en"],
                "formula": thinker["formula"],
                "tags": thinker["tags"],
                "category": thinker["category"],
                "category_label": thinker["category_label"],
                "category_label_en": thinker["category_label_en"],
                "category_theme": thinker["category_theme"],
                "category_theme_en": thinker["category_theme_en"],
                "category_signal": thinker["category_signal"],
                "category_signal_en": thinker["category_signal_en"],
                "accent": thinker["accent"],
                "featured": thinker["id"] in featured_ids,
                "priority_curated": thinker_is_priority_curated(thinker),
                "index_url": f"/courses/{thinker['id']}/",
                "source_tracks": thinker_source_tracks(thinker),
                "reference_shelf": thinker_reference_bundle(thinker),
                "case_notes": thinker["course_doc"]["cases"],
                "lessons": [
                    {
                        "number": lesson["number"],
                        "title": lesson["title"],
                        "title_en": lesson_title_en(thinker, lesson["number"]),
                        "subtitle": lesson["subtitle"],
                        "subtitle_en": lesson_subtitle_en(thinker, lesson["number"]),
                        "summary": lesson["summary"],
                        "page_url": f"/courses/{thinker['id']}/{lesson['number']}.html",
                        "focus": COURSE_BLUEPRINT[lesson["number"] - 1]["focus"],
                        "focus_en": COURSE_BLUEPRINT[lesson["number"] - 1]["focus_en"],
                        "deliverable": COURSE_BLUEPRINT[lesson["number"] - 1]["deliverable"],
                        "deliverable_en": COURSE_BLUEPRINT[lesson["number"] - 1]["deliverable_en"],
                    }
                    for lesson in thinker["lessons"]
                ],
            }
        )
    return {
        "version": catalog["version"],
        "stats": catalog["stats"],
        "blueprint": catalog["blueprint"],
        "categories": catalog["categories"],
        "featured_ids": catalog.get("featured_ids", []),
        "thinkers": thinkers,
        "category_map": categories,
    }


def write_outputs(catalog: dict) -> None:
    ROOT_INDEX.write_text(render_root_index(catalog), encoding="utf-8")
    CATALOG_PATH.write_text(
        json.dumps(render_catalog_json(catalog), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for thinker in catalog["thinkers"]:
        thinker_dir = BASE_DIR / thinker["id"]
        thinker_dir.mkdir(parents=True, exist_ok=True)
        (thinker_dir / "index.html").write_text(render_thinker_index(thinker), encoding="utf-8")
        for lesson in thinker["lessons"]:
            lesson_path = thinker_dir / f"{lesson['number']}.html"
            lesson_path.write_text(render_lesson_page(thinker, lesson["number"]), encoding="utf-8")


def main() -> None:
    catalog = bootstrap_catalog()
    write_outputs(catalog)
    print(
        f"Generated course catalog for {catalog['stats']['thinkers']} thinkers and "
        f"{catalog['stats']['lessons']} lessons."
    )


if __name__ == "__main__":
    main()
