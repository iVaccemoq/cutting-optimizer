def get_bounding_box(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return {
        "width": max(xs) - min(xs),
        "height": max(ys) - min(ys)
    }


def translate_points(points, dx, dy):
    return [[x + dx, y + dy] for x, y in points]


def optimize_cut(sheet, parts):
    """
    Guillotine + Best Fit для деталей,
    заданных координатами вершин.
    """

    placements = []

    free_rects = [{
        "x": 0,
        "y": 0,
        "width": sheet["width"],
        "height": sheet["height"]
    }]

    total_area = sheet["width"] * sheet["height"]
    used_area = 0

    for part in parts:
        bbox = get_bounding_box(part["points"])
        pw, ph = bbox["width"], bbox["height"]

        best_fit = None

        for rect in free_rects:
            if pw <= rect["width"] and ph <= rect["height"]:
                leftover = (rect["width"] - pw) * (rect["height"] - ph)
                if best_fit is None or leftover < best_fit["leftover"]:
                    best_fit = {"rect": rect, "leftover": leftover}

        if best_fit is None:
            continue

        r = best_fit["rect"]

        placed_points = translate_points(
            part["points"],
            r["x"],
            r["y"]
        )

        placements.append({
            "original_points": part["points"],
            "placed_points": placed_points,
            "x": r["x"],
            "y": r["y"]
        })

        used_area += pw * ph

        free_rects.remove(r)

        if r["width"] - pw > 0:
            free_rects.append({
                "x": r["x"] + pw,
                "y": r["y"],
                "width": r["width"] - pw,
                "height": ph
            })

        if r["height"] - ph > 0:
            free_rects.append({
                "x": r["x"],
                "y": r["y"] + ph,
                "width": r["width"],
                "height": r["height"] - ph
            })

    waste = round((1 - used_area / total_area) * 100, 2)

    return {
        "placements": placements,
        "waste": waste
    }
