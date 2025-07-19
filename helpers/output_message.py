from collections import defaultdict


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

