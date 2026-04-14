import pya


class VanDerPauw(pya.PCellDeclarationHelper):

    def __init__(self):
        super(VanDerPauw, self).__init__()

        self.param("size", self.TypeDouble, "Square size (um)", default=200.0)
        self.param("contact_size", self.TypeDouble, "Contact pad size (um)", default=30.0)
        self.param("contact_inset", self.TypeDouble, "Contact inset from corner (um)", default=5.0)
        self.param("pad_size", self.TypeDouble, "Probe pad size (um)", default=50.0)
        self.param("pad_gap", self.TypeDouble, "Pad gap from square (um)", default=10.0)
        self.param("trace_width", self.TypeDouble, "Metal trace width (um)", default=10.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_via", self.TypeLayer, "VIA layer", default=pya.LayerInfo(3, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "VdP({:.0f})".format(self.size)

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        sz  = u(self.size)
        cs  = u(self.contact_size)
        ci  = u(self.contact_inset)
        ps  = u(self.pad_size)
        pg  = u(self.pad_gap)
        tw  = u(self.trace_width)

        li_diff  = self.cell.layout().layer(self.l_diff)
        li_via   = self.cell.layout().layer(self.l_via)
        li_metal = self.cell.layout().layer(self.l_metal)

        def box(li, x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        hs = sz / 2

        # doped square
        box(li_diff, -hs, -hs, hs, hs)

        # contacts at 4 corners (inset from edge)
        corners = [
            (-hs + ci, -hs + ci),
            ( hs - ci - cs, -hs + ci),
            ( hs - ci - cs,  hs - ci - cs),
            (-hs + ci,  hs - ci - cs),
        ]

        # pad positions (outside the square)
        pad_pos = [
            (-hs - pg - ps, -hs),           # left-bottom
            ( hs + pg, -hs),                 # right-bottom
            ( hs + pg,  hs - ps),            # right-top
            (-hs - pg - ps,  hs - ps),       # left-top
        ]

        for i, (cx, cy) in enumerate(corners):
            box(li_via, cx, cy, cx + cs, cy + cs)
            box(li_metal, cx, cy, cx + cs, cy + cs)

            px, py = pad_pos[i]
            box(li_metal, px, py, px + ps, py + ps)

            # trace from contact to pad
            ccx = cx + cs/2
            ccy = cy + cs/2
            pcx = px + ps/2
            pcy = py + ps/2

            if i == 0 or i == 3:  # left side
                box(li_metal, px + ps, ccy - tw/2, ccx, ccy + tw/2)
            else:  # right side
                box(li_metal, ccx, ccy - tw/2, px, ccy + tw/2)
