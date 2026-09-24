#!/usr/bin/env python3
"""Validate the SAP MM mock dataset and optionally copy it to a deployment directory."""
from __future__ import annotations
import argparse, json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "mock_data"
FILES = ("purchase_orders.json","purchase_requisitions.json","goods_receipts.json",
         "invoices.json","vendors.json","users.json")

def load(path):
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON list.")
    return data

def value(r, *keys):
    for k in keys:
        if r.get(k) is not None:
            return str(r[k])
    return None

def idx(rows, *keys):
    return {value(r,*keys): r for r in rows if value(r,*keys)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    source=a.source.resolve()
    data={}
    for name in FILES:
        path=source/name
        if not path.exists():
            print(f"ERROR: missing {path}",file=sys.stderr); return 1
        data[name]=load(path)

    pos=idx(data["purchase_orders.json"],"po_number","purchase_order","id")
    prs=idx(data["purchase_requisitions.json"],"pr_number","purchase_requisition","id")
    vendors=idx(data["vendors.json"],"vendor_id","vendor","id")
    users=idx(data["users.json"],"user_id","username","id")
    errors=[]; warnings=[]

    for po_id,po in pos.items():
        v=value(po,"vendor_id","vendor")
        pr=value(po,"pr_number","purchase_requisition")
        if v and v not in vendors: errors.append(f"PO {po_id}: unknown vendor {v}")
        if pr and pr not in prs: warnings.append(f"PO {po_id}: PR {pr} is absent from mock PR data")

    for gr in data["goods_receipts.json"]:
        gid=value(gr,"gr_number","goods_receipt","id") or "<unknown>"
        po=value(gr,"po_number","purchase_order"); user=value(gr,"posted_by","user_id")
        if po and po not in pos: errors.append(f"GR {gid}: unknown PO {po}")
        if user and user not in users: errors.append(f"GR {gid}: unknown user {user}")

    for inv in data["invoices.json"]:
        iid=value(inv,"invoice_number","invoice","id") or "<unknown>"
        po=value(inv,"po_number","purchase_order"); v=value(inv,"vendor_id","vendor")
        if po and po not in pos: errors.append(f"Invoice {iid}: unknown PO {po}")
        if v and v not in vendors: errors.append(f"Invoice {iid}: unknown vendor {v}")

    for w in warnings: print("WARNING:",w)
    if errors:
        for e in errors: print("ERROR:",e,file=sys.stderr)
        return 1

    print(f"Validation passed: {sum(map(len,data.values()))} records across {len(FILES)} files.")
    if a.output:
        out=a.output.resolve(); out.mkdir(parents=True,exist_ok=True)
        for name in FILES: shutil.copy2(source/name,out/name)
        print(f"Seeded: {out}")
    return 0

if __name__=="__main__":
    sys.exit(main())
