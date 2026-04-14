import pya
import math


class KochSnowflake(pya.PCellDeclarationHelper):

    def __init__(self):
        super(KochSnowflake, self).__init__()

        self.param("size", self.TypeDouble, "Side length (um)", default=300.0)
        self.param("iterations", self.TypeInt, "Fractal iterations", default=4)
        self.param("line_width", self.TypeDouble, "Line width (um)", default=3.0)

        self.param("l_metal", self.TypeLayer, "Layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "Koch(n={:d})".format(self.iterations)

    def _koch_points(self, p1, p2, depth):
        if depth == 0:
            return [p1]

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        a = (p1[0] + dx/3, p1[1] + dy/3)
        b = (p1[0] + dx*2/3, p1[1] + dy*2/3)

        # peak of equilateral triangle on the middle segment
        mx = (a[0] + b[0])/2 - (b[1] - a[1]) * math.sqrt(3)/2
        my = (a[1] + b[1])/2 + (b[0] - a[0]) * math.sqrt(3)/2
        peak = (mx, my)

        pts = []
        pts += self._koch_points(p1, a, depth - 1)
        pts += self._koch_points(a, peak, depth - 1)
        pts += self._koch_points(peak, b, depth - 1)
        pts += self._koch_points(b, p2, depth - 1)
        return pts

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        sz = u(self.size)
        lw = u(self.line_width)
        n  = min(self.iterations, 6)

        li = self.cell.layout().layer(self.l_metal)

        # equilateral triangle vertices (centered)
        h = sz * math.sqrt(3) / 2
        v0 = (-sz/2, -h/3)
        v1 = (sz/2, -h/3)
        v2 = (0, 2*h/3)

        edges = [(v0, v1), (v1, v2), (v2, v0)]
        all_pts = []
        for p1, p2 in edges:
            all_pts += self._koch_points(p1, p2, n)

        # thicken the fractal outline into a polygon by offsetting inward/outward
        pts = all_pts
        num = len(pts)
        outer = []
        inner = []

        for i in range(num):
            p0 = pts[(i - 1) % num]
            p1 = pts[i]
            p2 = pts[(i + 1) % num]

            # average normal direction at this vertex
            dx1, dy1 = p1[0] - p0[0], p1[1] - p0[1]
            dx2, dy2 = p2[0] - p1[0], p2[1] - p1[1]
            l1 = math.sqrt(dx1*dx1 + dy1*dy1) or 1
            l2 = math.sqrt(dx2*dx2 + dy2*dy2) or 1

            nx = -(dy1/l1 + dy2/l2) / 2
            ny = (dx1/l1 + dx2/l2) / 2
            nl = math.sqrt(nx*nx + ny*ny) or 1
            nx /= nl
            ny /= nl

            outer.append(pya.Point(p1[0] + nx * lw/2, p1[1] + ny * lw/2))
            inner.append(pya.Point(p1[0] - nx * lw/2, p1[1] - ny * lw/2))

        inner.reverse()
        self.cell.shapes(li).insert(pya.Polygon(outer + inner))
