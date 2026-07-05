# annotatia 项目总结

## 目标

用 Python + pykakasi 将日语文本中的汉字转为平假名读音，生成带 `\ruby{}` 注音的 `.tex` 文件，支持歌词文件 (.lrc) 特殊处理。

## 迭代过程

1. **核心功能** — pykakasi 分词，汉字段包裹 `\ruby{}{}`，非汉字原样输出
2. **CLI 参数** — `--engine`（xelatex/pdflatex/lualatex）、`--template`（完整文档模板）
3. **居中对齐 & 行距** — `--center`、`--linespread`
4. **LRC 歌词支持** — 自动检测 `.lrc` 扩展名，剥离时间戳 `[mm:ss.xxx]`，默认启用 `--center --linespread 1.5 --hr`
5. **强制覆盖** — `--center`/`--hr` 改为 `BooleanOptionalAction`，支持 `--no-center`/`--no-hr`
6. **自动换行** — 改用 `\n\n` 段落分隔替代 `\\` 换行，长句自动折行
7. **句间横线** — `--hr` 在句与句之间插入 `\rule{0.6\linewidth}{0.4pt}`
8. **双列排版** — `--twocolumn`，基于 `multicol` 包
9. **项目描述** — `pyproject.toml`（PEP 621，setuptools + entry point）
10. **Arch 打包** — `PKGBUILD`（`file://` 引用本地源，`python -m build` + `installer`）
11. **文档** — `README.md`、`SUMMARY.md`

## 关键技术决策

- **pykakasi 2.3.0 bug 规避**：逐行处理文本，避免 `\n` 后复制前序 segment
- **整词注音**：尊重 pykakasi 分词结果，不拆单字
- **汉字检测**：仅 CJK Unified Ideograph 范围（`\u4e00-\u9fff`）触发注音，片假名外来语跳过
- **段落 vs 换行**：`\n\n` 段落分隔确保自动折行，同时支持空行分段（歌词段落间隔）
- **模板三引擎**：xelatex（默认，xeCJK + 自定义 `\ruby` 宏）、pdflatex（CJK + ruby.sty）、lualatex（luatexja + luatexja-ruby）

## 项目结构

```
├── pyproject.toml          # Python 项目配置 (PEP 621)
├── PKGBUILD                # Arch Linux 打包脚本
├── README.md               # 用户文档
├── SUMMARY.md              # 本文件
├── src/
│   └── annotatia.py        # 主脚本 (203行)
├── .opencode/
│   └── plans/
│       └── ANNOTATE_PLAN.md # 设计文档
└── *.lrc                   # 测试用歌词文件
```

## 构建与安装

```bash
pip install .                        # Python
makepkg -si                          # Arch Linux
```
