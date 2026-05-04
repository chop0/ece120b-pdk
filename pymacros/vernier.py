import pya


class Vernier(pya.PCellDeclarationHelper):

    def __init__(self):
        super(Vernier, self).__init__()

        self.param("num_ticks", self.TypeInt, "Ticks per side", default=10)
        self.param("pitch", self.TypeDouble, "Tick pitch (um)", default=10.0)
        self.param("tick_length", self.TypeDouble, "Tick length (um)", default=20.0)
        self.param("tick_width", self.TypeDouble, "Tick width (um)", default=2.0)
        self.param("gap", self.TypeDouble, "Gap between tick rows (um)", default=4.0)
        self.param("label_size", self.TypeDouble, "Label text size (um)", default=6.0)

        self.param("l_ref", self.TypeLayer, "Reference layer", default=pya.LayerInfo(1, 0))
        self.param("l_align", self.TypeLayer, "Aligned layer", default=pya.LayerInfo(2, 0))

    def display_text_impl(self):
        return "Vernier({}/{}->{}/{})".format(
            self.l_ref.layer, self.l_ref.datatype,
            self.l_align.layer, self.l_align.datatype)

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        n   = self.num_ticks
        p   = u(self.pitch)
        tl  = u(self.tick_length)
        tw  = u(self.tick_width)
        gap = u(self.gap)
        lsz = u(self.label_size)

        li_ref   = self.cell.layout().layer(self.l_ref)
        li_align = self.cell.layout().layer(self.l_align)

        def box(li, x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        def label(li, x, y, text):
            t = pya.Text(text, pya.Trans(pya.Point(x, y)))
            t.size = lsz
            self.cell.shapes(li).insert(t)

        for i in range(-n, n + 1):
            x = i * p
            major = (i % 5 == 0)
            h = tl if major else tl * 0.6

            seg_h = h / 3
            for k in range(3):
                half_w = round(tw * (k + 1) / 6)
                y_lo_top = gap/2 + k * seg_h
                box(li_ref, x - half_w, y_lo_top, x + half_w, y_lo_top + seg_h)

                y_hi_bot = -gap/2 - k * seg_h
                box(li_align, x - half_w, y_hi_bot - seg_h, x + half_w, y_hi_bot)

            if major:
                um_val = abs(i) * self.pitch
                txt = "{:.0f}u".format(um_val) if um_val == int(um_val) else "{:.1f}u".format(um_val)
                label(li_ref, x, gap/2 + h + u(2), txt)
                label(li_align, x, -gap/2 - h - lsz - u(2), txt)

        # title text to the right
        total_w = n * p
        label(li_ref, total_w + u(10), gap/2 + tl/2, "Min. tick {:.1f}u".format(self.pitch))
