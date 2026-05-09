# 🏛️ Digital Sage — 100位智者思想课程

> 每位智者 10 门系统课程，共 1000 门课，全部配有中文语音讲解。

## 正式入口

- 课程主页：https://digitalsage.cloud/courses/
- GitHub Pages：https://mokangmedical.github.io/digital-sage-courses/
- 主站：https://www.digitalsage.cloud/

## 当前仓库职责

这个仓库只负责课程静态内容：

- 课程总站首页
- 每位智者的 10 门课程页
- 所有 MP3 语音讲解
- GitHub Pages 静态发布

视觉主题与页面收尾统一由下面这个脚本负责：

```bash
python3 tools/refresh_courses_site.py
```

## 课程体系

每门课结构：
1. 思想体系总览
2. 核心概念①
3. 核心概念②
4. 核心概念③
5. 判断框架（4步决策法）
6. 实践案例
7. 思维模型工具箱
8. 价值体系与信仰
9. 方法论·可操作系统
10. 整合与行动

## 思想家分类

| 领域 | 人数 |
|------|:--:|
| 商业领袖 | 20 |
| 科技思想家 | 15 |
| 设计大师 | 7 |
| 科学家 | 17 |
| 医学专家 | 10 |
| 思想家 | 20 |
| 文化创作者 | 4 |
| 公共治理 | 9 |

## 访问

- 主站：https://www.digitalsage.cloud/
- 课程：https://digitalsage.cloud/courses/
- 3D殿堂：https://www.digitalsage.cloud/3d.html
- GitHub Pages：https://mokangmedical.github.io/digital-sage-courses/

## 技术

- 每门课含 HTML 课程页面 + MP3 语音讲解
- 语音由 edge-tts 生成（zh-CN-YunxiNeural）
- 共 1000 个 MP3 文件，约 150MB
- 页面统一主题：`assets/course-theme.css`
- 页面收尾脚本：`tools/refresh_courses_site.py`

## Pages 维护

GitHub Pages / 域名策略 / 发布检查见：

- `docs/PAGES_MAINTENANCE.md`
