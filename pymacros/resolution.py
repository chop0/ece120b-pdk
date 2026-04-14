import pya


class ResolutionChart(pya.PCellDeclarationHelper):

    def __init__(self):
        super(ResolutionChart, self).__init__()

        self.param("widths", self.TypeString, "Line widths (um, comma-sep)", default="10,8,6,5,4,3,2.5,2,1.5")
        self.param("num_lines", self.TypeInt, "Lines per group", default=5)
        self.param("line_length", self.TypeDouble, "Line length (um)", default=100.0)
        self.param("group_gap", self.TypeDouble, "Gap between groups (um)", default=30.0)
        self.param("label_size", self.TypeDouble, "Label size (um)", default=8.0)

        self.param("l_layer", self.TypeLayer, "Layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "ResChart"

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        widths = [float(w.strip()) for w in self.widths.split(",") if w.strip()]
        nl  = self.num_lines
        ll  = u(self.line_length)
        gg  = u(self.group_gap)
        lsz = u(self.label_size)

        li = self.cell.layout().layer(self.l_layer)

        def box(x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        def label(x, y, text):
            t = pya.Text(text, pya.Trans(pya.Point(x, y)))
            t.size = lsz
            self.cell.shapes(li).insert(t)

        y = 0
        for w_um in widths:
            w = u(w_um)
            pitch = w * 2  # equal line and space

            # horizontal group
            for i in range(nl):
                box(0, y + i * pitch, ll, y + i * pitch + w)

            # vertical group next to it
            vx = ll + gg
            for i in range(nl):
                box(vx + i * pitch, y, vx + i * pitch + w, y + ll)

            # label
            label(vx + nl * pitch + u(5), y + ll/2, "{:.1f}u".format(w_um))

            group_h = max(nl * pitch, ll)
            y += group_h + gg
