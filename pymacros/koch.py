import pya
import math


class KochSnowflake(pya.PCellDeclarationHelper):

    def __init__(self):
        super(KochSnowflake, self).__init__()

        self.param("size", self.TypeDouble, "Side length (um)", default=300.0)
        self.param("iterations", self.TypeInt, "Fractal iterations", default=4)
        self.param("line_width", self.TypeDouble, "Ring width (um, 0=filled)", default=3.0)
        self.param("filled", self.TypeBoolean, "Fill solid (ignore ring width)", default=False)

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

        # peak of equilateral triangle on the middle segment, pointing
        # outward for a CCW-wound base triangle
        mx = (a[0] + b[0])/2 + (b[1] - a[1]) * math.sqrt(3)/2
        my = (a[1] + b[1])/2 - (b[0] - a[0]) * math.sqrt(3)/2
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

        # equilateral triangle vertices, CCW, centered on centroid
        h = sz * math.sqrt(3) / 2
        v0 = (-sz/2, -h/3)
        v1 = (sz/2, -h/3)
        v2 = (0, 2*h/3)

        edges = [(v0, v1), (v1, v2), (v2, v0)]
        all_pts = []
        for p1, p2 in edges:
            all_pts += self._koch_points(p1, p2, n)

        poly_pts = [pya.Point(int(round(x)), int(round(y))) for x, y in all_pts]
        outer_poly = pya.Polygon(poly_pts)

        if self.filled or lw <= 0:
            self.cell.shapes(li).insert(outer_poly)
        else:
            region = pya.Region(outer_poly)
            inner = region.sized(-int(round(lw)))
            self.cell.shapes(li).insert(region - inner)
