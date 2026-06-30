# 红楼梦知识图谱

《红楼梦知识图谱》是一个从小规模试点开始的古典小说知识库。首版聚焦前五回：把正文做成带实体高亮的阅读器，同时抽取人物、地点、府系、身份、物件、诗文、概念、时间、事件和关系，生成可浏览的静态知识图谱页面。

在线站点发布在 GitHub Pages：

- https://gigode.de/hongloumeng-kb/
- `docs/chapters/001.html`
- `docs/entities/person.html`
- `docs/graph/index.html`

## 当前范围

- 文本来源：维基文库《红楼梦》章节页，生成时记录在 `data/chapters.json`。
- 试点章节：第 1-5 回。
- 高亮类型：人物、地点、府系、身份、物件、诗文、概念、时间。
- 分类页面：每类实体都有统计、关系读法、详细注释和资料依据。
- 图谱内容：基础人物关系、府系关系、居住/携带/出场关系、事件参与关系。
- 发布方式：纯静态 HTML/CSS/JS，适合 GitHub Pages。

## 资料依据

第一版注释主要参考：

- 维基文库《红楼梦》文本与回目。
- 维基百科条目：金陵十二钗、贾宝玉、王熙凤。
- 《红楼梦》多维叙事视角研究。
- 大观园隐喻相关论文。
- 《红楼梦》兼美论人物关系研究。

这些资料统一整理在 `data/notes.json`，页面生成器会读取它来生成分类说明和实体注释。

## 目录

```text
texts/raw/       抓取和分段后的正文
texts/tagged/    自动标注后的 Markdown
data/            实体、事件、关系、图谱、注释 JSON
scripts/         抓取、标注、索引、验证、渲染脚本
docs/            GitHub Pages 静态站点
tests/           pytest 测试
```

## 重新生成

在这台机器上优先使用 Scoop Python：

```powershell
$py = "C:\Users\zm_ji\scoop\apps\python\current\python.exe"
& $py -m pip install -e ".[dev]"
& $py scripts/fetch_wikisource.py --chapters 5 --insecure
& $py scripts/annotate_pilot.py
& $py scripts/build_entity_index.py
& $py scripts/validate_graph_data.py
& $py scripts/build_graph.py
& $py scripts/render_site.py
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
& $py -m pytest -v
```

`--insecure` 只用于当前 Windows Python 证书链异常时抓取公开文本；证书正常的环境可去掉。`PYTEST_DISABLE_PLUGIN_AUTOLOAD` 用于避开本机全局 pytest 插件和 Python 3.14 的兼容问题。

## 已知限制

- 标注仍是首轮自动标注，优先覆盖高价值实体和主题短语，不追求全量。
- 事件和关系以首版展示为目标，采用人工整理的核心关系，后续再扩大和校验。
- 本项目先不引入 Neo4j、RDF、全量 wiki 或复杂推理。

## 许可

《红楼梦》原文为公有领域文本。项目生成的数据、脚本和页面暂按 MIT 许可准备；正式发布前可再根据用途调整。
