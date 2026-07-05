#!/usr/bin/env python3
import argparse
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


def convert_to_ruby(text):
    kks = pykakasi.kakasi()
    lines = text.split('\n')
    processed = [_process_line(l, kks) for l in lines]
    return '\n'.join(processed)


RUBY_MACRO = (
    r'\newcommand{\ruby}[2]{'
    r'\leavevmode\vtop{'
    r'\ialign{\hfil##\hfil\cr'
    r'\scriptsize #2\cr'
    r'\noalign{\kern-0.5ex}'
    r'#1\cr}}}'
)


def generate_template(content, engine, center=False, linespread=None):
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
        preamble += r'\begin{document}' + nl
        postamble = nl + r'\end{document}' + nl
    elif engine == 'lualatex':
        preamble = (
            r'\documentclass{article}' + nl
            + r'\usepackage{luatexja}' + nl
            + r'\usepackage{luatexja-ruby}' + nl
        )
        if linespread is not None:
            preamble += r'\linespread{%s}' % linespread + nl + r'\selectfont' + nl
        preamble += r'\begin{document}' + nl
        postamble = nl + r'\end{document}' + nl
    else:
        preamble = (
            r'\documentclass{article}' + nl
            + r'\usepackage{CJK}' + nl
            + r'\usepackage{ruby}' + nl
            + r'\begin{CJK}{UTF8}{min}' + nl
        )
        if linespread is not None:
            preamble += r'\linespread{%s}' % linespread + nl + r'\selectfont' + nl
        preamble += r'\begin{document}' + nl
        postamble = (
            nl + r'\end{document}' + nl
            + r'\end{CJK}' + nl
        )

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
    parser.add_argument('--center', action='store_true',
                        help='Center-align text in the document')
    parser.add_argument('--linespread', type=float,
                        help='Line spacing multiplier (e.g. 1.5 for one-and-a-half spacing)')

    args = parser.parse_args()

    if args.input:
        with open(args.input, encoding='utf-8') as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    converted = convert_to_ruby(text)

    if args.template:
        output = generate_template(converted, args.engine,
                                   center=args.center,
                                   linespread=args.linespread)
    else:
        output = converted

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        sys.stdout.write(output)


if __name__ == '__main__':
    main()
