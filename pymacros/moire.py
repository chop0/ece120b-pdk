import pya


class AlignMoireRotation(pya.PCellDeclarationHelper):

    def __init__(self):
        super(AlignMoireRotation, self).__init__()

        self.param("width", self.TypeDouble, "Grating width (um)", default=500.0)
        self.param("height", self.TypeDouble, "Grating height (um)", default=500.0)
        self.param("pitch", self.TypeDouble, "Line pitch (um)", default=8.0)
        self.param("line_width", self.TypeDouble, "Line width (um)", default=4.0)
        self.param("border", self.TypeDouble, "Border frame width (um)", default=5.0)
        self.param("breaks", self.TypeBoolean, "Add vertical breaks", default=False)
        self.param("break_pitch", self.TypeDouble, "Break pitch (um)", default=50.0)
        self.param("break_width", self.TypeDouble, "Break width (um)", default=4.0)

        self.param("l_ref", self.TypeLayer, "Reference layer", default=pya.LayerInfo(1, 0))
        self.param("l_align", self.TypeLayer, "Aligned layer", default=pya.LayerInfo(2, 0))

    def display_text_impl(self):
        return "AlignMoireRotation(p={:.0f})".format(self.pitch)

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        w   = u(self.width)
        h   = u(self.height)
        p   = u(self.pitch)
        lw  = u(self.line_width)
        bdr = u(self.border)
        do_breaks = self.breaks
        bp  = u(self.break_pitch)
        bw  = u(self.break_width)

        li_ref   = self.cell.layout().layer(self.l_ref)
        li_align = self.cell.layout().layer(self.l_align)

        def box(li, x1, y1, x2, y2):
            self.cell.shapes(li).insert(pya.Box(x1, y1, x2, y2))

        box(li_ref, -w/2 - bdr, -h/2 - bdr, w/2 + bdr, -h/2)
        box(li_ref, -w/2 - bdr, h/2, w/2 + bdr, h/2 + bdr)
        box(li_ref, -w/2 - bdr, -h/2, -w/2, h/2)
        box(li_ref, w/2, -h/2, w/2 + bdr, h/2)

        if not do_breaks:
            x = -w/2
            while x < w/2:
                box(li_ref, x, -h/2, x + lw, h/2)
                box(li_align, x, -h/2, x + lw, h/2)
                x += p
        else:
            x = -w/2
            while x < w/2:
                y = -h/2
                while y < h/2:
                    seg_top = min(y + bp - bw, h/2)
                    if seg_top > y:
                        box(li_ref, x, y, x + lw, seg_top)
                        box(li_align, x, y, x + lw, seg_top)
                    y += bp
                x += p
