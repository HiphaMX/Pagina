import requests

login_res = requests.post('https://www.hipha.mx/api/auth/login', data={'username': 'hola@hipha.mx', 'password': 'Celi@ThePug2026'})
print('Login status:', login_res.status_code)
token = login_res.json().get('access_token')

if token:
    headers = {'Authorization': f'Bearer {token}'}
    overview_res = requests.get('https://www.hipha.mx/api/dashboard/reconciliation/overview?month=2026-08&account_rfc=DEGF851127TK1', headers=headers)
    print('Overview:', overview_res.json())

    tx_res = requests.get('https://www.hipha.mx/api/dashboard/reconciliation/transactions?month=2026-08&account_rfc=DEGF851127TK1', headers=headers)
    txs = tx_res.json()
    print(f'Total txs returned: {len(txs)}')
    for t in txs:
        f = t.get('fecha')
        tip = t.get('tipo')
        m = t.get('monto')
        st = t.get('status_conciliacion')
        b = t.get('banco')
        c = t.get('concepto')
        print(f"{f} | {tip} | ${m:,.2f} | {st} | Banco: {b} | {c}")
