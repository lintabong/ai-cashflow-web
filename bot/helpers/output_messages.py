from collections import defaultdict
from decimal import Decimal

def render_grouped_table(data):
    if not data:
        return "Tidak ada data transaksi."

    grouped = defaultdict(list)
    for d in data:
        grouped[d["date"]].append(d)

    MAX_ITEM_LEN = 18
    result = ""
    for tanggal, transaksi in grouped.items():
        result += f"📅 Tanggal {tanggal}:\n"
        result += f"\nTransaksi via: {transaksi[0]['wallet']}\n"
        result += f"Ket: (o) outcome, (i) income\n"
        result += "```text\n"
        result += f"| {'Item':<18} | {'Qty':>3} | {'Harga':>8} | {'Subtotal':>8} |\n"
        result += f"|{'-'*20}|{'-'*5}|{'-'*10}|{'-'*10}|\n"
        for d in transaksi:
            quantity = d.get("quantity", 0)
            price = d.get("price", 0)
            total = quantity * price
            flow_label = '(i)' if d.get('flowType') == 'income' else '(o)' if d.get('flowType') == 'expense' else ''
            
            raw_name = d.get("activityName", "")
            item_label = f"{flow_label} {raw_name}".strip()

            # Potong jika terlalu panjang
            if len(item_label) > MAX_ITEM_LEN:
                item_label = item_label[:MAX_ITEM_LEN - 1] + "…"

            result += f"| {item_label:<18} | {quantity:>3} | {price:>8} | {total:>8} |\n"
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
    total_balance = 0
    for wallet in wallets:
        name = wallet['name']
        balance = wallet['balance']
        total_balance += balance
        result += f"| {name:<15} | {balance:>15,.2f} |\n"
    result += f"|{'-'*17}|{'-'*17}|\n"
    result += f"| {'TOTAL':<15} | {total_balance:>15,.2f} |\n"
    result += "```\n"
    return result
