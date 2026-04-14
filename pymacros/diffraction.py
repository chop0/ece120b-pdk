import pya


class DiffractionGrating(pya.PCellDeclarationHelper):

    def __init__(self):
        super(DiffractionGrating, self).__init__()

        self.param("num_gratings", self.TypeInt, "Number of gratings", default=5)
        self.param("pitch_start", self.TypeDouble, "Starting pitch (um)", default=3.0)
        self.param("pitch_step", self.TypeDouble, "Pitch increment (um)", default=2.0)
        self.param("duty_cycle", self.TypeDouble, "Duty cycle (0-1)", default=0.5)
        self.param("grating_w", self.TypeDouble, "Grating width (um)", default=200.0)
        self.param("grating_h", self.TypeDouble, "Grating height (um)", default=100.0)
        self.param("gap", self.TypeDouble, "Gap between gratings (um)", default=30.0)
        self.param("label_size", self.TypeDouble, "Label size (um)", default=8.0)

        self.param("l_metal", self.TypeLayer, "Layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "DiffGrating(n={:d})".format(self.num_gratings)

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        n   = self.num_gratings
        gw  = u(self.grating_w)
        gh  = u(self.grating_h)
        gap = u(self.gap)
        lsz = u(self.label_size)

        li = self.cell.layout().layer(self.l_metal)

        def box(x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        def label(x, y, text):
            t = pya.Text(text, pya.Trans(pya.Point(x, y)))
            t.size = lsz
            self.cell.shapes(li).insert(t)

        for i in range(n):
            pitch = self.pitch_start + i * self.pitch_step
            p = u(pitch)
            lw = p * self.duty_cycle
            y0 = i * (gh + gap)

            x = 0
            while x < gw:
                box(x, y0, x + lw, y0 + gh)
                x += p

            label(gw + u(5), y0 + gh/2, "{:.1f}u".format(pitch))
