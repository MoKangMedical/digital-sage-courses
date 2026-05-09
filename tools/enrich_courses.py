from __future__ import annotations

import json
import re
import subprocess
from html import escape
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
CATALOG_PATH = ASSETS_DIR / "course-catalog.json"
ROOT_INDEX = BASE_DIR / "index.html"


CATEGORY_INFO = {
    "商业领袖": {
        "id": "business",
        "theme": "资本配置、增长纪律与组织杠杆",
        "signal": "用现金流、护城河和长期配置去看真正的企业质量。",
        "accent": "#2563eb",
    },
    "科技思想家": {
        "id": "technology",
        "theme": "技术路线、平台势能与工程判断",
        "signal": "从底层技术演进、分发与规模化约束去看产品机会。",
        "accent": "#0f766e",
    },
    "设计大师": {
        "id": "design",
        "theme": "体验秩序、材料语言与审美取舍",
        "signal": "把抽象理念压缩成可触达、可感知、可复用的设计语言。",
        "accent": "#7c3aed",
    },
    "科学家": {
        "id": "science",
        "theme": "假设、证据与长期发现",
        "signal": "从问题定义、实验设计和证据质量出发搭建认知。",
        "accent": "#0891b2",
    },
    "医学专家": {
        "id": "medical",
        "theme": "风险识别、临床判断与系统防控",
        "signal": "先排危险，再看证据，再决定行动优先级。",
        "accent": "#db2777",
    },
    "思想家": {
        "id": "philosophy",
        "theme": "价值系统、意义建构与判断框架",
        "signal": "把复杂现实压缩成能反复调用的原则与提问方式。",
        "accent": "#b45309",
    },
    "文化创作者": {
        "id": "culture",
        "theme": "叙事张力、审美结构与人性观察",
        "signal": "把经验转译成作品，把作品再转译成理解世界的方法。",
        "accent": "#c2410c",
    },
    "公共治理": {
        "id": "policy",
        "theme": "制度设计、协同治理与长期稳定",
        "signal": "看清利益结构、执行路径和长期秩序的代价。",
        "accent": "#475569",
    },
}


COURSE_BLUEPRINT = [
    {"number": 1, "title": "思想体系总览", "focus": "建立全局图谱", "deliverable": "一张可复述的总地图"},
    {"number": 2, "title": "核心概念①", "focus": "抓第一根支柱", "deliverable": "识别最重要的概念变量"},
    {"number": 3, "title": "核心概念②", "focus": "抓第二根支柱", "deliverable": "理解概念之间如何联动"},
    {"number": 4, "title": "核心概念③", "focus": "抓第三根支柱", "deliverable": "补齐这套系统的边界条件"},
    {"number": 5, "title": "判断框架", "focus": "学会怎么判断", "deliverable": "一套可迁移的决策顺序"},
    {"number": 6, "title": "实践案例", "focus": "看思想如何落地", "deliverable": "把抽象原则映射到真实场景"},
    {"number": 7, "title": "思维模型工具箱", "focus": "提炼可复用工具", "deliverable": "一组随时可调用的模型"},
    {"number": 8, "title": "价值体系与信仰", "focus": "回到底层信念", "deliverable": "分清原则与技巧的层级"},
    {"number": 9, "title": "方法论·可操作系统", "focus": "把理解变成动作", "deliverable": "一套 30 天可执行的方法"},
    {"number": 10, "title": "整合与行动", "focus": "完成知识闭环", "deliverable": "形成自己的行动版公式"},
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


def build_lesson_cards(thinker_dir: Path, thinker_html: str, audio_texts: dict) -> list[dict]:
    cards = sorted(
        (
            {
                "number": int(number),
                "title": strip_html(title_text),
                "subtitle": strip_html(subtitle_text),
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
                "subtitle": strip_html(subtitle_match.group(1)) if subtitle_match else blueprint["focus"],
                "summary": audio_texts.get(str(lesson_number), ""),
            }
        )
    return cards


def bootstrap_catalog() -> dict:
    root_html = load_bootstrap_root_html()
    thinkers: list[dict] = []
    category_counts: dict[str, int] = {}

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

            thinker = {
                "id": slug,
                "name": strip_html(name),
                "title": strip_html(title),
                "quote": signature,
                "guiding_question": guiding_question,
                "formula": formula,
                "category": category_meta["id"],
                "category_label": category_label,
                "category_theme": category_meta["theme"],
                "category_signal": category_meta["signal"],
                "accent": category_meta["accent"],
                "tags": tags[:3],
                "lessons": lesson_cards,
            }
            thinkers.append(thinker)
            category_counts[category_meta["id"]] = category_counts.get(category_meta["id"], 0) + 1

    categories = []
    for label, info in CATEGORY_INFO.items():
        categories.append(
            {
                "id": info["id"],
                "label": label,
                "theme": info["theme"],
                "signal": info["signal"],
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
        "version": 4,
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
        if data.get("version", 0) >= 4 and thinkers and has_lessons:
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
                <strong>{escape(category['label'])}</strong>
                <span>{category['count']} 位智者</span>
              </div>
              <p>{escape(category['theme'])}</p>
              <small>{escape(category['signal'])}</small>
            </article>
            """
        )

    blueprint_cards = []
    for item in catalog["blueprint"]:
        blueprint_cards.append(
            f"""
            <article class="blueprint-card">
              <span class="badge">第{item['number']}课</span>
              <strong>{escape(item['title'])}</strong>
              <p>{escape(item['focus'])}</p>
              <small>{escape(item['deliverable'])}</small>
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
                    <small>{escape(thinker['title'])}</small><br>
                    {tags}<br>
                    <small class="course-note">10门课程 · 1 套完整判断系统</small>
                  </div>
                </a>
                """
            )
        category_sections.append(f"<h2>{escape(category_label)}</h2><div class=\"thinker-grid\">{''.join(cards)}</div>")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>智者思想课程 — Digital Sage</title>
<link rel="stylesheet" href="assets/course-theme.css">
</head>
<body class="catalog-page">
<nav>
  <a href="https://www.digitalsage.cloud/">主站首页</a>
  <a href="./index.html" class="active">思想课程</a>
  <a href="https://www.digitalsage.cloud/3d.html">3D 殿堂</a>
</nav>
<div class="c">
  <section class="hero">
    <h1>🏛️ 智者思想课程</h1>
    <p>100 位智者 × 10 门系统课程。不是碎片摘录，而是从总览、概念、框架、案例到行动的完整学习路径。</p>
    <div class="stats">
      <div class="stat"><div class="sn">{catalog['stats']['thinkers']}</div><div class="sl">位思想家</div></div>
      <div class="stat"><div class="sn">{catalog['stats']['lessons']}</div><div class="sl">门课程</div></div>
      <div class="stat"><div class="sn">{catalog['stats']['categories']}</div><div class="sl">大领域</div></div>
    </div>
  </section>

  <section class="spark-system">
    <div class="section-head">
      <div>
        <div class="eyebrow">Spark 2 Curriculum</div>
        <h3>每一位智者，都被拆成同一套 10 课学习系统。</h3>
      </div>
      <p>先建立全局地图，再拆三根支柱，接着进入判断框架、实践案例、工具箱、价值系统和行动闭环。课程之间能横向比较，课程内部能纵向深入。</p>
    </div>
    <div class="blueprint-grid">{''.join(blueprint_cards)}</div>
    <div class="domain-grid">{''.join(category_cards)}</div>
  </section>

  {''.join(category_sections)}
</div>
</body>
</html>
"""


def thinker_summary_cards(thinker: dict) -> list[tuple[str, str]]:
    scenarios = CATEGORY_SCENARIOS[thinker["category"]]
    return [
        ("适合带着什么问题来学", f"优先带着这类问题进入：{scenarios[0]}"),
        ("这一套课真正训练什么", f"训练你把 {thinker['guiding_question']} 变成稳定的判断起点。"),
        ("学完之后能迁移到哪里", f"最终不是模仿 {thinker['name']}，而是把 {', '.join(thinker['tags'])} 迁移到你自己的业务和选择。"),
    ]


def render_thinker_index(thinker: dict) -> str:
    summary_cards = "".join(
        f"""
        <article class="learning-card">
          <strong>{escape(title)}</strong>
          <p>{escape(body)}</p>
        </article>
        """
        for title, body in thinker_summary_cards(thinker)
    )
    module_cards = "".join(
        f"""
        <article class="module-card">
          <span class="badge">第{lesson['number']}课</span>
          <strong>{escape(lesson['title'])}</strong>
          <p>{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['focus'])}</p>
          <small>{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['deliverable'])}</small>
        </article>
        """
        for lesson in thinker["lessons"]
    )
    course_cards = "".join(
        f"""
        <a href="{lesson['number']}.html" class="ci-card">
          <div class="ci-num">第{lesson['number']}课</div>
          <div>
            <div class="ci-title">{escape(lesson['title'])}</div>
            <div class="ci-sub">{escape(lesson['subtitle'])}</div>
            <div class="mini-note">{escape(COURSE_BLUEPRINT[lesson['number'] - 1]['deliverable'])}</div>
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
<body class="thinker-page">
<div class="container">
  <a href="../index.html" class="back-link">← 返回课程总目录</a>

  <section class="header">
    <h1>{escape(thinker['name'])} · 思想体系</h1>
    <p class="subtitle">{escape(thinker['title'])} · 10 门系统课程</p>
    <div class="tags">{render_tags(thinker['tags'])}</div>
    <p class="signature">"{escape(thinker['quote'])}"</p>
  </section>

  <section class="learning-grid">{summary_cards}</section>

  <section class="spark-system thinker-system">
    <div class="section-head">
      <div>
        <div class="eyebrow">Curriculum Arc</div>
        <h3>{escape(thinker['name'])} 的 10 课，不是知识点列表，而是一条递进学习弧线。</h3>
      </div>
      <p>前四课建立图谱与三根支柱，第 5 到 7 课把判断框架和工具箱拆开，第 8 到 10 课回到价值系统、可执行方法和个人行动整合。</p>
    </div>
    <div class="module-ladder">{module_cards}</div>
  </section>

  <div class="course-grid">{course_cards}</div>
</div>
</body>
</html>
"""


def render_lesson_page(thinker: dict, lesson_number: int) -> str:
    context = course_contexts(thinker, lesson_number)
    lesson = context["lesson"]
    prev_link = f'{lesson_number - 1}.html' if lesson_number > 1 else ""
    next_link = f'{lesson_number + 1}.html' if lesson_number < 10 else ""
    cards = "".join(
        f"""
        <article class="spark-card">
          <strong>{escape(title)}</strong>
          <p>{escape(body)}</p>
        </article>
        """
        for title, body in context["cards"]
    )
    bullets = "".join(f"<li>{escape(item.strip())}</li>" for item in context["bullets"])
    misreads = "".join(f"<li>{escape(item.strip())}</li>" for item in context["misreads"])
    actions = "".join(f"<li>{escape(item.strip())}</li>" for item in context["actions"])
    scenario_cards = "".join(
        f"""
        <article class="capsule">
          <strong>应用场景 {index + 1}</strong>
          <p>{escape(text)}</p>
        </article>
        """
        for index, text in enumerate(context["scenarios"])
    )
    progress_cards = (
        f"""
        <article class="kpi-card">
          <span>课程定位</span>
          <strong>{escape(context['blueprint']['focus'])}</strong>
          <p>{escape(context['blueprint']['deliverable'])}</p>
        </article>
        <article class="kpi-card">
          <span>关键追问</span>
          <strong>{escape(context['question'])}</strong>
          <p>这是 {escape(thinker['name'])} 在复杂问题前会先回到的起点。</p>
        </article>
        <article class="kpi-card">
          <span>底层支柱</span>
          <strong>{escape(' / '.join(thinker['tags']))}</strong>
          <p>课程内容始终围绕这三根支柱组织，而不是零散知识点。</p>
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
<body class="lesson-page">
<div class="container">
  <a href="./index.html" class="back-link">← 返回{escape(thinker['name'])}课程目录</a>

  <section class="course-header">
    <div class="badge">第{lesson_number}课 / 共10课</div>
    <h1>{escape(lesson['title'])}</h1>
    <p class="subtitle">{escape(lesson['subtitle'])}</p>
    <div class="header-tags">{render_tags([thinker['category_label'], *thinker['tags'][:2]])}</div>
  </section>

  <div class="audio-player">
    <span class="audio-label">🎙️ 语音讲解</span>
    <audio controls preload="none" src="audio/{lesson_number}.mp3"></audio>
  </div>

  <section class="lesson-kpis">{progress_cards}</section>

  <section class="section">
    <h2>本课解决什么问题</h2>
    <p>{escape(context['intro'])}</p>
    <p>{escape(lesson['summary'])}</p>
  </section>

  <section class="spark-grid">{cards}</section>

  <section class="section">
    <h2>判断清单</h2>
    <ul class="bullet-list">{bullets}</ul>
  </section>

  <section class="capsule-grid">{scenario_cards}</section>

  <section class="section">
    <h2>常见误区</h2>
    <ul class="bullet-list subtle-list">{misreads}</ul>
  </section>

  <section class="section memory-line">
    <h2>一句话记住</h2>
    <p>{escape(context['memory'])}</p>
  </section>

  <section class="section">
    <h2>课后动作</h2>
    <ol class="action-list">{actions}</ol>
  </section>

  <div class="course-nav">
    {f'<a href="{prev_link}">← 上一课</a>' if prev_link else '<span class="disabled">← 上一课</span>'}
    <div class="course-index">{index_links}</div>
    {f'<a href="{next_link}">下一课 →</a>' if next_link else '<span class="disabled">下一课 →</span>'}
  </div>
</div>
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
                "title": thinker["title"],
                "quote": thinker["quote"],
                "guiding_question": thinker["guiding_question"],
                "formula": thinker["formula"],
                "tags": thinker["tags"],
                "category": thinker["category"],
                "category_label": thinker["category_label"],
                "category_theme": thinker["category_theme"],
                "category_signal": thinker["category_signal"],
                "accent": thinker["accent"],
                "featured": thinker["id"] in featured_ids,
                "index_url": f"/courses/{thinker['id']}/",
                "lessons": [
                    {
                        "number": lesson["number"],
                        "title": lesson["title"],
                        "subtitle": lesson["subtitle"],
                        "summary": lesson["summary"],
                        "page_url": f"/courses/{thinker['id']}/{lesson['number']}.html",
                        "focus": COURSE_BLUEPRINT[lesson["number"] - 1]["focus"],
                        "deliverable": COURSE_BLUEPRINT[lesson["number"] - 1]["deliverable"],
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
