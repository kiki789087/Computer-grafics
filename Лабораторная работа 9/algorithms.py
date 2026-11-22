INSIDE = 0
LEFT   = 1
RIGHT  = 2
BOTTOM = 4
TOP    = 8

def compute_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    return code

def sutherland_cohen(x1, y1, x2, y2, xmin, ymin, xmax, ymax):

    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)
    accept = False

    while True:
        if (code1 | code2) == 0:
            accept = True
            break
        elif (code1 & code2) != 0:
            break
        else:
            code_out = code1 if code1 != 0 else code2
            x, y = 0.0, 0.0
            if code_out & TOP:
                if y2 == y1:
                    break
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif code_out & BOTTOM:
                if y2 == y1:
                    break
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif code_out & RIGHT:
                if x2 == x1:
                    break
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax
            elif code_out & LEFT:
                if x2 == x1:
                    break
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin
            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        return x1, y1, x2, y2, True
    return x1, y1, x2, y2, False

def simple_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    if x1 != x2:
        t = (xmin - x1) / (x2 - x1)
        if 0 <= t <= 1:
            y = y1 + t * (y2 - y1)
            if ymin <= y <= ymax:
                if x1 < xmin:
                    x1, y1 = xmin, y
                elif x2 < xmin:
                    x2, y2 = xmin, y

    if x1 != x2:
        t = (xmax - x1) / (x2 - x1)
        if 0 <= t <= 1:
            y = y1 + t * (y2 - y1)
            if ymin <= y <= ymax:
                if x1 > xmax:
                    x1, y1 = xmax, y
                elif x2 > xmax:
                    x2, y2 = xmax, y

    if y1 != y2:
        t = (ymin - y1) / (y2 - y1)
        if 0 <= t <= 1:
            x = x1 + t * (x2 - x1)
            if xmin <= x <= xmax:
                if y1 < ymin:
                    x1, y1 = x, ymin
                elif y2 < ymin:
                    x2, y2 = x, ymin

    if y1 != y2:
        t = (ymax - y1) / (y2 - y1)
        if 0 <= t <= 1:
            x = x1 + t * (x2 - x1)
            if xmin <= x <= xmax:
                if y1 > ymax:
                    x1, y1 = x, ymax
                elif y2 > ymax:
                    x2, y2 = x, ymax

    visible = (xmin <= x1 <= xmax and ymin <= y1 <= ymax and
               xmin <= x2 <= xmax and ymin <= y2 <= ymax)
    return x1, y1, x2, y2, visible

def midpoint_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax, eps=0.5):

    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    if (code1 | code2) == 0:
        return x1, y1, x2, y2, True
    if (code1 & code2) != 0:
        return x1, y1, x2, y2, False

    def find_visible_point(px, py, qx, qy):
        if compute_code(px, py, xmin, ymin, xmax, ymax) == 0:
            return px, py, True

        while (abs(qx - px) > eps) or (abs(qy - py) > eps):
            mx = (px + qx) / 2.0
            my = (py + qy) / 2.0
            code_m = compute_code(mx, my, xmin, ymin, xmax, ymax)
            code_p = compute_code(px, py, xmin, ymin, xmax, ymax)

            if (code_m & code_p) != 0:
                px, py = mx, my
            else:
                qx, qy = mx, my

        if compute_code(px, py, xmin, ymin, xmax, ymax) == 0:
            return px, py, True
        if compute_code(qx, qy, xmin, ymin, xmax, ymax) == 0:
            return qx, qy, True
        return (px + qx) / 2.0, (py + qy) / 2.0, True
    vx1, vy1, ok1 = find_visible_point(x1, y1, x2, y2)
    vx2, vy2, ok2 = find_visible_point(x2, y2, x1, y1)
    if not ok1 or not ok2:
        return x1, y1, x2, y2, False
    if (xmin <= vx1 <= xmax and ymin <= vy1 <= ymax and
        xmin <= vx2 <= xmax and ymin <= vy2 <= ymax):
        return vx1, vy1, vx2, vy2, True
    return x1, y1, x2, y2, False

ALGORITHMS = {
    "Сазерленда-Коэна": sutherland_cohen,
    "Простой алгоритм": simple_clip,
    "Алгоритм средней точки": midpoint_clip,
}

def clip_segment(algorithm_name, x1, y1, x2, y2, xmin, ymin, xmax, ymax, eps=0.5):
    if algorithm_name == "Алгоритм средней точки":
        return midpoint_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax, eps)
    func = ALGORITHMS.get(algorithm_name, sutherland_cohen)
    return func(x1, y1, x2, y2, xmin, ymin, xmax, ymax)