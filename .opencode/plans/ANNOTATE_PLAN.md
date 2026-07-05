# 日语汉字→平假名注音 + LaTeX `\ruby{}` 生成脚本

## 目标

用 Python + [pykakasi](https://pypi.org/project/pykakasi/) 将日语文本中的汉字转为平假名读音，生成 `.tex` 文件，用 `\ruby{漢字}{よみ}` 命令为汉字注音。

---

## 用法

```bash
python3 annotate.py [选项] [输入文件]

选项:
  -o, --output FILE  输出 .tex 文件（默认 stdout）
  --engine {xelatex,pdflatex,lualatex} 目标 TeX 引擎（默认 xelatex）
  --template         输出完整 LaTeX 文档（含 \documentclass{} 等）
  -h, --help         显示帮助

输入:
  未指定文件时从 stdin 读取
```

---

## 处理流程

```
输入文本
    │
    ▼
pykakasi.kakasi().convert(text)
    │  返回 [{'orig':..., 'hira':...}, ...]
    ▼
遍历每个 segment:
    ├─ orig == hira          → 纯假名/符号 → 原样输出
    ├─ orig 含 CJK 表意文字  → \ruby{orig}{hira}
    └─ 不含汉字              → 原样输出（如外来语「コンピュータ」）
    │
    ▼
拼接为 LaTeX 字符串
    │
    ▼
若 --template: 嵌入 preamble + postamble
    │
    ▼
输出到文件 / stdout
```

### 注音粒度

- **整词注音**：pykakasi 自动分词，不会拆成单字。
- 例：`読み物` → `\ruby{読み物}{よみもの}`（而不是逐字 `\ruby{読}{よ}\ruby{み}{み}\ruby{物}{もの}`）

---

## TeX 模板

### `--engine xelatex`（默认，推荐）

```latex
\documentclass{article}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Noto Sans CJK JP}
\newcommand{\ruby}[2]{\leavevmode\vtop{\ialign{\hfil##\hfil\cr\scriptsize #2\cr\noalign{\kern-0.5ex}#1\cr}}}
\begin{document}
<注音内容>
\end{document}
```

编译：`xelatex sample.tex`

### `--engine pdflatex`

```latex
\documentclass{article}
\usepackage{CJK}
\usepackage{ruby}
\begin{CJK}{UTF8}{min}
\begin{document}
<注音内容>
\end{document}
\end{CJK}
```

编译：`pdflatex sample.tex`

### `--engine lualatex`

```latex
\documentclass{article}
\usepackage{luatexja}
\usepackage{luatexja-ruby}
\begin{document}
<注音内容>
\end{document}
```

编译：`lualatex sample.tex`

---

## 边界情况

| 情况 | 处理 |
|---|---|
| 纯平假名 / 片假名 | 原样输出，不注音 |
| 汉字 + 送り仮名（読み物） | 整词注音：`\ruby{読み物}{よみもの}` |
| 片假名外来语 | 不注音（无汉字） |
| 英文 / 数字 / 标点 | 保留原样 |
| 空输入 | 输出空文件 |

---

## 文件清单

| 文件 | 说明 |
|---|---|
| `annotate.py` | 主脚本 |
| `.opencode/plans/ANNOTATE_PLAN.md` | 本计划 |

---

## 技术栈

- Python 3 + `pykakasi` 2.x — 汉字→假名转换
- LaTeX
  - **XeLaTeX**（默认）：`xeCJK` + 自定义 `\ruby` 宏，支持系统字体（Noto CJK）
  - **pdfLaTeX**：`CJK` + `ruby.sty` 传统方案
  - **LuaLaTeX**：`luatexja` + `luatexja-ruby` 现代方案
