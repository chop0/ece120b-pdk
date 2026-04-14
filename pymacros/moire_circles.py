import pya
import math


class AlignMoireLinear(pya.PCellDeclarationHelper):

    def __init__(self):
        super(AlignMoireLinear, self).__init__()

        self.param("radius", self.TypeDouble, "Pattern radius (um)", default=200.0)
        self.param("pitch", self.TypeDouble, "Ring pitch (um)", default=8.0)
        self.param("line_width", self.TypeDouble, "Ring width (um)", default=4.0)
        self.param("num_points", self.TypeInt, "Points per circle", default=128)
        self.param("label_size", self.TypeDouble, "Label text size (um)", default=10.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_gate", self.TypeLayer, "GATE layer", default=pya.LayerInfo(2, 0))
        self.param("l_via", self.TypeLayer, "VIA layer", default=pya.LayerInfo(3, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "AlignMoireLinear(r={:.0f} p={:.0f})".format(self.radius, self.pitch)

    def _ring(self, li, r_inner, r_outer, n, a_start, a_end):
        pts_outer = []
        pts_inner = []
        steps = max(int(n * (a_end - a_start) / (2 * math.pi)), 8)
        for i in range(steps + 1):
            a = a_start + (a_end - a_start) * i / steps
            c = math.cos(a)
            s = math.sin(a)
            pts_outer.append(pya.Point(r_outer * c, r_outer * s))
            pts_inner.append(pya.Point(r_inner * c, r_inner * s))
        pts_inner.reverse()
        self.cell.shapes(li).insert(pya.Polygon(pts_outer + pts_inner))

    def _disk_slice(self, li, r, n, a_start, a_end):
        pts = [pya.Point(0, 0)]
        steps = max(int(n * (a_end - a_start) / (2 * math.pi)), 8)
        for i in range(steps + 1):
            a = a_start + (a_end - a_start) * i / steps
            pts.append(pya.Point(r * math.cos(a), r * math.sin(a)))
        self.cell.shapes(li).insert(pya.Polygon(pts))

    def _label(self, li, x, y, text, size):
        t = pya.Text(text, pya.Trans(pya.Point(x, y)))
        t.size = size
        self.cell.shapes(li).insert(t)

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        rad  = u(self.radius)
        p    = u(self.pitch)
        lw   = u(self.line_width)
        n    = self.num_points
        lsz  = u(self.label_size)

        layers = [
            self.cell.layout().layer(self.l_diff),
            self.cell.layout().layer(self.l_gate),
            self.cell.layout().layer(self.l_via),
            self.cell.layout().layer(self.l_metal),
        ]
        names = ["1", "2", "3", "4"]

        # 4 quadrants: 3 adjacent pairs + 1 with all layers
        quads = [
            (0, 1),
            (1, 2),
            (2, 3),
            None,  # all 4
        ]
        gap = math.radians(2)
        quad_angle = math.pi / 2

        for qi, pair in enumerate(quads):
            a_start = qi * quad_angle + gap / 2
            a_end = (qi + 1) * quad_angle - gap / 2

            if pair is not None:
                la, lb = pair
                layer_set = [(la, lb)]
            else:
                layer_set = [(i, i) for i in range(4)]

            for la, lb in layer_set:
                r = p
                while r < rad:
                    r_inner = r - lw / 2
                    r_outer = r + lw / 2
                    if r_inner < 0:
                        r_inner = 0
                    self._ring(layers[la], r_inner, r_outer, n, a_start, a_end)
                    if lb != la:
                        self._ring(layers[lb], r_inner, r_outer, n, a_start, a_end)
                    r += p

                if lw / 2 > 0:
                    self._disk_slice(layers[la], lw / 2, n, a_start, a_end)
                    if lb != la:
                        self._disk_slice(layers[lb], lw / 2, n, a_start, a_end)

            # label at mid-angle, well outside the pattern
            mid_a = (a_start + a_end) / 2
            lx = (rad + u(40)) * math.cos(mid_a)
            ly = (rad + u(40)) * math.sin(mid_a)

            if pair is not None:
                la, lb = pair
                txt = "{} + {}".format(names[la], names[lb])
                self._label(layers[la], lx, ly, txt, lsz)
            else:
                self._label(layers[0], lx, ly, "ALL", lsz)
