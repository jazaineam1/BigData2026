#!/usr/bin/env python3
"""Comprueba referencias locales literales del sitio estático."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ATTRS={"href","src","poster"}
SKIP_PREFIXES=("#","mailto:","tel:","data:","javascript:","http://","https://","//")

class RefParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ATTRS and value:
                self.refs.append((tag,key,value))

def target_for(root:Path,source:Path,raw:str):
    raw=raw.strip()
    if not raw or raw.startswith(SKIP_PREFIXES) or "{{" in raw or "${" in raw:
        return None
    path=unquote(urlsplit(raw).path)
    if not path:
        return source
    if path.startswith("/BigData2026/"):
        return root/path[len("/BigData2026/"):]
    if path.startswith("/"):
        return root/path[1:]
    return (source.parent/path).resolve()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path("."))
    ap.add_argument("--allow-missing",action="append",default=[],help="Ruta relativa al root generada en otra etapa")
    args=ap.parse_args()
    root=args.root.resolve()
    if not root.exists():
        raise SystemExit(f"LINK CHECK: no existe {root}")
    allowed={(root/Path(p)).resolve() for p in args.allow_missing}
    checked=0
    errors=[]
    html_files=sorted(root.rglob("*.html"))
    for source in html_files:
        parser=RefParser()
        parser.feed(source.read_text("utf-8",errors="replace"))
        for tag,attr,raw in parser.refs:
            target=target_for(root,source,raw)
            if target is None:
                continue
            checked+=1
            try:
                target.relative_to(root)
            except ValueError:
                errors.append((source,raw,"sale del artefacto"))
                continue
            if not target.exists() and target not in allowed:
                errors.append((source,raw,str(target.relative_to(root))))
    if errors:
        print(f"LINK CHECK: FAIL · {len(errors)} referencia(s) local(es) rota(s)")
        for source,raw,target in errors:
            print(f" - {source.relative_to(root)} · {raw!r} -> {target}")
        raise SystemExit(1)
    print(f"LINK CHECK: OK · {len(html_files)} HTML · {checked} referencias locales verificadas")
if __name__=="__main__":
    main()
