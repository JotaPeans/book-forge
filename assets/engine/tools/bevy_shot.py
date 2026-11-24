#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Captura uma imagem de um exemplo de Bevy com janela, para conferir o resultado visual.

    python tools/bevy_shot.py content/extra/aula_B3.md 120 /tmp/saida.png [quadros]

`120` é o número da linha (a primeira do bloco ```rust ... bevy ...). O bloco é compilado no
projeto de verificação com o plugin de tools/bevy_shot/shot.rs injetado no primeiro
`App::new()`; ele redireciona a câmera para uma textura (a janela sai preta em uma máquina sem
sessão gráfica), captura o quadro `quadros` (padrão 60) e fecha o app.
Se o bloco tem vários arquivos (mod), passe o caminho de um .rs em vez do .md.
"""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verify_code import BEVY_DIR, BEVY_TOML, scan  # noqa: E402


def main():
    fonte, linha, saida = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]).resolve()
    quadros = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    if fonte.endswith(".md"):
        blocos = scan(Path(fonte).read_text(encoding="utf-8").split("\n"))
        bloco = next(b for b in blocos if b["line"] == linha)
        codigo = bloco["code"]
    else:
        codigo = Path(fonte).read_text(encoding="utf-8")

    assert "App::new()" in codigo, "o bloco precisa criar um App::new()"
    codigo = codigo.replace(
        "App::new()",
        'App::new().add_plugins(shot::Shot { path: "%s", frames: %d })' % (saida, quadros), 1)
    codigo = "mod shot;\n" + codigo

    (BEVY_DIR / "src").mkdir(parents=True, exist_ok=True)
    if not (BEVY_DIR / "Cargo.toml").exists() or (BEVY_DIR / "Cargo.toml").read_text(encoding="utf-8") != BEVY_TOML:
        (BEVY_DIR / "Cargo.toml").write_text(BEVY_TOML, encoding="utf-8")
    (BEVY_DIR / "src" / "main.rs").write_text(codigo, encoding="utf-8")
    (BEVY_DIR / "src" / "shot.rs").write_text(
        (Path(__file__).parent / "bevy_shot" / "shot.rs").read_text(encoding="utf-8"), encoding="utf-8")

    env = {k: v for k, v in os.environ.items() if k != "RUSTUP_TOOLCHAIN"}
    env["BEVY_ASSET_ROOT"] = str(BEVY_DIR)  # a pasta assets/ do projeto de verificação
    c = subprocess.run(["cargo", "build", "-q", "--color", "never"], cwd=BEVY_DIR, env=env,
                       capture_output=True, text=True)
    if c.returncode:
        print(c.stderr)
        sys.exit(1)
    tdir = Path(env.get("CARGO_TARGET_DIR", BEVY_DIR / "target"))
    saida.unlink(missing_ok=True)
    r = subprocess.run([str(tdir / "debug" / "bloco")], cwd=BEVY_DIR, env=env,
                       capture_output=True, text=True, timeout=180)
    print("código de saída:", r.returncode)
    print("imagem:", saida if saida.exists() else "NÃO GERADA")
    if not saida.exists():
        print((r.stdout + r.stderr)[-1500:])


if __name__ == "__main__":
    main()
