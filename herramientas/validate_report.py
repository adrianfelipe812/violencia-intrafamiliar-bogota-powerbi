"""Valida todos los JSON del informe PBIR contra su $schema (descargando referencias remotas)."""
import json, os, sys, urllib.request
from jsonschema import Draft7Validator, Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

CACHE = {}
def retrieve(uri):
    if uri not in CACHE:
        with urllib.request.urlopen(uri) as r:
            CACHE[uri] = json.loads(r.read().decode("utf-8"))
    return Resource.from_contents(CACHE[uri], default_specification=DRAFT7)

registry = Registry(retrieve=retrieve)
root = sys.argv[1]
errors = 0; checked = 0
for dp, _, files in os.walk(os.path.join(root, "definition")):
    for f in files:
        if not f.endswith(".json"): continue
        p = os.path.join(dp, f)
        doc = json.load(open(p, encoding="utf-8"))
        sch_uri = doc.get("$schema")
        if not sch_uri: continue
        schema = retrieve(sch_uri).contents
        V = Draft202012Validator if "2020-12" in str(schema.get("$schema", "")) else Draft7Validator
        v = V(schema, registry=registry)
        errs = list(v.iter_errors(doc)); checked += 1
        for e in errs[:5]:
            errors += 1
            print("ERROR", os.path.relpath(p, root), "->", "/".join(map(str, e.absolute_path)), ":", e.message[:300])
print(f"Revisados {checked} archivos, {errors} errores")
