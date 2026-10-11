import os
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.reconciliation import BankTransaction, CFDIInvoice

env_vars = dotenv_values('.env.prod')
db_url = env_vars.get('DATABASE_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
db = Session()

print("=== TRANSACTIONS FOR 2026-08 (DEGF851127TK1) ===")
txs = db.query(BankTransaction).filter(
    BankTransaction.account_rfc == 'DEGF851127TK1',
    BankTransaction.periodo_mes == '2026-08'
).order_by(BankTransaction.fecha).all()

print(f"Total txs: {len(txs)}")
ingresos = [t for t in txs if t.tipo == 'INGRESO']
egresos = [t for t in txs if t.tipo == 'EGRESO']

print(f"Total Ingresos ({len(ingresos)}): ${sum(t.monto for t in ingresos):,.2f}")
for t in ingresos:
    print(f"  ING | {t.fecha.strftime('%Y-%m-%d')} | ${t.monto:,.2f} | {t.status_conciliacion} | {t.banco} | {t.concepto}")

print(f"Total Egresos ({len(egresos)}): ${sum(t.monto for t in egresos):,.2f}")
for t in egresos:
    print(f"  EGR | {t.fecha.strftime('%Y-%m-%d')} | ${t.monto:,.2f} | {t.status_conciliacion} | {t.banco} | {t.concepto}")

print("\n=== CFDIs FOR 2026-08 (DEGF851127TK1) ===")
cfdis = db.query(CFDIInvoice).filter(
    CFDIInvoice.account_rfc == 'DEGF851127TK1'
).all()
cfdis_aug = [c for c in cfdis if c.fecha_emision and c.fecha_emision.strftime('%Y-%m') == '2026-08']
print(f"Total CFDIs in August: {len(cfdis_aug)}")
for c in cfdis_aug:
    print(f"  CFDI | {c.fecha_emision.strftime('%Y-%m-%d')} | {c.tipo} | ${c.total:,.2f} | Conciliado={c.conciliado} | {c.nombre_emisor} -> {c.nombre_receptor}")
