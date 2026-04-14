import pya


class CrossoverVia(pya.PCellDeclarationHelper):

    def __init__(self):
        super(CrossoverVia, self).__init__()

        self.param("diff_w", self.TypeDouble, "DIFF width (um)", default=100.0)
        self.param("diff_h", self.TypeDouble, "DIFF height (um)", default=40.0)
        self.param("via_w", self.TypeDouble, "Via pad width (um)", default=25.0)
        self.param("via_inset", self.TypeDouble, "Via inset from DIFF edge (um)", default=3.0)
        self.param("metal_gap", self.TypeDouble, "Gap between via and bridge metal (um)", default=5.0)
        self.param("metal_overlap", self.TypeDouble, "Metal overlap beyond DIFF (um)", default=5.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_via", self.TypeLayer, "VIA layer", default=pya.LayerInfo(3, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "CrossoverVia({:.0f}x{:.0f})".format(self.diff_w, self.diff_h)

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        dw  = u(self.diff_w)
        dh  = u(self.diff_h)
        vw  = u(self.via_w)
        vi  = u(self.via_inset)
        mg  = u(self.metal_gap)
        mo  = u(self.metal_overlap)

        li_diff  = self.cell.layout().layer(self.l_diff)
        li_via   = self.cell.layout().layer(self.l_via)
        li_metal = self.cell.layout().layer(self.l_metal)

        def box(li, x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        box(li_diff, -dw/2, -dh/2, dw/2, dh/2)

        # left via + metal pad
        lv_x1 = -dw/2 + vi
        lv_x2 = lv_x1 + vw
        box(li_via, lv_x1, -dh/2 + vi, lv_x2, dh/2 - vi)
        box(li_metal, lv_x1, -dh/2 + vi, lv_x2, dh/2 - vi)

        # right via + metal pad
        rv_x2 = dw/2 - vi
        rv_x1 = rv_x2 - vw
        box(li_via, rv_x1, -dh/2 + vi, rv_x2, dh/2 - vi)
        box(li_metal, rv_x1, -dh/2 + vi, rv_x2, dh/2 - vi)

        # bridge metal in the middle (no via, isolated by gaps)
        bridge_x1 = lv_x2 + mg
        bridge_x2 = rv_x1 - mg
        box(li_metal, bridge_x1, -dh/2 + vi, bridge_x2, dh/2 - vi)
