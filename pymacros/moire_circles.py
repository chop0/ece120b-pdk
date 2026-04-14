import pya
import math


class AlignMoireLinear(pya.PCellDeclarationHelper):

    def __init__(self):
        super(AlignMoireLinear, self).__init__()

        self.param("radius", self.TypeDouble, "Pattern radius (um)", default=200.0)
        self.param("pitch", self.TypeDouble, "Ring pitch (um)", default=8.0)
        self.param("line_width", self.TypeDouble, "Ring width (um)", default=4.0)
        self.param("num_points", self.TypeInt, "Points per circle", default=128)

        self.param("l_ref", self.TypeLayer, "Reference layer", default=pya.LayerInfo(1, 0))
        self.param("l_align", self.TypeLayer, "Aligned layer", default=pya.LayerInfo(2, 0))

    def display_text_impl(self):
        return "AlignMoireLinear(r={:.0f} p={:.0f})".format(self.radius, self.pitch)

    def _ring(self, li, r_inner, r_outer, n):
        pts_outer = []
        pts_inner = []
        for i in range(n):
            a = 2 * math.pi * i / n
            c = math.cos(a)
            s = math.sin(a)
            pts_outer.append(pya.Point(r_outer * c, r_outer * s))
            pts_inner.append(pya.Point(r_inner * c, r_inner * s))
        pts_inner.reverse()
        self.cell.shapes(li).insert(pya.Polygon(pts_outer + pts_inner))

    def _disk(self, li, r, n):
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            pts.append(pya.Point(r * math.cos(a), r * math.sin(a)))
        self.cell.shapes(li).insert(pya.Polygon(pts))

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        rad = u(self.radius)
        p   = u(self.pitch)
        lw  = u(self.line_width)
        n   = self.num_points

        li_ref   = self.cell.layout().layer(self.l_ref)
        li_align = self.cell.layout().layer(self.l_align)

        r = p
        while r < rad:
            r_inner = r - lw / 2
            r_outer = r + lw / 2
            self._ring(li_ref, r_inner, r_outer, n)
            self._ring(li_align, r_inner, r_outer, n)
            r += p

        # center dot
        if lw / 2 > 0:
            self._disk(li_ref, lw / 2, n)
            self._disk(li_align, lw / 2, n)
