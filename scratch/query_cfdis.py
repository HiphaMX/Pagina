import requests

login_res = requests.post('https://www.hipha.mx/api/auth/login', data={'username': 'hola@hipha.mx', 'password': 'Celi@ThePug2026'})
token = login_res.json().get('access_token')

if token:
    headers = {'Authorization': f'Bearer {token}'}
    cfdi_res = requests.get('https://www.hipha.mx/api/dashboard/reconciliation/invoices?account_rfc=DEGF851127TK1', headers=headers)
    cfdis = cfdi_res.json()
    print(f'Total CFDIs in DB: {len(cfdis)}')
    for c in cfdis:
        print(f"{c.get('fecha_emision')} | {c.get('tipo')} | ${c.get('total'):,.2f} | {c.get('nombre_emisor')[:30]} -> {c.get('nombre_receptor')[:30]} | {c.get('conceptos_resumen')[:40] if c.get('conceptos_resumen') else ''}")
