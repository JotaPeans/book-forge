#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de build do book-forge: transforma content/*.md + book.py em um PDF único, com o design
do livro "Rust do Zero ao Avançado" (faixa de destaque, caixas coloridas, capas de capítulo,
gabaritos no fim, referências).

    pip install reportlab
    python build.py              # dist/<OUT_NAME> (somente aulas que já existem)

O conteúdo fica em content/*.md; o plano (capítulos/aulas) e as opções ficam em book.py
(LANG, THEME, HEADER, CODE_LANG... veja o book.py do scaffold). Formato dos .md: README.md.
"""
import argparse
import re
import shlex
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, Image, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle,
                                XPreformatted)

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import book as B  # noqa: E402

LANG = getattr(B, "LANG", "pt-BR")
CONTENT_DIR = getattr(B, "CONTENT_DIR", "content")
OUT_NAME = getattr(B, "OUT_NAME", "livro.pdf")
CODE_LANG = getattr(B, "CODE_LANG", "rust")       # linguagem padrão dos blocos de código

# ----------------------------------------------------------------------------
# Textos da interface (pt-BR e en). Sobrescreva qualquer chave com STRINGS em book.py.
# ----------------------------------------------------------------------------
_STR = {
    "pt-BR": dict(
        box_objetivos="Objetivos da aula", box_conceito="Conceito", box_pausa="Pause e pense",
        box_erro_comum="Erro comum", box_pratica="Na prática", box_dica="Dica",
        box_resumo="Resumo da aula", box_checkpoint="Checkpoint",
        box_exercicios="Exercícios · mão na massa",
        cover_kicker="CURSO COMPLETO · DO BÁSICO AO AVANÇADO", n_lessons="%s + projeto",
        w_lesson=("aula", "aulas"), w_project=("projeto", "projetos"), w_week=("semana", "semanas"),
        edition="Edição de estudo", chapter_cover="Capa de capítulo", in_chapter="NESTE CAPÍTULO",
        chapter_project="PROJETO DO CAPÍTULO", journey="SUA JORNADA",
        next_stop="Próxima parada: Aula %s · %s", cut_line="- - -   CORTE   - - -",
        spoilers="ATENÇÃO · SPOILERS À FRENTE", answers_word="Gabaritos",
        cut_text="As respostas de todos os exercícios estão nas próximas páginas. "
                 "Antes de virar a página, confirme:",
        cut_checklist=["Tentei resolver sozinho, sem olhar a resposta.",
                       "Rodei o código e li a mensagem de erro, se houve.",
                       "Comparei meu resultado com o que a aula pedia."],
        answers_footer="Gabaritos · %d aula(s) com respostas", plan_kicker="PLANO DO CURSO",
        plan_title="O caminho completo",
        plan_sub="%s e %s. Estimativa de %d h, ou ≈ %s a %d h por semana.",
        legend_ready="aula pronta", legend_pending="pendente",
        legend_note="Leitura = tempo de ler e digitar. Com exercícios, conte ≈ 3x.",
        project="Projeto", project_up="PROJETO", lesson="Aula", lesson_up="AULA",
        m_duration="Duração", m_prereq="Pré-requisito", m_difficulty="Dificuldade",
        m_deliverable="Entrega", ans_kicker="GABARITOS", ans_title="Respostas dos exercícios",
        ans_sub="Confira só depois de tentar. Compare com o seu código e peça uma revisão.",
        ans_bookmark="Gabarito · Aula %s", answers_run="Respostas",
        refs_kicker="REFERÊNCIAS", refs_title="Para ir além",
        refs_sub="Leituras e ferramentas que acompanham o curso. Confira sempre a versão da "
                 "documentação.", refs_word="Referências", guide="Guia do livro",
        plan_word="Plano do curso", appendix="Apêndice", figure="Figura", listing="Listagem",
        error_title="Mensagem de erro", output_name="saída do programa", text_name="texto",
        terminal_name="terminal", missing_image="imagem não encontrada"),
    "en": dict(
        box_objetivos="Lesson objectives", box_conceito="Concept", box_pausa="Pause and think",
        box_erro_comum="Common mistake", box_pratica="In practice", box_dica="Tip",
        box_resumo="Lesson summary", box_checkpoint="Checkpoint",
        box_exercicios="Exercises · hands-on",
        cover_kicker="COMPLETE COURSE · FROM BASICS TO ADVANCED", n_lessons="%s + project",
        w_lesson=("lesson", "lessons"), w_project=("project", "projects"), w_week=("week", "weeks"),
        edition="Study edition", chapter_cover="Chapter cover", in_chapter="IN THIS CHAPTER",
        chapter_project="CHAPTER PROJECT", journey="YOUR JOURNEY",
        next_stop="Next stop: Lesson %s · %s", cut_line="- - -   CUT HERE   - - -",
        spoilers="WARNING · SPOILERS AHEAD", answers_word="Answer key",
        cut_text="The answers to every exercise are on the next pages. "
                 "Before you turn the page, make sure:",
        cut_checklist=["I tried to solve it on my own, without peeking.",
                       "I ran the code and read the error message, if any.",
                       "I compared my result with what the lesson asked for."],
        answers_footer="Answer key · %d lesson(s) with answers", plan_kicker="COURSE PLAN",
        plan_title="The full path",
        plan_sub="%s and %s. Estimated %d h, or about %s at %d h per week.",
        legend_ready="lesson ready", legend_pending="pending",
        legend_note="Reading = time to read and type along. With exercises, count on about 3x.",
        project="Project", project_up="PROJECT", lesson="Lesson", lesson_up="LESSON",
        m_duration="Duration", m_prereq="Prerequisite", m_difficulty="Difficulty",
        m_deliverable="Deliverable", ans_kicker="ANSWER KEY", ans_title="Exercise answers",
        ans_sub="Check only after you tried. Compare with your own code and ask for a review.",
        ans_bookmark="Answers · Lesson %s", answers_run="Answers",
        refs_kicker="REFERENCES", refs_title="Going further",
        refs_sub="Readings and tools that go with the course. Always check the documentation "
                 "version.", refs_word="References", guide="Book guide",
        plan_word="Course plan", appendix="Appendix", figure="Figure", listing="Listing",
        error_title="Error output", output_name="program output", text_name="text",
        terminal_name="terminal", missing_image="image not found"),
}
if LANG not in _STR:
    raise SystemExit("LANG '%s' sem tradução. Use: %s ou adicione em STRINGS." % (LANG, ", ".join(_STR)))
ST = dict(_STR[LANG]); ST.update(getattr(B, "STRINGS", {}))


def pl(n, words):
    """'1 aula', '3 aulas' (words = (singular, plural))."""
    return "%d %s" % (n, words[0] if n == 1 else words[1])

# Nomes de caixas e de blocos: o dialeto aceita português e inglês.
ALIAS = {"objectives": "objetivos", "concept": "conceito", "pause": "pausa",
         "common-mistake": "erro-comum", "practice": "pratica", "tip": "dica",
         "summary": "resumo", "exercises": "exercicios", "answers": "gabarito",
         "answer": "gabarito"}
LANG_ALIAS = {"error": "erro", "output": "saida", "image": "imagem", "figure": "imagem"}

# ----------------------------------------------------------------------------
# Fontes (embutidas na pasta fonts/ para funcionar em qualquer sistema)
# ----------------------------------------------------------------------------
FD = ROOT / "fonts"
for name, fn in [("Sans", "LiberationSans-Regular.ttf"), ("Sans-B", "LiberationSans-Bold.ttf"),
                 ("Sans-I", "LiberationSans-Italic.ttf"), ("Sans-BI", "LiberationSans-BoldItalic.ttf"),
                 ("Mono", "DejaVuSansMono.ttf"), ("Mono-B", "DejaVuSansMono-Bold.ttf"),
                 ("Mono-I", "DejaVuSansMono-Oblique.ttf"), ("Mono-BI", "DejaVuSansMono-BoldOblique.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FD / fn)))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-BI")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-B", italic="Mono-I", boldItalic="Mono-BI")

# ----------------------------------------------------------------------------
# Paleta (v3 aprovada). O tema padrão é o laranja do livro original; só a cor de destaque
# muda entre temas, o resto (cinzas, âmbar, vermelho, verde) é fixo.
# ----------------------------------------------------------------------------
HEX = colors.HexColor
THEMES = {  # (destaque, destaque escuro, fundo claro, palavra-chave no código)
    "orange": ("#EF8939", "#D56F24", "#FFFBF7", "#E37A2E"),
    "blue": ("#3B82C4", "#2C6AA6", "#F6FAFE", "#2F76B8"),
    "green": ("#3E9B6B", "#2D7D54", "#F6FBF8", "#348A5C"),
    "purple": ("#8B6BC9", "#7050B0", "#FAF8FE", "#7C5BBE"),
    "teal": ("#2E9AA0", "#217C82", "#F5FBFB", "#278A90"),
    "red": ("#D8605B", "#B84843", "#FFF8F8", "#C9504B"),
}
THEME = getattr(B, "THEME", "orange")
if THEME not in THEMES:
    raise SystemExit("THEME '%s' desconhecido. Use: %s" % (THEME, ", ".join(THEMES)))
ACC, ACC_DK, ACC_BG_HEX, ACC_KW = THEMES[THEME]
ORANGE, ORANGE_DK, ORANGE_BG = HEX(ACC), HEX(ACC_DK), HEX(ACC_BG_HEX)
GRAY_BORDER, GRAY_LINE, GRAY_BG = HEX("#DEDEE2"), HEX("#ECECEF"), HEX("#FBFBFB")
TEXT, MUTED = HEX("#27272A"), HEX("#7C7C86")
AMBER, AMBER_BG = HEX("#E3B552"), HEX("#FFFDF6")
RED, RED_BG = HEX("#E88A85"), HEX("#FFFBFB")
GREEN, GREEN_BG = HEX("#6DB38A"), HEX("#FAFDFB")
SLATE, SLATE_TAG = HEX("#A1A1AA"), HEX("#6B6B75")
SLATE_HEX = "#A1A1AA"
WHITE = colors.white

W, H = A4
MARGIN = 20 * mm
BOTTOM = 21 * mm
CONTENT_W = W - 2 * MARGIN
STRIPE = 1.6 * mm
PAD = 11

# ----------------------------------------------------------------------------
# Estilos
# ----------------------------------------------------------------------------
def PS(name, **kw):
    return ParagraphStyle(name, **kw)

body = PS("body", fontName="Sans", fontSize=10.2, leading=15.2, textColor=TEXT, spaceAfter=7)
box_body = PS("box_body", parent=body, fontSize=9.6, leading=14, spaceAfter=3)
bullet = PS("bullet", parent=body, leftIndent=14, bulletIndent=2, bulletFontName="Sans-B", spaceAfter=2.5)
box_bullet = PS("box_bullet", parent=box_body, leftIndent=14, bulletIndent=2, bulletFontName="Sans-B", spaceAfter=2)
h_kicker = PS("kicker", fontName="Sans-B", fontSize=8.5, leading=11, textColor=ORANGE, spaceAfter=4)
h_title = PS("title", fontName="Sans-B", fontSize=25, leading=29, textColor=TEXT, spaceAfter=6)
h_sub = PS("sub", fontName="Sans", fontSize=11.5, leading=16, textColor=MUTED, spaceAfter=12)
h2 = PS("h2", fontName="Sans-B", fontSize=14, leading=18, textColor=TEXT)
h2_num = PS("h2n", parent=h2, textColor=ORANGE)
h3 = PS("h3", fontName="Sans-B", fontSize=11.5, leading=15, textColor=TEXT, spaceBefore=6, spaceAfter=4)
meta_label = PS("ml", fontName="Sans-B", fontSize=7.5, leading=10, textColor=MUTED)
meta_val = PS("mv", fontName="Sans", fontSize=9.5, leading=12.5, textColor=TEXT)
cap = PS("cap", fontName="Sans-I", fontSize=8.5, leading=11, textColor=MUTED, spaceBefore=2, spaceAfter=9)
small = PS("small", fontName="Sans", fontSize=8.6, leading=11.5, textColor=MUTED)
cell = PS("cell", fontName="Sans", fontSize=9.6, leading=12.5, textColor=TEXT)
cell_muted = PS("cell_muted", parent=cell, textColor=MUTED, fontSize=9)


def tag_style(c):
    return PS("tag", fontName="Sans-B", fontSize=7.8, leading=10, textColor=c, spaceAfter=3)


# ----------------------------------------------------------------------------
# Texto inline: `codigo`, **negrito**, *itálico*
# ----------------------------------------------------------------------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text):
    """`código`, **negrito** e *itálico*. O negrito pode atravessar trechos de código."""
    codes = []

    def stash(m):
        codes.append("<font name='Mono' size='8.6' color='#52525B'>%s</font>" % esc(m.group(1)))
        return "\x00%d\x00" % (len(codes) - 1)

    t = re.sub(r"`([^`]+)`", stash, text)
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])", r"<i>\1</i>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], t)


# ----------------------------------------------------------------------------
# Destaque de sintaxe (Rust completo; demais linguagens por tabela de palavras-chave)
# ----------------------------------------------------------------------------
_SLASH, _HASH = r"//[^\n]*", r"#[^\n]*"
_LANGS = {   # nome -> (comentário, palavras-chave, tipos/constantes, aspas simples são string?)
    "rust": (_SLASH, r"fn|let|mut|use|struct|enum|impl|pub|match|if|else|for|while|loop|return|"
             r"self|Self|in|as|mod|trait|move|const|static|where|dyn|type|unsafe|async|await|ref|"
             r"crate|super|break|continue|true|false",
             r"String|Vec|Option|Result|Box|Rc|Arc|RefCell|Mutex|HashMap|i8|i16|i32|i64|u8|u16|"
             r"u32|u64|f32|f64|usize|isize|bool|char|str|Some|None|Ok|Err", False),
    "python": (_HASH, r"def|class|import|from|as|if|elif|else|for|while|return|in|not|and|or|is|"
               r"with|try|except|finally|raise|lambda|yield|pass|break|continue|global|nonlocal|"
               r"async|await|assert|del", r"True|False|None|self|int|str|float|bool|list|dict|"
               r"set|tuple|bytes", True),
    "js": (_SLASH, r"function|const|let|var|if|else|for|while|do|return|class|extends|new|this|"
           r"import|export|from|default|async|await|try|catch|finally|throw|switch|case|break|"
           r"continue|typeof|instanceof|of|in|interface|type|enum|implements|public|private|"
           r"readonly|as", r"true|false|null|undefined|string|number|boolean|void|any|never|"
           r"unknown|Promise|Array|Map|Set", True),
    "c": (_SLASH, r"if|else|for|while|do|return|struct|enum|union|typedef|static|const|extern|"
          r"sizeof|switch|case|break|continue|goto|class|public|private|protected|namespace|"
          r"using|template|new|delete|virtual|override", r"int|char|float|double|void|long|"
          r"short|unsigned|signed|size_t|bool|NULL|true|false|uint8_t|uint16_t|uint32_t|"
          r"uint64_t|int8_t|int16_t|int32_t|int64_t|auto", False),
    "go": (_SLASH, r"func|var|const|type|struct|interface|map|chan|go|defer|if|else|for|range|"
           r"return|switch|case|break|continue|package|import|select|fallthrough",
           r"int|int8|int16|int32|int64|uint|uint8|uint16|uint32|uint64|float32|float64|string|"
           r"bool|byte|rune|error|nil|true|false", False),
    "java": (_SLASH, r"class|interface|extends|implements|public|private|protected|static|final|"
             r"abstract|void|if|else|for|while|do|return|new|this|super|import|package|try|catch|"
             r"finally|throw|throws|switch|case|break|continue|enum|var|record",
             r"int|long|double|float|boolean|char|byte|short|String|List|Map|Set|null|true|false",
             False),
    "sh": (_HASH, r"if|then|else|elif|fi|for|while|do|done|case|esac|function|in|export|local|"
           r"return|echo|cd|exit", r"true|false", True),
}
_ALIASES = {"rs": "rust", "py": "python", "python3": "python", "javascript": "js", "ts": "js",
            "typescript": "js", "tsx": "js", "jsx": "js", "cpp": "c", "c++": "c", "h": "c",
            "bash": "sh", "zsh": "sh", "shell": "sh", "kotlin": "java", "cs": "java",
            "csharp": "java"}
_TOKENS = {}


def _tokens(lang):
    """Regex de tokens da linguagem (compilado uma vez)."""
    lang = _ALIASES.get(lang, lang)
    if lang not in _LANGS:
        return None
    if lang not in _TOKENS:
        com, kw, ty, sq = _LANGS[lang]
        strs = r"\"(?:[^\"\\]|\\.)*\"" + (r"|'(?:[^'\\\n]|\\.)*'" if sq else "")
        life = r"|(?P<life>'[a-z_]+\b(?!'))" if lang == "rust" else ""
        macro = r"|(?P<macro>\b\w+!)" if lang == "rust" else ""
        _TOKENS[lang] = re.compile(
            r"(?P<comment>%s)|(?P<string>%s)%s%s|(?P<kw>\b(?:%s)\b)|(?P<type>\b(?:%s)\b)|"
            r"(?P<num>\b\d[\d_]*(?:\.\d+)?\b)" % (com, strs, life, macro, kw, ty))
    return _TOKENS[lang]


SYN = {"comment": ("#71717A", "i"), "string": ("#5E9C77", ""), "life": ("#4F9A94", ""),
       "macro": ("#6B6B75", "b"), "kw": (ACC_KW, "b"), "type": ("#4F9A94", ""),
       "num": ("#D49246", "")}


def highlight(src, lang="rust"):
    rx = _tokens(lang)
    if rx is None:
        return esc(src)
    out, pos = [], 0
    for m in rx.finditer(src):
        out.append(esc(src[pos:m.start()]))
        color, style = SYN[m.lastgroup]
        t = esc(m.group())
        if style:
            t = "<%s>%s</%s>" % (style, t, style)
        out.append('<font color="%s">%s</font>' % (color, t))
        pos = m.end()
    out.append(esc(src[pos:]))
    return "".join(out)


# ----------------------------------------------------------------------------
# Blocos visuais
# ----------------------------------------------------------------------------
def h2_block(num, text):
    t = Table([[Paragraph("%02d" % num, h2_num), Paragraph(text, h2)]],
              colWidths=[11 * mm, CONTENT_W - 11 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("LINEBELOW", (0, 0), (-1, 0), 0.8, GRAY_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    return [Spacer(1, 8), t, Spacer(1, 9)]


def striped_box(inner, color, bg, dashed=False, width=CONTENT_W, rpad=PAD):
    t = Table([["", inner]], colWidths=[STRIPE, width - STRIPE])
    style = [
        ("BACKGROUND", (0, 0), (0, 0), color), ("BACKGROUND", (1, 0), (1, 0), bg),
        ("BOX", (0, 0), (-1, -1), 0.7, GRAY_BORDER),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), PAD), ("RIGHTPADDING", (1, 0), (1, 0), rpad),
        ("TOPPADDING", (1, 0), (1, 0), 8), ("BOTTOMPADDING", (1, 0), (1, 0), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP")]
    if dashed:
        style[2] = ("BOX", (0, 0), (-1, -1), 0.9, color, None, (3, 2))
    t.setStyle(TableStyle(style))
    return t


def meta_row(items):
    cells = [[Paragraph(l.upper(), meta_label), Spacer(1, 2), Paragraph(v, meta_val)] for l, v in items]
    n = len(items)
    t = Table([cells], colWidths=[CONTENT_W / n] * n)
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.7, GRAY_BORDER), ("LINEBEFORE", (1, 0), (-1, 0), 0.7, GRAY_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def title_block(kicker, title, subtitle="", meta=None):
    out = [Spacer(1, 4)]
    if kicker:
        out.append(Paragraph(esc(kicker.upper()), h_kicker))
    out.append(Paragraph(inline(title), h_title))
    if subtitle:
        out.append(Paragraph(inline(subtitle), h_sub))
    if meta:
        out += [meta_row(meta), Spacer(1, 12)]
    return out


def line_budget(width, font_size, pad=20):
    return int((width - pad) / (0.602 * font_size))


def _figura(opts, width, ctx):
    """Uma imagem (captura de tela, por exemplo) com legenda numerada.

    ```imagem file=content/extra/img/arena.png caption="..." largura=0.6
    `largura` é a fração da largura da página (padrão 0.62); o caminho é relativo à raiz."""
    caminho = ROOT / opts["file"]
    if not caminho.exists():
        print("  aviso: %s: %s" % (ST["missing_image"], caminho))
        return [Spacer(1, 4)]
    img = Image(str(caminho))
    alvo = width * float(opts.get("largura", 0.62))
    img.drawHeight = img.drawHeight * alvo / img.drawWidth
    img.drawWidth = alvo
    img.hAlign = "CENTER"
    moldura = Table([[img]], colWidths=[alvo + 8])
    moldura.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.7, GRAY_BORDER),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                                 ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    moldura.hAlign = "CENTER"
    itens = [moldura]
    if opts.get("caption"):
        ctx["figura"] = ctx.get("figura", 0) + 1
        num = ("%s %s.%d · " % (ST["figure"], ctx["label"], ctx["figura"])) if ctx.get("label") else ""
        itens.append(Paragraph(num + inline(opts["caption"]), cap))
    return [KeepTogether(itens), Spacer(1, 10)]


def code_block(src, info, width, ctx):
    """Bloco de código com cabeçalho do arquivo; divide entre páginas se for longo."""
    try:
        parts = shlex.split(info) if info else []
    except ValueError:
        parts = info.split()
    lang = parts[0] if parts else "text"
    lang = LANG_ALIAS.get(lang, lang)
    opts = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
    if lang == "imagem":
        return _figura(opts, width, ctx)
    src = src.strip("\n")
    lines = src.split("\n")
    size = 8.3 if lang != "erro" else 7.6
    pad = 30 if lang == "erro" else 20
    limit = line_budget(width, size, pad=pad)
    # linha larga demais (saída real de uma ferramenta, por exemplo): encolhe a fonte, até um piso
    mais_larga = max(len(ln) for ln in lines)
    if mais_larga > limit:
        size = max(6.6, size * limit / mais_larga - 0.05)
        limit = line_budget(width, size, pad=pad)
    for ln in lines:
        if len(ln) > limit:
            print("  aviso: linha longa (%d > %d) em bloco '%s': %s…" % (len(ln), limit, lang, ln[:50]))

    if lang == "erro":
        return [_error_block(lines, width, opts.get("titulo", ST["error_title"]), size),
                Spacer(1, 10)]

    default_file = {"sh": ST["terminal_name"], "text": ST["text_name"], "saida": ST["output_name"]}
    default_file.update(getattr(B, "FILE_NAMES", {}))  # ex.: {"rust": "src/main.rs"}
    fname = opts.get("file", default_file.get(lang, lang))
    st = PS("code", fontName="Mono", fontSize=size, leading=min(12.2, size * 1.47),
            textColor=TEXT)
    head = Paragraph('<font color="#71717A">%s</font>' % esc(fname),
                     PS("fn", fontName="Mono", fontSize=7.4, leading=10, textColor=MUTED))
    chunks = [lines[i:i + 14] for i in range(0, len(lines), 14)] or [[""]]
    rows = [[head]]
    for ch in chunks:
        body_txt = "\n".join(ch)
        rows.append([XPreformatted(highlight(body_txt, lang), st)])
    t = Table(rows, colWidths=[width])
    last = len(rows) - 1
    cmds = [("BACKGROUND", (0, 0), (0, 0), HEX("#F5F5F6")), ("BACKGROUND", (0, 1), (0, -1), GRAY_BG),
            ("BOX", (0, 0), (-1, -1), 0.7, GRAY_BORDER), ("LINEBELOW", (0, 0), (0, 0), 0.5, GRAY_BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), PAD), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (0, 0), 4), ("BOTTOMPADDING", (0, 0), (0, 0), 4),
            ("TOPPADDING", (0, 1), (-1, -1), 0), ("BOTTOMPADDING", (0, 1), (-1, -1), 0),
            ("TOPPADDING", (0, 1), (0, 1), 8), ("BOTTOMPADDING", (0, last), (0, last), 8),
            ("NOSPLIT", (0, 0), (0, 1))]
    t.setStyle(TableStyle(cmds))
    out = [t]
    if opts.get("caption"):
        ctx["listing"] += 1
        num = ("%s %s.%d · " % (ST["listing"], ctx["label"], ctx["listing"])) if ctx["label"] else ""
        out.append(Paragraph(num + inline(opts["caption"]), cap))
    else:
        out.append(Spacer(1, 8))
    return out


def _error_block(lines, width, title="Error output", size=7.6):
    txt = esc("\n".join(lines))
    txt = re.sub(r"^(thread '[^']*' panicked at)", r'<font color="#DE7670"><b>\1</b></font>', txt, flags=re.M)
    txt = re.sub(r"^((?:error|erro|Error|Traceback|\w+Error|FAIL)(?:\[E\d+\])?)",
                 r'<font color="#DE7670"><b>\1</b></font>', txt, flags=re.M)
    txt = re.sub(r"^(warning)", r'<font color="#D9A441"><b>\1</b></font>', txt, flags=re.M)
    txt = re.sub(r"(\^+)", r'<font color="#DE7670"><b>\1</b></font>', txt)
    head = Paragraph('<font color="#DE7670"><b>%s</b></font>' % esc(title.upper()),
                     PS("eh", fontName="Sans-B", fontSize=7.4, leading=10))
    st = PS("codeerr", fontName="Mono", fontSize=size, leading=min(11, size * 1.45),
            textColor=TEXT)
    return striped_box([head, Spacer(1, 3), XPreformatted(txt, st)], RED, RED_BG, width=width, rpad=6)


BOXES = {   # nome canônico -> (rótulo, cor, fundo, tracejada)
    "objetivos": (ST["box_objetivos"], ORANGE, ORANGE_BG, False),
    "conceito": (ST["box_conceito"], ORANGE, ORANGE_BG, False),
    "pausa": (ST["box_pausa"], ORANGE, WHITE, True),
    "erro-comum": (ST["box_erro_comum"], AMBER, AMBER_BG, False),
    "pratica": (ST["box_pratica"], SLATE, GRAY_BG, False),
    "dica": (ST["box_dica"], GREEN, GREEN_BG, False),
    "resumo": (ST["box_resumo"], ORANGE, ORANGE_BG, False),
    "checkpoint": (ST["box_checkpoint"], ORANGE, ORANGE_BG, False),
    "exercicios": (ST["box_exercicios"], ORANGE, WHITE, False),
}


def exercise_table(items, width):
    rows = [[Paragraph('<font color="%s"><b>%d</b></font>' % (ACC, i), PS("n", fontName="Sans-B", fontSize=11, leading=14)),
             Paragraph(inline(t), box_body)] for i, t in enumerate(items, 1)]
    t = Table(rows, colWidths=[9 * mm, width - 9 * mm])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -2), 0.5, GRAY_LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def render_box(name, title, blocks, ctx):
    name = ALIAS.get(name, name)
    if name not in BOXES:
        raise SystemExit("Caixa desconhecida: '%s'. Válidas: %s"
                         % (name, ", ".join(list(BOXES) + list(ALIAS) + ["gabarito"])))
    default, color, bg, dashed = BOXES[name]
    tag = default + (" · " + title if title else "")
    inner_w = CONTENT_W - STRIPE - PAD - PAD
    inner = [Paragraph(esc(tag.upper()), tag_style(SLATE_TAG if color == SLATE else color))]
    for b in blocks:
        if b[0] == "ol" and name == "exercicios":
            inner.append(exercise_table(b[1], inner_w))
        elif b[0] == "ul" and name == "checkpoint":
            inner += [Paragraph(inline(t), box_bullet, bulletText="○") for t in b[1]]
        else:
            inner += render_blocks([b], ctx, inner_w, in_box=True)
    return [KeepTogether([striped_box(inner, color, bg, dashed), Spacer(1, 10)])]


def render_blocks(blocks, ctx, width=CONTENT_W, in_box=False):
    out = []
    pending = None          # título de seção aguardando o primeiro bloco seguinte
    pstyle, bstyle = (box_body, box_bullet) if in_box else (body, bullet)
    gap = 0 if in_box else 3
    for b in blocks:
        k = b[0]
        chunk = []
        if k == "h2":
            ctx["h2"] += 1
            if pending:
                out += pending
            pending = h2_block(ctx["h2"], inline(b[1]))
            continue
        elif k == "h3":
            chunk = [Paragraph(inline(b[1]), h3)]
        elif k == "p":
            chunk = [Paragraph(inline(b[1]), pstyle)]
        elif k == "ul":
            chunk = [Paragraph(inline(t), bstyle, bulletText="•") for t in b[1]] + [Spacer(1, gap)]
        elif k == "ol":
            chunk = [Paragraph(inline(t), bstyle, bulletText="%d." % i) for i, t in enumerate(b[1], b[2])] + [Spacer(1, gap)]
        elif k == "code":
            chunk = code_block(b[2], b[1], width, ctx)
        elif k == "box":
            if ALIAS.get(b[1], b[1]) == "gabarito":
                ctx["answers"].append(b[3])
            else:
                chunk = render_box(b[1], b[2], b[3], ctx)
        if chunk and pending:
            first = chunk[0]
            inner = list(first._content) if isinstance(first, KeepTogether) else [first]
            chunk[0] = KeepTogether(pending + inner)
            pending = None
        out += chunk
    if pending:
        out += pending
    return out


# ----------------------------------------------------------------------------
# Parser do Markdown simplificado
# ----------------------------------------------------------------------------
def _fence_open(s):
    m = re.match(r"^(`{3,})", s)
    return len(m.group(1)) if m else 0


def parse_blocks(text):
    lines = text.split("\n")
    i, blocks, para = 0, [], []

    def flush():
        nonlocal para
        if para:
            blocks.append(("p", " ".join(s.strip() for s in para)))
            para = []

    while i < len(lines):
        s = lines[i].strip()
        n = _fence_open(s)
        if n:
            flush()
            info, buf = s[n:].strip(), []
            i += 1
            while i < len(lines) and not re.fullmatch(r"`{%d,}" % n, lines[i].strip()):
                buf.append(lines[i])
                i += 1
            blocks.append(("code", info, "\n".join(buf)))
            i += 1
            continue
        if s.startswith(":::") and len(s) > 3:
            flush()
            name, _, title = s[3:].strip().partition(" ")
            i += 1
            buf, fence = [], 0
            while i < len(lines):
                t = lines[i].strip()
                fn = _fence_open(t)
                if fence == 0 and fn:
                    fence = fn
                elif fence and re.fullmatch(r"`{%d,}" % fence, t):
                    fence = 0
                if t == ":::" and fence == 0:
                    break
                buf.append(lines[i])
                i += 1
            blocks.append(("box", name, title.strip(), parse_blocks("\n".join(buf))))
            i += 1
            continue
        if s.startswith("### "):
            flush(); blocks.append(("h3", s[4:])); i += 1; continue
        if s.startswith("## "):
            flush(); blocks.append(("h2", s[3:])); i += 1; continue
        for kind, rx in (("ul", r"^[-*] (.*)"), ("ol", r"^(\d+)\.\s+(.*)")):
            m = re.match(rx, s)
            if m:
                flush()
                start = int(m.group(1)) if kind == "ol" else 1
                items = [m.group(m.lastindex)]
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    mm_ = re.match(rx, nxt.strip())
                    if mm_ and not nxt.startswith("  "):
                        items.append(mm_.group(mm_.lastindex)); i += 1
                    elif nxt.startswith("  ") and nxt.strip():
                        items[-1] += " " + nxt.strip(); i += 1
                    else:
                        break
                blocks.append((kind, items, start))
                break
        else:
            if not s:
                flush()
            else:
                para.append(s)
            i += 1
    flush()
    return blocks


def load_md(path):
    text = Path(path).read_text(encoding="utf-8")
    meta = {}
    if text.startswith("---"):
        _, fm, text = text.split("---", 2)
        for ln in fm.strip().splitlines():
            k, _, v = ln.partition(":")
            meta[k.strip()] = v.strip()
    return meta, parse_blocks(text)


# ----------------------------------------------------------------------------
# Flowables especiais
# ----------------------------------------------------------------------------
RUN = {"right": "", "left": ""}


class Mark(Flowable):
    """Define cabeçalho/rodapé correntes e cria marcador (outline) no PDF."""
    def __init__(self, key, title, level, right="", left=""):
        super().__init__()
        self.key, self.title, self.level, self.right, self.left = key, title, level, right, left

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        RUN["right"], RUN["left"] = self.right, self.left
        if self.title:
            self.canv.bookmarkPage(self.key)
            self.canv.addOutlineEntry(self.title, self.key, self.level, closed=False)


class FullPage(Flowable):
    """Página inteira desenhada direto no canvas (capas, página de corte)."""
    def __init__(self, fn, *args):
        super().__init__()
        self.fn, self.args = fn, args

    def wrap(self, aw, ah):
        return (aw, ah - 0.01)

    def draw(self):
        c = self.canv
        c.saveState()
        c.translate(-MARGIN, -BOTTOM)
        self.fn(c, *self.args)
        c.restoreState()


HEADER = getattr(B, "HEADER", ("%s · %s" % (B.TITLE, B.TAGLINE)).upper())
PROJECT_LABELS = {ch["project"]["label"] for ch in B.CHAPTERS}


def is_project(label):
    return label in PROJECT_LABELS


def top_band(c):
    c.setFillColor(ORANGE)
    c.rect(0, H - 4 * mm, W, 4 * mm, stroke=0, fill=1)


def running(c, doc):
    c.saveState()
    top_band(c)
    c.setFont("Sans-B", 7.8); c.setFillColor(MUTED)
    c.drawString(MARGIN, H - 12 * mm, HEADER)
    c.setFont("Sans", 7.8)
    c.drawRightString(W - MARGIN, H - 12 * mm, RUN["right"])
    c.setStrokeColor(GRAY_BORDER); c.setLineWidth(0.6)
    c.line(MARGIN, H - 14.5 * mm, W - MARGIN, H - 14.5 * mm)
    c.line(MARGIN, 15 * mm, W - MARGIN, 15 * mm)
    c.setFont("Sans", 8)
    c.drawString(MARGIN, 10.5 * mm, RUN["left"])
    c.setFillColor(ORANGE); c.setFont("Sans-B", 8.5)
    c.drawRightString(W - MARGIN, 10.5 * mm, str(doc.page))
    c.restoreState()


def footer_only(c, left):
    c.setStrokeColor(GRAY_BORDER); c.setLineWidth(0.6)
    c.line(MARGIN, 15 * mm, W - MARGIN, 15 * mm)
    c.setFont("Sans", 8); c.setFillColor(MUTED)
    c.drawString(MARGIN, 10.5 * mm, left)


# ----------------------------------------------------------------------------
# Capas
# ----------------------------------------------------------------------------
def draw_book_cover(c, n_chapters_ready):
    top_band(c)
    c.setFont("Sans-B", 8.5); c.setFillColor(ORANGE)
    c.drawString(MARGIN, H - 62 * mm, getattr(B, "COVER_KICKER", ST["cover_kicker"]))
    c.setFont("Sans-B", 120); c.drawString(MARGIN - 3 * mm, H - 100 * mm, B.TITLE)
    c.setFillColor(TEXT); c.setFont("Sans-B", 30)
    c.drawString(MARGIN, H - 118 * mm, B.TAGLINE)
    sub = Paragraph(inline(B.SUBTITLE), PS("cs", fontName="Sans", fontSize=11.5, leading=16.5, textColor=MUTED))
    w, h = sub.wrap(135 * mm, 50 * mm)
    sub.drawOn(c, MARGIN, H - 128 * mm - h)
    c.setFillColor(ORANGE); c.rect(MARGIN, H - 137 * mm - h, 24 * mm, 1.1 * mm, stroke=0, fill=1)

    gap = 4 * mm
    cols = min(4, len(B.CHAPTERS))
    bw = (CONTENT_W - (cols - 1) * gap) / cols
    by = H - 170 * mm - h
    for i, ch in enumerate(B.CHAPTERS):
        x = MARGIN + (i % cols) * (bw + gap)
        by_i = by - (i // cols) * 31 * mm
        c.setStrokeColor(GRAY_BORDER); c.setLineWidth(0.7); c.setFillColor(WHITE)
        c.rect(x, by_i, bw, 26 * mm, stroke=1, fill=1)
        c.setFillColor(ORANGE); c.rect(x, by_i + 26 * mm - 1.2 * mm, bw, 1.2 * mm, stroke=0, fill=1)
        c.setFont("Sans-B", 17); c.drawString(x + 4 * mm, by_i + 13.5 * mm, ch["number"])
        c.setFillColor(TEXT); c.setFont("Sans-B", 10.5)
        c.drawString(x + 4 * mm, by_i + 7.2 * mm, ch["title"])
        c.setFillColor(MUTED); c.setFont("Sans", 8)
        c.drawString(x + 4 * mm, by_i + 3 * mm, ST["n_lessons"] % pl(len(ch["lessons"]), ST["w_lesson"]))

    rows = (len(B.CHAPTERS) + cols - 1) // cols
    c.setFont("Sans", 9.5); c.setFillColor(MUTED)
    c.drawString(MARGIN, by - (rows - 1) * 31 * mm - 12 * mm, B.AUDIENCE)
    footer_only(c, ST["edition"])


def draw_chapter_cover(c, ch, idx, existing):
    top_band(c)
    c.setFont("Sans-B", 7.8); c.setFillColor(MUTED)
    c.drawString(MARGIN, H - 12 * mm, HEADER)
    c.setFont("Sans", 7.8); c.drawRightString(W - MARGIN, H - 12 * mm, ST["chapter_cover"])
    c.setStrokeColor(GRAY_BORDER); c.setLineWidth(0.6)
    c.line(MARGIN, H - 14.5 * mm, W - MARGIN, H - 14.5 * mm)

    c.setFillColor(ORANGE); c.setFont("Sans-B", 110)
    c.drawString(MARGIN - 2 * mm, H - 100 * mm, ch["number"])
    c.setFont("Sans-B", 10); c.drawString(MARGIN, H - 117 * mm, ch["kicker"])
    c.setFillColor(TEXT); c.setFont("Sans-B", 40)
    c.drawString(MARGIN, H - 133 * mm, ch["title"])
    sub = Paragraph(inline(ch["subtitle"]), PS("cs", fontName="Sans", fontSize=11.5, leading=16.5, textColor=MUTED))
    w, h = sub.wrap(135 * mm, 40 * mm)
    sub.drawOn(c, MARGIN, H - 143 * mm - h)
    c.setFillColor(ORANGE); c.rect(MARGIN, H - 152 * mm - h, 24 * mm, 1.1 * mm, stroke=0, fill=1)

    top = H - 170 * mm - h
    c.setFont("Sans-B", 7.8); c.setFillColor(MUTED); c.drawString(MARGIN, top + 3 * mm, ST["in_chapter"])
    rh = 10.5 * mm
    n = len(ch["lessons"])
    c.setStrokeColor(GRAY_BORDER); c.setLineWidth(0.7)
    c.rect(MARGIN, top - rh * n, CONTENT_W, rh * n, stroke=1, fill=0)
    for i, ls in enumerate(ch["lessons"]):
        yy = top - rh * (i + 1)
        if i < n - 1:
            c.setStrokeColor(GRAY_LINE); c.line(MARGIN, yy, W - MARGIN, yy)
        ready = existing.get(ls["file"], False)
        c.setFillColor(ORANGE if ready else SLATE); c.setFont("Sans-B", 11)
        c.drawString(MARGIN + 5 * mm, yy + 3.6 * mm, ls["label"])
        c.setFillColor(TEXT if ready else MUTED); c.setFont("Sans", 10.5)
        c.drawString(MARGIN + 16 * mm, yy + 3.6 * mm, ls["title"])
        c.setFillColor(MUTED); c.setFont("Sans", 9)
        c.drawRightString(W - MARGIN - 5 * mm, yy + 3.7 * mm, ls["reading"])

    pj = ch["project"]
    py = top - rh * n - 6 * mm - 13 * mm
    c.setFillColor(ORANGE_BG); c.setStrokeColor(GRAY_BORDER)
    c.rect(MARGIN, py, CONTENT_W, 13 * mm, stroke=1, fill=1)
    c.setFillColor(ORANGE); c.rect(MARGIN, py, STRIPE, 13 * mm, stroke=0, fill=1)
    c.setFont("Sans-B", 7.5); c.drawString(MARGIN + 7 * mm, py + 8 * mm, ST["chapter_project"])
    c.setFillColor(TEXT); c.setFont("Sans", 10.5); c.drawString(MARGIN + 7 * mm, py + 3.2 * mm, pj["title"])
    c.setFillColor(MUTED); c.setFont("Sans", 9)
    c.drawRightString(W - MARGIN - 5 * mm, py + 3.4 * mm, pj["reading"])

    jy = 28 * mm
    c.setFont("Sans-B", 7.8); c.setFillColor(MUTED); c.drawString(MARGIN, jy + 9 * mm, ST["journey"])
    gap = 3 * mm
    nch = len(B.CHAPTERS)
    sw = (CONTENT_W - gap * (nch - 1)) / nch
    for i, other in enumerate(B.CHAPTERS):
        x = MARGIN + i * (sw + gap)
        c.setFillColor(ORANGE if i <= idx else GRAY_LINE)
        c.rect(x, jy + 3 * mm, sw, 1.8 * mm, stroke=0, fill=1)
        fnt = "Sans-B" if i == idx else "Sans"
        label = other.get("journey") or "%s  %s" % (other["number"], other["title"])
        fsz = 8.5
        while fsz > 5.5 and pdfmetrics.stringWidth(label, fnt, fsz) > sw:
            fsz -= 0.25
        c.setFont(fnt, fsz)
        c.setFillColor(ORANGE_DK if i == idx else MUTED)
        c.drawString(x, jy - 2 * mm, label)
    first = next((l for l in ch["lessons"] + [ch["project"]] if existing.get(l["file"])), ch["lessons"][0])
    footer_only(c, ST["next_stop"] % (first["label"], first["title"]))


def draw_cut_page(c, n_lessons):
    top_band(c)
    mid = H * 0.5 + 8 * mm
    c.setStrokeColor(MUTED); c.setLineWidth(0.9); c.setDash(5, 4)
    c.line(MARGIN, mid + 42 * mm, W - MARGIN, mid + 42 * mm)
    c.line(MARGIN, mid - 52 * mm, W - MARGIN, mid - 52 * mm)
    c.setDash()
    c.setFont("Sans", 7.8); c.setFillColor(MUTED)
    c.drawCentredString(W / 2, mid + 45 * mm, ST["cut_line"])
    c.setFillColor(ORANGE); c.setFont("Sans-B", 9)
    c.drawCentredString(W / 2, mid + 26 * mm, ST["spoilers"])
    c.setFillColor(TEXT); c.setFont("Sans-B", 44)
    c.drawCentredString(W / 2, mid + 4 * mm, ST["answers_word"])
    p = Paragraph(ST["cut_text"],
                  PS("cp", fontName="Sans", fontSize=11, leading=16, textColor=MUTED, alignment=1))
    w, h = p.wrap(125 * mm, 40 * mm)
    p.drawOn(c, (W - w) / 2, mid - 8 * mm - h)
    items = getattr(B, "CUT_CHECKLIST", ST["cut_checklist"])
    y = mid - 18 * mm - h
    for t in items:
        c.setStrokeColor(ORANGE); c.setLineWidth(1); c.setFillColor(WHITE)
        c.rect(W / 2 - 62 * mm, y - 0.5 * mm, 3.6 * mm, 3.6 * mm, stroke=1, fill=1)
        c.setFillColor(TEXT); c.setFont("Sans", 10.5)
        c.drawString(W / 2 - 55 * mm, y, t.replace("`", ""))
        y -= 8 * mm
    footer_only(c, ST["answers_footer"] % n_lessons)


# ----------------------------------------------------------------------------
# Plano do curso (gerado do manifesto)
# ----------------------------------------------------------------------------
def plan_flowables(existing):
    def num(txt):
        m = re.search(r"\d+", txt or "")
        return int(m.group()) if m else 0

    total_h = sum(num(ch.get("hours")) for ch in B.CHAPTERS)
    weeks = sum(num(ch.get("weeks")) for ch in B.CHAPTERS)
    n_less = sum(len(ch["lessons"]) for ch in B.CHAPTERS)
    out = title_block(ST["plan_kicker"], ST["plan_title"],
                      ST["plan_sub"] % (pl(n_less, ST["w_lesson"]),
                                        pl(len(B.CHAPTERS), ST["w_project"]), total_h,
                                        pl(weeks, ST["w_week"]), getattr(B, "HOURS_PER_WEEK", 6)))
    legend = Paragraph('<font color="%s">●</font> %s &nbsp;&nbsp; <font color="%s">○</font> %s'
                       " &nbsp;&nbsp; <i>%s</i>" % (ACC, ST["legend_ready"], SLATE_HEX,
                                                    ST["legend_pending"], ST["legend_note"]), small)
    out += [legend, Spacer(1, 8)]
    for ch in B.CHAPTERS:
        rows = [[Paragraph('<font color="%s"><b>%s</b></font>  <b>%s</b>' % (ACC_DK, esc(ch["number"]), esc(ch["title"])), cell),
                 "", Paragraph(" · ".join(x for x in (ch.get("hours"), ch.get("weeks")) if x),
                               PS("r", parent=cell_muted, alignment=2)), ""]]
        for ls in ch["lessons"] + [ch["project"]]:
            ready = existing.get(ls["file"], False)
            is_proj = is_project(ls["label"])
            lab = '<font color="%s"><b>%s</b></font>' % (ACC, ls["label"])
            ttl = ("<i>%s · %s</i>" % (ST["project"], esc(ls["title"]))) if is_proj else esc(ls["title"])
            mark = ('<font color="%s">●</font>' % ACC) if ready else ('<font color="%s">○</font>' % SLATE_HEX)
            rows.append([Paragraph(lab, cell), Paragraph(ttl, cell), Paragraph(ls["reading"], PS("r2", parent=cell_muted, alignment=2)),
                         Paragraph(mark, PS("m", parent=cell, alignment=1))])
        t = Table(rows, colWidths=[15 * mm, CONTENT_W - 15 * mm - 26 * mm - 12 * mm, 26 * mm, 12 * mm])
        t.setStyle(TableStyle([
            ("SPAN", (0, 0), (1, 0)), ("SPAN", (2, 0), (3, 0)),
            ("BOX", (0, 0), (-1, -1), 0.7, GRAY_BORDER), ("LINEBELOW", (0, 0), (-1, 0), 1.2, ORANGE),
            ("LINEBELOW", (0, 1), (-1, -2), 0.4, GRAY_LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.0),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, -1), (-1, -1), ORANGE_BG)]))
        out += [KeepTogether([t]), Spacer(1, 6)]
    return out


# ----------------------------------------------------------------------------
# Montagem do livro
# ----------------------------------------------------------------------------
def resolve(rel, exemplo=False):
    return ROOT / CONTENT_DIR / rel


def md_flowables(path, label=""):
    meta, blocks = load_md(path)
    ctx = {"label": label, "h2": 0, "listing": 0, "answers": []}
    items = None
    if "duration" in meta or "difficulty" in meta:
        diff = int(meta.get("difficulty", 0) or 0)
        items = [(ST["m_duration"], meta.get("duration", "—")), (ST["m_prereq"], meta.get("prereq", "—")),
                 (ST["m_difficulty"], "●" * diff + "○" * (5 - diff)),
                 (ST["m_deliverable"], meta.get("deliverable", "—"))]
    fl = title_block(meta.get("kicker", ""), meta.get("title", ""), meta.get("subtitle", ""), items)
    fl += render_blocks(blocks, ctx)
    return meta, fl, ctx["answers"]


def answers_flowables(entries):
    out = title_block(ST["ans_kicker"], ST["ans_title"], ST["ans_sub"])
    for i, (label, title, blocks) in enumerate(entries):
        out.append(Mark("ans-" + label, ST["ans_bookmark"] % label, 1, ST["answers_word"], ST["answers_word"]))
        head = Table([[Paragraph('<font color="%s"><b>%s</b></font>' % (ACC, esc((ST["project_up"] if is_project(label) else ST["lesson_up"]) + " " + label)), cell),
                       Paragraph("<b>%s</b>" % esc(title), PS("ah", parent=cell, fontSize=11))]],
                     colWidths=[24 * mm, CONTENT_W - 24 * mm])
        head.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.8, GRAY_BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        out += [Spacer(1, 10), head, Spacer(1, 8)]
        ctx = {"label": "", "h2": 0, "listing": 0, "answers": []}
        out += render_blocks(blocks, ctx)
    return out


def references_flowables():
    out = title_block(ST["refs_kicker"], ST["refs_title"], ST["refs_sub"])
    lw, rw = CONTENT_W * 0.64, CONTENT_W * 0.36
    for cat, refs in B.REFERENCES:
        rows = [[Paragraph('<font color="%s"><b>%s</b></font>' % (ACC_DK, esc(cat.upper())), PS("rc", parent=cell, fontSize=7.8)), ""]]
        for t, d, u in refs:
            rows.append([Paragraph("<b>%s</b><br/><font color='#7C7C86' size='8'>%s</font>" % (esc(t), esc(d)),
                                   PS("rt", parent=cell, fontSize=9, leading=11.2)),
                         Paragraph('<link href="%s"><font color="%s" size="7.2">%s</font></link>' % (u, ACC_DK, esc(u.replace("https://", ""))),
                                   PS("u", parent=cell, alignment=2, leading=9))])
        t = Table(rows, colWidths=[lw, rw])
        t.setStyle(TableStyle([("SPAN", (0, 0), (1, 0)), ("BOX", (0, 0), (-1, -1), 0.7, GRAY_BORDER),
                               ("LINEBELOW", (0, 0), (-1, 0), 1.0, ORANGE), ("LINEBELOW", (0, 1), (-1, -2), 0.4, GRAY_LINE),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2.6),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
        out += [t, Spacer(1, 6)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()
    out_path = Path(args.out) if args.out else ROOT / "dist" / OUT_NAME
    out_path.parent.mkdir(exist_ok=True)

    existing = {}
    for ch in B.CHAPTERS:
        for ls in ch["lessons"] + [ch["project"]]:
            existing[ls["file"]] = resolve(ls["file"]).exists()

    segments = [("blank", [Mark("capa", "Capa", 0), FullPage(draw_book_cover, 0)])]

    for item in B.FRONT:
        if item == "@plano":
            segments.append(("page", [Mark("plano", ST["plan_word"], 0, ST["guide"], ST["plan_word"])] + plan_flowables(existing)))
        else:
            meta, fl, _ = md_flowables(ROOT / item)
            segments.append(("page", [Mark(item, meta.get("title", item), 0, ST["guide"], meta.get("title", ""))] + fl))

    answers = []
    for idx, ch in enumerate(B.CHAPTERS):
        ready = [ls for ls in ch["lessons"] + [ch["project"]] if existing[ls["file"]]]
        if not ready:
            continue
        segments.append(("blank", [Mark("cap-" + ch["id"], "%s · %s" % (ch["number"], ch["title"]), 0),
                                   FullPage(draw_chapter_cover, ch, idx, existing)]))
        for ls in ready:
            print("  lendo", ls["file"])
            meta, fl, ans = md_flowables(resolve(ls["file"]), label=ls["label"])
            title = meta.get("title", ls["title"])
            proj = is_project(ls["label"])
            kind = ST["project_up"] if proj else "%s %s" % (ST["lesson_up"], ls["label"])
            hdr = "%s · %s" % (ch["hdr"], ST["project"] if proj else "%s %s" % (ST["lesson"], ls["label"]))
            # kicker padrão se o arquivo não definiu
            if not meta.get("kicker"):
                fl[1:1] = [Paragraph(esc("%s · %s" % (ch["short"], kind)), h_kicker)]
            segments.append(("page", [Mark("l-" + ls["label"], "%s · %s" % (ls["label"], title), 1, hdr, title)] + fl))
            for a in ans:
                answers.append((ls["label"], title, a))

    if answers:
        segments.append(("blank", [Mark("gabaritos", ST["answers_word"], 0), FullPage(draw_cut_page, len(answers))]))
        segments.append(("page", [Mark("gab-lista", ST["answers_run"], 1, ST["answers_word"], ST["answers_word"])] + answers_flowables(answers)))

    for item in B.BACK:
        meta, fl, _ = md_flowables(ROOT / item)
        segments.append(("page", [Mark(item, meta.get("title", item), 0, ST["appendix"], meta.get("title", ""))] + fl))
    segments.append(("page", [Mark("refs", ST["refs_word"], 0, ST["refs_word"], ST["refs_word"])] + references_flowables()))

    story = []
    for i, (kind, fl) in enumerate(segments):
        if i:
            story += [NextPageTemplate(kind), PageBreak()]
        story += fl

    frame = Frame(MARGIN, BOTTOM, CONTENT_W, H - BOTTOM - 22 * mm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc = BaseDocTemplate(str(out_path), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=22 * mm,
                          bottomMargin=BOTTOM, title=B.TITLE + " · " + B.TAGLINE, author=getattr(B, "AUTHOR", "Claude"))
    doc.addPageTemplates([PageTemplate(id="blank", frames=[frame]),
                          PageTemplate(id="page", frames=[frame], onPageEnd=running)])
    doc.build(story)
    pend = [k for k, v in existing.items() if not v]
    print("ok ->", out_path, "| ready: %d | pending: %d" % (len(existing) - len(pend), len(pend)))


if __name__ == "__main__":
    main()
