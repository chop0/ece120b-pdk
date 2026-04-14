import pya


class ProcessMonitor(pya.PCellDeclarationHelper):

    def __init__(self):
        super(ProcessMonitor, self).__init__()

        self.param("widths", self.TypeString, "Bar widths (um, comma-sep)", default="1.5,2,3,4,5,8,10,15,20")
        self.param("bar_length", self.TypeDouble, "Bar length (um)", default=200.0)
        self.param("gap", self.TypeDouble, "Gap between bars (um)", default=15.0)
        self.param("label_size", self.TypeDouble, "Label size (um)", default=6.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "ProcessMon"

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        widths = [float(w.strip()) for w in self.widths.split(",") if w.strip()]
        bl  = u(self.bar_length)
        gap = u(self.gap)
        lsz = u(self.label_size)

        li_diff  = self.cell.layout().layer(self.l_diff)
        li_metal = self.cell.layout().layer(self.l_metal)

        def box(li, x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        def label(li, x, y, text):
            t = pya.Text(text, pya.Trans(pya.Point(x, y)))
            t.size = lsz
            self.cell.shapes(li).insert(t)

        x = 0
        for w_um in widths:
            w = u(w_um)

            # doped bar
            box(li_diff, x, 0, x + w, bl)

            # metal bar on top (slightly wider for visibility)
            box(li_metal, x, 0, x + w, bl)

            # label centered below each bar
            txt = "{:.1f}u".format(w_um)
            txt_w = len(txt) * lsz * 0.6
            label(li_diff, x + w/2 - txt_w/2, -u(12), txt)

            x += w + gap
