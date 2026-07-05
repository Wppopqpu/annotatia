#!/usr/bin/env python3
import argparse
import re
import sys

import pykakasi


def contains_kanji(text):
    for c in text:
        if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf':
            return True
    return False


def _process_line(line, kks):
    segments = kks.convert(line)
    parts = []
    for seg in segments:
        orig = seg['orig']
        hira = seg['hira']
        if orig == hira or not contains_kanji(orig):
            parts.append(orig)
        else:
            parts.append(r'\ruby{%s}{%s}' % (orig, hira))
    return ''.join(parts)


PARA = '\n\n'


def convert_to_ruby(text):
    kks = pykakasi.kakasi()
    lines = text.split('\n')
    processed = [_process_line(l, kks) for l in lines]
    return PARA.join(processed)


LRC_TIMESTAMP_RE = re.compile(r'\[\d{2}:\d{2}\.\d{2,3}\]')


def parse_lrc(text):
    lines = text.split('\n')
    result = []
    for line in lines:
        cleaned = LRC_TIMESTAMP_RE.sub('', line).strip()
        result.append(cleaned)
    return '\n'.join(result)


def add_hr_separator(text):
    lines = text.split(PARA)
    non_empty = [i for i, l in enumerate(lines) if l.strip()]
    result = []
    for i, line in enumerate(lines):
        if line.strip():
            if result and result[-1].strip():
                result.append(r'\vspace{0.3ex}\rule{0.6\linewidth}{0.4pt}\vspace{0.3ex}')
            result.append(line)
        else:
            result.append('')
    return PARA.join(result)


RUBY_MACRO = (
    r'\newcommand{\ruby}[2]{'
    r'\leavevmode\vtop{'
    r'\ialign{\hfil##\hfil\cr'
    r'\scriptsize #2\cr'
    r'\noalign{\kern-0.5ex}'
    r'#1\cr}}}'
)


def generate_template(content, engine, center=False, linespread=None, twocolumn=False):
    nl = '\n'
    if engine == 'xelatex':
        preamble = (
            r'\documentclass{article}' + nl
            + r'\usepackage{fontspec}' + nl
            + r'\usepackage{xeCJK}' + nl
            + r'\setCJKmainfont{Noto Sans CJK JP}' + nl
            + RUBY_MACRO + nl
        )
        if linespread is not None:
            preamble += r'\linespread{%s}' % linespread + nl + r'\selectfont' + nl
        if twocolumn:
            preamble += r'\usepackage{multicol}' + nl
        preamble += r'\begin{document}' + nl
        if twocolumn:
            preamble += r'\begin{multicols}{2}' + nl
        postamble = nl
        if twocolumn:
            postamble += r'\end{multicols}' + nl
        postamble += r'\end{document}' + nl
    elif engine == 'lualatex':
        preamble = (
            r'\documentclass{article}' + nl
            + r'\usepackage{luatexja}' + nl
            + r'\usepackage{luatexja-ruby}' + nl
        )
        if linespread is not None:
            preamble += r'\linespread{%s}' % linespread + nl + r'\selectfont' + nl
        if twocolumn:
            preamble += r'\usepackage{multicol}' + nl
        preamble += r'\begin{document}' + nl
        if twocolumn:
            preamble += r'\begin{multicols}{2}' + nl
        postamble = nl
        if twocolumn:
            postamble += r'\end{multicols}' + nl
        postamble += r'\end{document}' + nl
    else:
        preamble = (
            r'\documentclass{article}' + nl
            + r'\usepackage{CJK}' + nl
            + r'\usepackage{ruby}' + nl
            + r'\begin{CJK}{UTF8}{min}' + nl
        )
        if linespread is not None:
            preamble += r'\linespread{%s}' % linespread + nl + r'\selectfont' + nl
        if twocolumn:
            preamble += r'\usepackage{multicol}' + nl
        preamble += r'\begin{document}' + nl
        if twocolumn:
            preamble += r'\begin{multicols}{2}' + nl
        postamble = nl
        if twocolumn:
            postamble += r'\end{multicols}' + nl
        postamble += r'\end{document}' + nl + r'\end{CJK}' + nl

    if center:
        content = r'\begin{center}' + nl + content + nl + r'\end{center}'

    return preamble + content + postamble


def main():
    parser = argparse.ArgumentParser(
        description='Convert Japanese text to LaTeX with furigana (\\ruby) annotation.'
    )
    parser.add_argument('input', nargs='?', help='Input file (stdin if not specified)')
    parser.add_argument('-o', '--output', help='Output .tex file (stdout if not specified)')
    parser.add_argument('--engine', choices=['xelatex', 'pdflatex', 'lualatex'],
                        default='xelatex',
                        help='Target LaTeX engine (default: xelatex)')
    parser.add_argument('--template', action='store_true',
                        help='Output complete LaTeX document with preamble')
    parser.add_argument('--center',
                        action=argparse.BooleanOptionalAction,
                        help='Center-align text in the document (use --no-center to disable)')
    parser.add_argument('--linespread', type=float,
                        help='Line spacing multiplier (e.g. 1.5 for one-and-a-half spacing)')
    parser.add_argument('--hr',
                        action=argparse.BooleanOptionalAction,
                        help='Insert horizontal rules between text lines (use --no-hr to disable)')
    parser.add_argument('--twocolumn',
                        action=argparse.BooleanOptionalAction,
                        help='Two-column layout (use --no-twocolumn to disable)')
    parser.add_argument('--lrc', action='store_true',
                        help='LRC lyrics mode (auto-sets --center --linespread 1.5 --hr, '
                             'strips timestamps; use --no-center/--no-hr to override)')

    args = parser.parse_args()

    if args.input:
        with open(args.input, encoding='utf-8') as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    is_lrc = args.lrc or (args.input and args.input.endswith('.lrc'))
    if is_lrc:
        text = parse_lrc(text)

    converted = convert_to_ruby(text)

    hr = args.hr if args.hr is not None else is_lrc

    if hr:
        converted = add_hr_separator(converted)

    if args.template:
        center = args.center if args.center is not None else is_lrc
        linespread = args.linespread if args.linespread is not None else (
            1.5 if is_lrc else None
        )
        output = generate_template(converted, args.engine,
                                   center=center,
                                   linespread=linespread,
                                   twocolumn=args.twocolumn)
    else:
        output = converted

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        sys.stdout.write(output)


if __name__ == '__main__':
    main()
