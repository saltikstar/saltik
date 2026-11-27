"""Validate published JSON-LD syntax and terms against the official Schema.org vocabulary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import urlopen

from lxml import html


VOCABULARY = "https://schema.org/version/latest/schemaorg-current-https.jsonld"


def validate(page_url: str) -> dict:
    with urlopen(page_url, timeout=30) as response:
        page = html.fromstring(response.read())
    with urlopen(VOCABULARY, timeout=30) as response:
        vocabulary = json.load(response)
    classes = {entry["@id"][7:] for entry in vocabulary["@graph"]
               if entry["@id"].startswith("schema:") and entry.get("@type") == "rdfs:Class"}
    properties = {entry["@id"][7:] for entry in vocabulary["@graph"]
                  if entry["@id"].startswith("schema:") and entry.get("@type") == "rdf:Property"}
    scripts = page.xpath('//head/script[@type="application/ld+json"]')
    errors: list[str] = []
    types: set[str] = set()
    defined_ids: set[str] = set()
    referenced_ids: set[str] = set()

    if len(scripts) != 1:
        errors.append(f"Expected one JSON-LD script, found {len(scripts)}")
    for script in scripts:
        try:
            data = json.loads(script.text)
        except json.JSONDecodeError as error:
            errors.append(f"JSON syntax: {error}")
            continue
        if data.get("@context") != "https://schema.org":
            errors.append("Unexpected @context")

        def walk(value, path: str = "$", parent_has_type: bool = False):
            if isinstance(value, list):
                for index, item in enumerate(value):
                    walk(item, f"{path}[{index}]")
            elif isinstance(value, dict):
                name = value.get("@type")
                if name:
                    names = name if isinstance(name, list) else [name]
                    for item in names:
                        types.add(item)
                        if item not in classes:
                            errors.append(f"{path}: unknown Schema.org type {item}")
                identifier = value.get("@id")
                if identifier:
                    (defined_ids if name else referenced_ids).add(identifier)
                for key, item in value.items():
                    if key.startswith("@"):
                        if key == "@graph":
                            walk(item, f"{path}.@graph")
                        continue
                    if key not in properties:
                        errors.append(f"{path}: unknown Schema.org property {key}")
                    walk(item, f"{path}.{key}")

        walk(data)
    for identifier in referenced_ids - defined_ids:
        errors.append(f"Unresolved @id reference: {identifier}")
    required = {"Dentist", "WebSite", "WebPage", "OfferCatalog"}
    for name in sorted(required - types):
        errors.append(f"Missing required type: {name}")
    return {"url": page_url, "vocabulary": VOCABULARY, "jsonld_scripts": len(scripts),
            "types": sorted(types), "errors": errors, "valid": not errors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["valid"] else 1)
