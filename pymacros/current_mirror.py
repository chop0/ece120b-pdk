import pya


class CurrentMirror(pya.PCellDeclarationHelper):

    def __init__(self):
        super(CurrentMirror, self).__init__()

        self.param("gate_length", self.TypeDouble, "Gate length (um)", default=10.0)
        self.param("w_ref", self.TypeDouble, "Reference FET width (um)", default=50.0)
        self.param("w_mirror", self.TypeDouble, "Mirror FET width (um)", default=50.0)
        self.param("n_mirrors", self.TypeInt, "Number of mirror output channels", default=1)
        self.param("sd_ext", self.TypeDouble, "S/D extension (um)", default=20.0)
        self.param("via_width", self.TypeDouble, "Via width (um)", default=6.0)
        self.param("gate_spacing", self.TypeDouble, "Gap between FETs (um)", default=15.0)

        self.param("gen_pads", self.TypeBoolean, "Generate probe pads", default=True)
        self.param("pad_size", self.TypeDouble, "Pad size (um)", default=30.0)
        self.param("pad_gap", self.TypeDouble, "Pad gap (um)", default=10.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_gate", self.TypeLayer, "GATE layer", default=pya.LayerInfo(2, 0))
        self.param("l_via", self.TypeLayer, "VIA layer", default=pya.LayerInfo(3, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "CurrMirror(N={} W1={:.0f} W2={:.0f})".format(
            self.n_mirrors, self.w_ref, self.w_mirror)

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        gl  = u(self.gate_length)
        wr  = u(self.w_ref)
        wm  = u(self.w_mirror)
        sd  = u(self.sd_ext)
        vw  = u(self.via_width)
        gs  = u(self.gate_spacing)
        ps  = u(self.pad_size)
        pg  = u(self.pad_gap)
        n   = max(1, int(self.n_mirrors))

        l = {
            "diff":  self.cell.layout().layer(self.l_diff),
            "gate":  self.cell.layout().layer(self.l_gate),
            "via":   self.cell.layout().layer(self.l_via),
            "metal": self.cell.layout().layer(self.l_metal),
        }

        def box(layer, x1, y1, x2, y2):
            self.cell.shapes(l[layer]).insert(pya.Box(x1, y1, x2, y2))

        dw = 2 * sd + gl
        sv = vw / 2

        # source/drain x centers
        src_x = -dw/2 + sd/2
        drn_x = dw/2 - sd/2

        # y layout: N mirror FETs stacked from bottom, reference FET on top
        m_bots = [i * (wm + gs) for i in range(n)]
        m_tops = [b + wm for b in m_bots]
        m_mids = [(b + t) / 2 for b, t in zip(m_bots, m_tops)]

        r_bot = n * (wm + gs)
        r_top = r_bot + wr
        r_mid = (r_bot + r_top) / 2

        # DIFF regions for each mirror and the reference
        for b, t in zip(m_bots, m_tops):
            box("diff", -dw/2, b, dw/2, t)
        box("diff", -dw/2, r_bot, dw/2, r_top)

        # GATE: continuous strip through all FETs
        box("gate", -gl/2, m_bots[0], gl/2, r_top)

        # gate metal (no via - gate oxide must stay intact)
        box("metal", -gl/2, m_bots[0], gl/2, r_top)

        # per-mirror source + drain via/metal
        for b, t in zip(m_bots, m_tops):
            box("via",  src_x - sv, b, src_x + sv, t)
            box("metal", src_x - sv, b, src_x + sv, t)
            box("via",  drn_x - sv, b, drn_x + sv, t)
            box("metal", drn_x - sv, b, drn_x + sv, t)

        # ref source via+metal
        box("via",  src_x - sv, r_bot, src_x + sv, r_top)
        box("metal", src_x - sv, r_bot, src_x + sv, r_top)

        # ref drain via+metal
        box("via",  drn_x - sv, r_bot, drn_x + sv, r_top)
        box("metal", drn_x - sv, r_bot, drn_x + sv, r_top)

        # diode-connect: metal bridge ref drain to gate (at ref center)
        box("metal", -gl/2, r_mid - sv, drn_x + sv, r_mid + sv)

        if not self.gen_pads:
            return

        # ref source pad (left)
        box("metal", -dw/2 - pg - ps, r_mid - ps/2, -dw/2 - pg, r_mid + ps/2)
        box("metal", -dw/2 - pg, r_mid - sv, src_x - sv, r_mid + sv)

        # mirror source pads (left) and drain pads (right) - one per mirror
        for mid in m_mids:
            box("metal", -dw/2 - pg - ps, mid - ps/2, -dw/2 - pg, mid + ps/2)
            box("metal", -dw/2 - pg, mid - sv, src_x - sv, mid + sv)

            box("metal", dw/2 + pg, mid - ps/2, dw/2 + pg + ps, mid + ps/2)
            box("metal", drn_x + sv, mid - sv, dw/2 + pg, mid + sv)

        # gate pad (right, in gap between top-most mirror and reference)
        g_mid = (m_tops[-1] + r_bot) / 2
        box("metal", dw/2 + pg, g_mid - ps/2, dw/2 + pg + ps, g_mid + ps/2)
        box("metal", gl/2, g_mid - sv, dw/2 + pg, g_mid + sv)
