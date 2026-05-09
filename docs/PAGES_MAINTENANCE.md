# GitHub Pages 维护说明

## 当前发布形态

- GitHub 仓库：`MoKangMedical/digital-sage-courses`
- GitHub Pages：`https://mokangmedical.github.io/digital-sage-courses/`
- 主站入口：`https://digitalsage.cloud/courses/`

当前 GitHub Pages 使用：

- 分支：`main`
- 路径：`/`
- HTTPS：开启

## 域名策略

这个仓库当前**不应该**放 `CNAME` 文件。

原因很简单：

- GitHub Pages 自定义域名是站点级的，只适合根域名或子域名
- 现在对外正式入口是 `digitalsage.cloud/courses/`
- 这是主站对课程仓库做的路径级接入，不是 GitHub Pages 原生的自定义域名绑定

所以当前推荐策略是：

1. GitHub Pages 继续保持官方地址：`mokangmedical.github.io/digital-sage-courses`
2. 主站继续把 `/courses/` 指向这一套静态课程资源
3. 如果未来要独立成子域名，例如 `courses.digitalsage.cloud`，再新增 `CNAME`

## 每次课程重新生成后的标准收尾

在仓库根目录执行：

```bash
python3 tools/refresh_courses_site.py
```

这一步会自动完成三件事：

1. 删除 `.DS_Store` 和 `._*` 这类 macOS 垃圾文件
2. 把课程总站、智者索引页、单课详情页统一切到共享主题
3. 修正 GitHub Pages / 主站双场景都能工作的相对链接

## 发布前检查

建议至少检查这几项：

```bash
find . -name '.DS_Store' -o -name '._*'
find . -name '*.html' | wc -l
find . -name '*.mp3' | wc -l
```

然后手动打开：

- `/index.html`
- 任意一个 `某智者/index.html`
- 任意一个 `某智者/1.html`

确认：

- 样式已统一
- 返回链接正常
- 音频播放器正常
- 相对路径在 GitHub Pages 下可访问

## 建议提交范围

一次正常的课程内容更新，通常只会包含：

- 课程 HTML 页面
- `audio/*.mp3`
- `audio_texts.json`
- `assets/course-theme.css`
- `tools/refresh_courses_site.py`
- `README.md` / 本文档

如果又出现 `._*` 这类文件，说明生成或打包过程又混入了 Finder 资源分叉，需要先清理再提交。
