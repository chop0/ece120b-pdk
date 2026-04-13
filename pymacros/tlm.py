import pya


class TLM(pya.PCellDeclarationHelper):

    def __init__(self):
        super(TLM, self).__init__()

        self.param("num_pads", self.TypeInt, "Number of pads", default=10)
        self.param("pad_w", self.TypeDouble, "Pad width (um)", default=80.0)
        self.param("pad_h", self.TypeDouble, "Pad height (um)", default=100.0)
        self.param("strip_h", self.TypeDouble, "DIFF strip height (um)", default=60.0)
        self.param("gap_start", self.TypeDouble, "Smallest gap (um)", default=10.0)
        self.param("gap_step", self.TypeDouble, "Gap increment (um)", default=10.0)
        self.param("via_inset", self.TypeDouble, "Via inset from pad edge (um)", default=5.0)
        self.param("metal_overlap", self.TypeDouble, "Metal overlap beyond via (um)", default=3.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_via", self.TypeLayer, "VIA layer", default=pya.LayerInfo(3, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "TLM(n={:d} g0={:.0f})".format(self.num_pads, self.gap_start)

    def coerce_parameters_impl(self):
        if self.num_pads < 2: self.num_pads = 2
        if self.gap_start < 1: self.gap_start = 1

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        n   = self.num_pads
        pw  = u(self.pad_w)
        ph  = u(self.pad_h)
        sh  = u(self.strip_h)
        g0  = u(self.gap_start)
        gs  = u(self.gap_step)
        vi  = u(self.via_inset)
        mo  = u(self.metal_overlap)

        li_diff  = self.cell.layout().layer(self.l_diff)
        li_via   = self.cell.layout().layer(self.l_via)
        li_metal = self.cell.layout().layer(self.l_metal)

        def box(li, x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        def label(li, x, y, text, size=None):
            if size is None: size = u(8)
            t = pya.Text(text, pya.Trans(pya.Point(x, y)))
            t.size = size
            self.cell.shapes(li).insert(t)

        x = 0
        pads = []
        gaps = []
        for i in range(n):
            gap = g0 + gs * i
            if i > 0:
                gaps.append(gap)
                x += gap
            pads.append(x)
            x += pw

        total_w = x
        sy1, sy2 = -sh/2, sh/2

        box(li_diff, 0, sy1, total_w, sy2)

        for i, px in enumerate(pads):
            box(li_via, px + vi, sy1, px + pw - vi, sy2)
            box(li_metal, px + vi - mo, -ph/2, px + pw - vi + mo, ph/2)

        for i, gap in enumerate(gaps):
            gap_x = pads[i] + pw + gap / 2
            gap_um = (self.gap_start + self.gap_step * (i + 1))
            label(li_diff, gap_x, sy2 + u(5), "{:.0f}u".format(gap_um))
            label(li_diff, gap_x, sy1 - u(12), "{:.0f}u".format(gap_um))

        label(li_diff, total_w + u(5), sy2, "TLM", u(12))
        label(li_diff, total_w + u(5), 0, "x{:.0f}u".format(self.strip_h), u(8))
