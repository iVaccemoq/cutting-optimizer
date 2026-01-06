from copy import deepcopy


def best_subset(cuts, stock_length, kerf):
    """
    Подбор набора отрезков с максимальной суммой <= stock_length
    с учётом толщины лезвия (kerf)
    """

    best_sum = 0
    best_combo = []

    cuts = sorted(cuts, key=lambda x: -x["length"])

    def backtrack(index, current_sum, combo):
        nonlocal best_sum, best_combo

        effective_sum = current_sum + kerf * len(combo)
        if effective_sum > stock_length:
            return

        if effective_sum > best_sum:
            best_sum = effective_sum
            best_combo = combo[:]

        if index >= len(cuts):
            return

        remaining_max = current_sum + sum(c["length"] for c in cuts[index:])
        if remaining_max + kerf * len(combo) <= best_sum:
            return

        # взять текущий
        backtrack(
            index + 1,
            current_sum + cuts[index]["length"],
            combo + [cuts[index]]
        )

        # не брать
        backtrack(index + 1, current_sum, combo)

    backtrack(0, 0, [])
    return best_combo


def optimize_cut(stocks: list, cuts: list, settings: dict | None = None):
    """
    SmartCut-подобный линейный раскрой
    Поддержка:
    - толщина лезвия (kerf)
    - торцовка (trimming)
    """

    settings = settings or {}
    kerf = settings.get("kerf", 0)
    trimming = settings.get("trimming", 0)

    materials = set(s["material"] for s in stocks) | set(c["material"] for c in cuts)

    result = {
        "materials": {},
        "total_waste_percent": 0
    }

    total_stock_length = 0
    total_waste_length = 0

    for material in materials:
        material_stocks = [s for s in stocks if s["material"] == material]
        material_cuts = [c for c in cuts if c["material"] == material]

        # --- заготовки ---
        expanded_stocks = []
        for s in material_stocks:
            for _ in range(s.get("quantity", 1)):
                effective_length = max(0, s["length"] - trimming)
                expanded_stocks.append({
                    "length": effective_length,
                    "original_length": s["length"],
                    "remaining": effective_length,
                    "name": s["name"],
                    "priority": s.get("priority", 0),
                    "cuts": []
                })

        expanded_stocks.sort(key=lambda x: (x["priority"], -x["length"]))

        # --- отрезки ---
        expanded_cuts = []
        for c in material_cuts:
            for _ in range(c.get("quantity", 1)):
                expanded_cuts.append({
                    "length": c["length"],
                    "name": c["name"]
                })

        remaining_cuts = expanded_cuts[:]

        # --- основной алгоритм ---
        for stock in expanded_stocks:
            if not remaining_cuts:
                break

            combo = best_subset(remaining_cuts, stock["length"], kerf)
            if not combo:
                continue

            total_cut_len = sum(c["length"] for c in combo)
            kerf_loss = kerf * len(combo)

            stock["cuts"] = combo
            stock["remaining"] = stock["length"] - total_cut_len - kerf_loss

            for c in combo:
                remaining_cuts.remove(c)

        used_stocks = [s for s in expanded_stocks if s["cuts"]]
        unused_stocks = [
            {"length": s["original_length"], "name": s["name"]}
            for s in expanded_stocks if not s["cuts"]
        ]

        material_stock_length = sum(s["original_length"] for s in used_stocks)
        material_waste_length = sum(s["remaining"] for s in used_stocks)

        waste_percent = (
            round(material_waste_length / material_stock_length * 100, 2)
            if material_stock_length > 0 else 0
        )

        total_stock_length += material_stock_length
        total_waste_length += material_waste_length

        result["materials"][material] = {
            "used_stocks": len(used_stocks),
            "used_cuts": sum(len(s["cuts"]) for s in used_stocks),
            "waste_percent": waste_percent,
            "stocks": used_stocks,
            "unused_cuts": remaining_cuts,
            "unused_stocks": unused_stocks
        }

    result["total_waste_percent"] = (
        round(total_waste_length / total_stock_length * 100, 2)
        if total_stock_length > 0 else 0
    )

    return result



