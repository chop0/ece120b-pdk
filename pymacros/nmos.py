import pya


class NMOS(pya.PCellDeclarationHelper):

    def __init__(self):
        super(NMOS, self).__init__()

        self.param("gate_length", self.TypeDouble, "Gate length (um)", default=10.0)
        self.param("gate_width", self.TypeDouble, "Gate width (um)", default=50.0)
        self.param("sd_extension", self.TypeDouble, "S/D extension beyond gate (um)", default=20.0)

        self.param("via_width", self.TypeDouble, "Via strip width (um)", default=6.0)

        self.param("gen_pads", self.TypeBoolean, "Generate probe pads", default=True)
        self.param("pad_size", self.TypeDouble, "Pad size (um)", default=30.0)
        self.param("pad_gap", self.TypeDouble, "Pad gap from DIFF edge (um)", default=3.0)
        self.param("taper_length", self.TypeDouble, "Taper length (um)", default=10.0)
        self.param("taper_width", self.TypeDouble, "Taper width at pad end (um)", default=16.0)

        self.param("body_via_size", self.TypeDouble, "Body via size (um)", default=10.0)
        self.param("body_spacing", self.TypeDouble, "Body spacing from drain pad (um)", default=5.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_gate", self.TypeLayer, "GATE layer", default=pya.LayerInfo(2, 0))
        self.param("l_via", self.TypeLayer, "VIA layer", default=pya.LayerInfo(3, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "NMOS(L={:.0f} W={:.0f})".format(self.gate_length, self.gate_width)

    def coerce_parameters_impl(self):
        if self.gate_length < 2: self.gate_length = 2
        if self.gate_width < 10: self.gate_width = 10

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        gl  = u(self.gate_length)
        gw  = u(self.gate_width)
        sd  = u(self.sd_extension)
        vw  = u(self.via_width)
        ps  = u(self.pad_size)
        pg  = u(self.pad_gap)
        tl  = u(self.taper_length)
        tw  = u(self.taper_width)
        bvs = u(self.body_via_size)
        bsp = u(self.body_spacing)

        l = {
            "diff":  self.cell.layout().layer(self.l_diff),
            "gate":  self.cell.layout().layer(self.l_gate),
            "via":   self.cell.layout().layer(self.l_via),
            "metal": self.cell.layout().layer(self.l_metal),
        }
        def box(layer, x1, y1, x2, y2):
            self.cell.shapes(l[layer]).insert(pya.Box(x1, y1, x2, y2))
        def poly(layer, pts):
            self.cell.shapes(l[layer]).insert(pya.Polygon([pya.Point(x, y) for x, y in pts]))

        dw = 2 * sd + gl
        dx1, dx2 = -dw/2, dw/2
        dy1, dy2 = -gw/2, gw/2
        gx1, gx2 = -gl/2, gl/2

        src_cx = (dx1 + gx1) / 2
        drn_cx = (gx2 + dx2) / 2
        sv = vw / 2
        hw = tw / 2

        box("diff", dx1, dy1, dx2, dy2)
        box("gate", gx1, dy1, gx2, dy2)

        # via + metal on source, drain, gate
        box("via", src_cx - sv, dy1, src_cx + sv, dy2)
        box("via", drn_cx - sv, dy1, drn_cx + sv, dy2)
        box("metal", src_cx - sv, dy1, src_cx + sv, dy2)
        box("metal", drn_cx - sv, dy1, drn_cx + sv, dy2)
        box("metal", gx1, dy1, gx2, dy2)

        if not self.gen_pads:
            return

        # body via
        dpx1 = dx2 + pg
        bx1 = dpx1 + (ps - bvs) / 2
        by1 = ps/2 + bsp
        box("via", bx1, by1, bx1 + bvs, by1 + bvs)

        # source pad + taper + trace
        spx2 = dx1 - pg
        box("metal", spx2 - ps, -ps/2, spx2, ps/2)
        poly("metal", [(spx2, -hw), (spx2, hw), (spx2 + tl, sv), (spx2 + tl, -sv)])
        box("metal", spx2 + tl, dy1, src_cx + sv, dy2)

        # drain pad + taper + trace
        box("metal", dpx1, -ps/2, dpx1 + ps, ps/2)
        poly("metal", [(dpx1, -hw), (dpx1, hw), (dpx1 - tl, sv), (dpx1 - tl, -sv)])
        box("metal", drn_cx - sv, dy1, dpx1 - tl, dy2)

        # gate pad + taper + trace
        gpy1 = dy2 + pg
        box("metal", -ps/2, gpy1, ps/2, gpy1 + ps)
        poly("metal", [(-hw, gpy1), (hw, gpy1), (gx2, gpy1 - tl), (gx1, gpy1 - tl)])
        box("metal", gx1, dy1, gx2, gpy1 - tl)

        # body pad
        mo = u(3)
        box("metal", bx1 - mo, by1 - mo, bx1 + bvs + mo, by1 + bvs + mo)
