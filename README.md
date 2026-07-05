# annotatia

日语汉字注音 LaTeX 生成器。将日语文本中的汉字转为平假名读音，输出带 `\ruby{}` 注音的 `.tex` 文件。
(a product of vibe-coding)
## 安装

```bash
# pip 安装
pip install .

# Arch Linux (PKGBUILD)
makepkg -si
```

依赖：`python`、`pykakasi`

## 用法

```bash
annotatia [选项] [输入文件]

# 从文件
annotatia input.txt -o output.tex

# 从 stdin
echo "日本語を読む" | annotatia

# 输出完整 LaTeX 文档
annotatia input.txt --template -o output.tex
xelatex output.tex
```

## 选项

| 参数 | 说明 |
|---|---|
| `-o, --output FILE` | 输出文件（默认 stdout） |
| `--engine {xelatex,pdflatex,lualatex}` | TeX 引擎（默认 xelatex） |
| `--template` | 输出完整 LaTeX 文档（含 `\documentclass{}`） |
| `--center / --no-center` | 居中对齐 |
| `--linespread N` | 行距倍数，如 `--linespread 1.5` |
| `--hr / --no-hr` | 句间插入细横线 |
| `--twocolumn / --no-twocolumn` | 双列排版 |
| `--lrc` | LRC 歌词模式（自动启用 `--center --linespread 1.5 --hr`，剥离时间戳） |

### LRC 歌词文件

`.lrc` 文件自动识别，无需显式 `--lrc`。可单独覆盖：

```bash
# .lrc 文件默认居中+横线+1.5倍行距
annotatia song.lrc --template

# 关闭居中、关闭横线
annotatia song.lrc --template --no-center --no-hr
```

## LaTeX 模板

### XeLaTeX（默认）

```latex
\documentclass{article}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont{Noto Sans CJK JP}
\newcommand{\ruby}[2]{...}
\begin{document}
\ruby{日本語}{にほんご}を読む
\end{document}
```

编译：`xelatex file.tex`

### pdfLaTeX

```latex
\documentclass{article}
\usepackage{CJK}
\usepackage{ruby}
\begin{CJK}{UTF8}{min}
\begin{document}
...
\end{document}
\end{CJK}
```

### LuaLaTeX

```latex
\documentclass{article}
\usepackage{luatexja}
\usepackage{luatexja-ruby}
\begin{document}
...
\end{document}
```

## 注音规则

- 整词注音（pykakasi 自动分词），不拆单字
- 纯假名/片假名/标点/英文原样输出
- 不含汉字的词（外来语等）不注音

## 项目文件

```
├── pyproject.toml      # Python 项目配置
├── PKGBUILD            # Arch 打包脚本
├── src/
│   └── annotatia.py    # 主脚本
└── .opencode/plans/
    └── ANNOTATE_PLAN.md # 设计文档
```
