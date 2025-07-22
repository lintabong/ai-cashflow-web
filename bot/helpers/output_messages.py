from collections import defaultdict
from decimal import Decimal


def render_grouped_table(data):
    if not data:
        return "Tidak ada data transaksi."

    grouped = defaultdict(list)
    for d in data:
        grouped[d["date"]].append(d)

    result = ""
    for tanggal, transaksi in grouped.items():
        result += f"📅 Tanggal {tanggal}:\n"
        result += "```text\n"
        result += f"| {'Item':<18} | {'Jumlah':>6} | {'Harga':>9} | {'Total':>9} |\n"
        result += f"|{'-'*20}|{'-'*8}|{'-'*11}|{'-'*11}|\n"
        for d in transaksi:
            quantity = d.get("quantity", 0)
            price = d.get("price", 0)
            total = quantity * price
            flow_label = '(in) ' if d.get('flowType') == 'income' else '(out)' if d.get('flowType') == 'expense' else ''
            item_label = f"{flow_label} {d['activityName']}"
            result += f"| {item_label:<18} | {quantity:>6} | {price:>9} | {total:>9} |\n"
        result += "```\n\n"
    return result

def render_wallet_summary(wallets):
    if not wallets:
        return "Tidak ada data dompet."

    result = ""
    result += "💼 Ringkasan Dompet:\n"
    result += ""
    result += "```text\n"
    result += f"| {'Nama Dompet':<15} | {'Saldo':>15} |\n"
    result += f"|{'-'*17}|{'-'*17}|\n"
    total_balance = Decimal("0.00")
    for wallet in wallets:
        name = wallet['name']
        balance = wallet['balance']
        total_balance += balance
        result += f"| {name:<15} | {balance:>15,.2f} |\n"
    result += f"|{'-'*17}|{'-'*17}|\n"
    result += f"| {'TOTAL':<15} | {total_balance:>15,.2f} |\n"
    result += "```\n"
    return result
