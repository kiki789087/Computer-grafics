import math
def bezier_point(points, t):
    pts = [list(p) for p in points]
    n = len(pts)
    while n > 1:
        new_pts = []
        for i in range(n - 1):
            x = (1 - t) * pts[i][0] + t * pts[i + 1][0]
            y = (1 - t) * pts[i][1] + t * pts[i + 1][1]
            new_pts.append([x, y])
        pts = new_pts
        n -= 1
    return tuple(pts[0])

def bezier_curve(points, steps=50):

    if len(points) < 2:
        return list(points)
    return [bezier_point(points, i / steps) for i in range(steps + 1)]

def bezier_levels(points, t):
    levels = [[tuple(p) for p in points]]
    cur = [tuple(p) for p in points]
    while len(cur) > 1:
        nxt = []
        for i in range(len(cur) - 1):
            x = (1 - t) * cur[i][0] + t * cur[i + 1][0]
            y = (1 - t) * cur[i][1] + t * cur[i + 1][1]
            nxt.append((x, y))
        levels.append(nxt)
        cur = nxt
    return levels

def chaikin_once(points):
    if len(points) < 2:
        return list(points)
    new_pts = [points[0]]
    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]
        qx = 0.75 * p0[0] + 0.25 * p1[0]
        qy = 0.75 * p0[1] + 0.25 * p1[1]
        rx = 0.25 * p0[0] + 0.75 * p1[0]
        ry = 0.25 * p0[1] + 0.75 * p1[1]
        new_pts.append((qx, qy))
        new_pts.append((rx, ry))
    new_pts.append(points[-1])
    return new_pts


def chaikin_curve(points, iterations=4):
    result = [list(points)]
    cur = list(points)
    for _ in range(iterations):
        cur = chaikin_once(cur)
        result.append(cur)
    return result

def _midpoint(p, q):
    return ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)

def _face_center(quad):
    n = len(quad)
    cx = sum(p[0] for p in quad) / n
    cy = sum(p[1] for p in quad) / n
    return (cx, cy)


def doo_sabin_face_point(quad):
    if len(quad) == 4:
        p0, p1, p2, p3 = quad
        m01 = _midpoint(p0, p1)
        m12 = _midpoint(p1, p2)
        m23 = _midpoint(p2, p3)
        m30 = _midpoint(p3, p0)
        x = (p0[0] + p1[0] + p2[0] + p3[0]
             + m01[0] + m12[0] + m23[0] + m30[0]) / 8.0
        y = (p0[1] + p1[1] + p2[1] + p3[1]
             + m01[1] + m12[1] + m23[1] + m30[1]) / 8.0
        return (x, y)
    return _face_center(quad)

def doo_sabin_iteration(grid):
    faces = grid["faces"]
    points = grid["vertices"]
    edges = {}
    for f in faces:
        for k in range(len(f)):
            a, b = f[k], f[(k + 1) % len(f)]
            key = tuple(sorted((a, b)))
            edges.setdefault(key, []).append(f)
    face_centers = {}
    for fi, f in enumerate(faces):
        coords = [points[i] for i in f]
        face_centers[fi] = _face_center(coords)

    edge_points = {}
    for (a, b) in edges:
        edge_points[(a, b)] = _midpoint(points[a], points[b])

    vertex_faces = {i: [] for i in range(len(points))}
    for fi, f in enumerate(faces):
        for vi in f:
            vertex_faces[vi].append(fi)

    vertex_points = {}
    for vi, fs in vertex_faces.items():
        if not fs:
            vertex_points[vi] = points[vi]
            continue
        x = points[vi][0]
        y = points[vi][1]
        for fi in fs:
            x += face_centers[fi][0]
            y += face_centers[fi][1]
        x /= (len(fs) + 1)
        y /= (len(fs) + 1)
        vertex_points[vi] = (x, y)

    new_faces = []
    for fi, f in enumerate(faces):
        n = len(f)
        for k in range(n):
            a = f[k]
            b = f[(k + 1) % n]
            key = tuple(sorted((a, b)))
            new_face = [
                vertex_points[a],
                edge_points[key],
                face_centers[fi],
                edge_points[tuple(sorted((b, f[(k + 2) % n])))],
            ]
            new_faces.append(new_face)

    all_new = list(vertex_points.values()) + list(edge_points.values()) + list(face_centers.values())

    return {
        "faces": new_faces,
        "new_points": all_new,
        "vertex_points": list(vertex_points.values()),
        "edge_points": list(edge_points.values()),
        "face_points": list(face_centers.values()),
    }


def doo_sabin(start_grid, iterations=2):
    states = [{
        "faces": [[start_grid["vertices"][i] for i in f]
                  for f in start_grid["faces"]],
        "vertices": [tuple(p) for p in start_grid["vertices"]],
        "new_points": [],
    }]

    cur_faces = start_grid["faces"]
    cur_points = start_grid["vertices"]

    for _ in range(iterations):
        step = doo_sabin_iteration({"faces": cur_faces, "vertices": cur_points})
        unique = []
        idx_map = {}

        def get_idx(p):
            key = (round(p[0], 6), round(p[1], 6))
            if key not in idx_map:
                idx_map[key] = len(unique)
                unique.append(p)
            return idx_map[key]

        new_faces_idx = []
        for f in step["faces"]:
            new_faces_idx.append([get_idx(p) for p in f])

        cur_faces = new_faces_idx
        cur_points = unique

        states.append({
            "faces": [[cur_points[i] for i in f] for f in cur_faces],
            "vertices": [tuple(p) for p in cur_points],
            "new_points": step["new_points"],
        })

    return states

def make_grid(rows, cols, x0=0.0, y0=0.0, dx=1.0, dy=1.0):
    vertices = []
    for r in range(rows):
        for c in range(cols):
            vertices.append((x0 + c * dx, y0 + r * dy))
    faces = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            i = r * cols + c
            faces.append([i, i + 1, i + 1 + cols, i + cols])
    return {"vertices": vertices, "faces": faces}