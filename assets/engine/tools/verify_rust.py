#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica o código de uma aula (.md) compilando cada bloco ```rust com rustc.

Flags na linha da cerca, depois de `rust` (ex.: ```rust fail file=src/main.rs caption="..."):
    (nenhuma)  o bloco DEVE compilar
    fail       o bloco DEVE falhar ao compilar (exemplo de erro)
    panic      deve compilar e DEVE dar panic ao executar
    run        compila e executa; a saída alimenta o bloco ```saida seguinte
    tokio      o bloco usa a biblioteca tokio: compila em um projeto cargo persistente (pasta
               livro_cargo no diretório temporário), e combina com fail/run/panic como os demais
    bevy test  compila e roda os #[test] com `cargo test` (a lógica de jogo se testa sem janela)
    bevy       o bloco usa o Bevy (versão fixada, ver BEVY_TOML): compila em um projeto cargo
               persistente. SEM `run` só compila (janela/GPU); com `run` executa (headless)
    test       compila com --test e roda os #[test] (uma thread, ordem estável); os
               testes DEVEM passar; a saída alimenta o bloco ```saida seguinte
    frag       trecho incompleto: não é verificado

Blocos ```erro e ```saida são preenchidos com a saída REAL quando se usa --fill:
    ```erro   -> usa o último bloco `fail` ou `panic` anterior
    ```saida  -> usa o último bloco `run` anterior

Uso:
    python tools/verify_code.py content/n1/aula_01.md            # só verifica
    python tools/verify_code.py content/n1/aula_01.md --fill     # verifica e reescreve erro/saida
    python tools/verify_code.py content/n1/aula_01.md --show     # mostra saídas no terminal
Requer `rustc` no PATH (edição 2021).
"""
import argparse
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path


def scan(lines):
    blocks, i = [], 0
    while i < len(lines):
        m = re.match(r"^(`{3,})(.*)$", lines[i].strip())
        if m:
            n, info, start = len(m.group(1)), m.group(2).strip(), i
            i += 1
            buf = []
            while i < len(lines) and not re.fullmatch(r"`{%d,}" % n, lines[i].strip()):
                buf.append(lines[i])
                i += 1
            try:
                toks = shlex.split(info)
            except ValueError:
                toks = info.split()
            blocks.append(dict(start=start, end=i, lang=toks[0] if toks else "", toks=toks[1:],
                               code="\n".join(buf), line=start + 1))
        i += 1
    return blocks


CARGO_DIR = Path(tempfile.gettempdir()) / "livro_cargo"
CARGO_TOML = """[package]
name = "bloco"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = { version = "=1.38.2", features = ["full"] }
"""


BEVY_DIR = Path(tempfile.gettempdir()) / "livro_cargo_bevy"
BEVY_TOML = """[package]
name = "bloco"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "=0.20.1"
avian3d = "=0.8.0"

[profile.dev]
opt-level = 1

[profile.dev.package."*"]
opt-level = 3
"""


def run_cargo(code, run=False, bevy=False, test=False):
    """Compila e roda o bloco em um projeto cargo (o tokio ou o bevy compilam uma vez só).

    O Bevy exige um rustc recente (o 1.97 ou mais): nesse caso o toolchain padrão é usado,
    ignorando RUSTUP_TOOLCHAIN."""
    d = BEVY_DIR if bevy else CARGO_DIR
    env = dict(os.environ)
    if bevy:
        env.pop("RUSTUP_TOOLCHAIN", None)
    (d / "src").mkdir(parents=True, exist_ok=True)
    modelo = BEVY_TOML if bevy else CARGO_TOML
    if not (d / "Cargo.toml").exists() or (d / "Cargo.toml").read_text(encoding="utf-8") != modelo:
        (d / "Cargo.toml").write_text(modelo, encoding="utf-8")  # mantém as dependências em dia
    (d / "src" / "main.rs").write_text(code + "\n", encoding="utf-8")
    c = subprocess.run(["cargo", "build", "-q", "--color", "never"], cwd=d, env=env,
                       capture_output=True, text=True)
    res = dict(ok=c.returncode == 0, cstderr=c.stderr, out="", err="", code=None)
    if c.returncode == 0 and test:
        # roda `cargo test` (uma thread, ordem estável) e guarda a saída dos testes
        t = subprocess.run(["cargo", "test", "--color", "never", "--", "--test-threads=1"],
                           cwd=d, env=env, capture_output=True, text=True, timeout=900)
        res.update(out=t.stdout, err=t.stderr, code=t.returncode)
        return res
    if c.returncode == 0 and run:
        env = dict(env, RUST_BACKTRACE="0")
        tdir = Path(os.environ.get("CARGO_TARGET_DIR", d / "target"))
        r = subprocess.run([str(tdir / "debug" / "bloco")], cwd=d,
                           capture_output=True, text=True, env=env, timeout=120)
        res.update(out=r.stdout, err=r.stderr, code=r.returncode)
    return res


def run_rust(code, run=False, test=False):
    with tempfile.TemporaryDirectory() as d:
        Path(d, "src").mkdir()
        Path(d, "src", "main.rs").write_text(code + "\n", encoding="utf-8")
        c = subprocess.run(["rustc", "--edition", "2021", "--color", "never", "-o", "main", "src/main.rs"]
                           + (["--test"] if test else []),
                           cwd=d, capture_output=True, text=True)
        res = dict(ok=c.returncode == 0, cstderr=c.stderr, out="", err="", code=None)
        if c.returncode == 0 and run:
            env = dict(os.environ, RUST_BACKTRACE="0")
            cmd = ["./main"] + (["--test-threads=1", "--color", "never"] if test else [])
            r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, env=env,
                               timeout=20)
            res.update(out=r.stdout, err=r.stderr, code=r.returncode)
        return res


LIMIT = 96


def wrap_line(line, limit=LIMIT):
    """Quebra linhas longas preservando o recuo da mensagem do compilador."""
    if len(line) <= limit:
        return [line]
    m = re.match(r"^(\s*\d*\s*\|)(\s*[-^~]*\s*)(.*)$", line)
    if m:
        first, cont = m.group(1) + m.group(2), re.sub(r"\d", " ", m.group(1)) + " " * len(m.group(2))
        text = m.group(3)
    else:
        m = re.match(r"^(\s*(?:= )?(?:help|note): )(.*)$", line)
        if not m:
            m = re.match(r"^((?:error|warning)(?:\[[A-Z]\d+\])?: )(.*)$", line)
            if m:
                first, cont, text = m.group(1), "    ", m.group(2)
                return _fill(first, cont, text, limit)
            return [line]
        first, cont, text = m.group(1), " " * len(m.group(1)), m.group(2)
    return _fill(first, cont, text, limit)


def _fill(first, cont, text, limit):
    out, cur, prefix = [], "", first
    for w in text.split(" "):
        if cur and len(prefix) + len(cur) + 1 + len(w) > limit:
            out.append(prefix + cur)
            cur, prefix = w, cont
        else:
            cur = (cur + " " + w) if cur else w
    out.append(prefix + cur)
    return out


def clean(text):
    """Remove ruído de macros e quebra linhas largas."""
    kept = []
    text = re.sub(r"/rustc/[0-9a-f]{40}/", "/rustc/.../", text)
    text = re.sub(r"\S*/registry/src/[^/\s]+/", ".../", text)
    for ln in text.split("\n"):
        if re.match(r"^\s*= note: this error originates in the macro", ln):
            if kept and re.match(r"^\s*\|\s*$", kept[-1]):
                kept.pop()
            continue
        kept.extend(wrap_line(ln))
    return "\n".join(kept)


def compiler_errors(stderr, max_errors=None):
    """Mantém só os diagnósticos 'error' (sem warnings e sem o rodapé 'aborting')."""
    parts = re.split(r"\n\n+", stderr.strip())
    keep = [p for p in parts if p.startswith("error") and not p.startswith("error: aborting")
            and not p.startswith("error: could not compile")]
    if max_errors:
        keep = keep[:max_errors]
    return clean("\n\n".join(keep))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--fill", action="store_true", help="reescreve blocos erro/saida com a saída real")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    path = Path(a.md)
    lines = path.read_text(encoding="utf-8").split("\n")
    blocks = scan(lines)
    last_fail = last_run = None
    problems, warnings = 0, 0
    replace = {}

    for idx, b in enumerate(blocks):
        flags = set(t for t in b["toks"] if "=" not in t)
        if b["lang"] == "rust" and "frag" not in flags:
            fail, panic = "fail" in flags, "panic" in flags
            test = "test" in flags
            run = "run" in flags or panic or test
            if "tokio" in flags or "bevy" in flags:
                r = run_cargo(b["code"], run=run, bevy="bevy" in flags, test=test)
            else:
                r = run_rust(b["code"], run=run, test=test)
            tag = "linha %d" % b["line"]
            if fail:
                if r["ok"]:
                    print("  ✗ %s: devia FALHAR e compilou" % tag); problems += 1
                else:
                    print("  ✓ %s: falha como esperado" % tag)
                    mx = next((int(t.split("=")[1]) for t in b["toks"] if t.startswith("max=")), None)
                    last_fail = compiler_errors(r["cstderr"], mx)
                    if a.show:
                        print(last_fail, "\n")
            elif not r["ok"]:
                print("  ✗ %s: NÃO compilou:\n%s" % (tag, r["cstderr"])); problems += 1
            else:
                nw = r["cstderr"].count("warning:")
                warnings += nw
                msg = "  ✓ %s: compila" % tag + (" (%d aviso(s))" % nw if nw else "")
                if panic:
                    if r["code"] == 0:
                        msg = "  ✗ %s: devia dar panic e terminou normalmente" % tag; problems += 1
                    else:
                        msg = "  ✓ %s: compila e dá panic como esperado" % tag
                        last_fail = clean(r["err"].strip())
                elif run and r["code"] != 0:
                    msg = "  ✗ %s: terminou com erro (%s)" % (tag, r["err"].strip()[:120]); problems += 1
                print(msg)
                if run and not panic:
                    last_run = r["out"].strip("\n")
                if a.show and run:
                    print("    saída:", r["out"].rstrip("\n").replace("\n", "\n           "), "\n")
        elif b["lang"] == "erro":
            if last_fail is None:
                print("  ✗ linha %d: bloco erro sem bloco fail/panic antes" % b["line"]); problems += 1
            else:
                replace[idx] = last_fail
        elif b["lang"] == "saida":
            if last_run is None:
                print("  ✗ linha %d: bloco saida sem bloco run antes" % b["line"]); problems += 1
            else:
                replace[idx] = last_run

    if a.fill and replace:
        for idx in sorted(replace, reverse=True):
            b = blocks[idx]
            lines[b["start"] + 1:b["end"]] = replace[idx].split("\n")
        path.write_text("\n".join(lines), encoding="utf-8")
        print("  → %d bloco(s) erro/saida atualizados com a saída real" % len(replace))
    print("%s: %d problema(s), %d aviso(s) de compilação" % (path.name, problems, warnings))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
