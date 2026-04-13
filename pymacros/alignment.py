import pya


class AlignmentMark(pya.PCellDeclarationHelper):

    def __init__(self):
        super(AlignmentMark, self).__init__()

        self.param("arm_length", self.TypeDouble, "Cross arm length (um)", default=40.0)
        self.param("arm_width", self.TypeDouble, "Cross arm width (um)", default=15.0)
        self.param("tip_pad", self.TypeDouble, "Extra pad at arm tips (um)", default=8.0)
        self.param("clearance", self.TypeDouble, "Gap between inner and outline (um)", default=3.0)
        self.param("outline_wall", self.TypeDouble, "Outline wall thickness (um)", default=5.0)
        self.param("spacing", self.TypeDouble, "Spacing between marks (um)", default=180.0)

        self.param("l_diff", self.TypeLayer, "DIFF layer", default=pya.LayerInfo(1, 0))
        self.param("l_gate", self.TypeLayer, "GATE layer", default=pya.LayerInfo(2, 0))
        self.param("l_via", self.TypeLayer, "VIA layer", default=pya.LayerInfo(3, 0))
        self.param("l_metal", self.TypeLayer, "METAL layer", default=pya.LayerInfo(4, 0))

    def display_text_impl(self):
        return "AlignMark"

    def _cross_region(self, cx, cy, arm, width, tip):
        hw = width / 2
        hp = (width + 2 * tip) / 2

        r = pya.Region()
        r.insert(pya.Box(cx - arm, cy - hw, cx + arm, cy + hw))
        r.insert(pya.Box(cx - hw, cy - arm, cx + hw, cy + arm))

        for dx, dy in [(arm, 0), (-arm, 0), (0, arm), (0, -arm)]:
            r.insert(pya.Box(cx + dx - hp, cy + dy - hp, cx + dx + hp, cy + dy + hp))

        r.merge()
        return r

    def produce_impl(self):
        dbu = self.layout.dbu
        def u(val): return val / dbu

        arm  = u(self.arm_length)
        aw   = u(self.arm_width)
        tip  = u(self.tip_pad)
        clr  = u(self.clearance)
        wall = u(self.outline_wall)
        sp   = u(self.spacing)

        layers = [
            self.cell.layout().layer(self.l_diff),
            self.cell.layout().layer(self.l_gate),
            self.cell.layout().layer(self.l_via),
            self.cell.layout().layer(self.l_metal),
        ]

        def insert_region(li, region):
            for p in region.each():
                self.cell.shapes(li).insert(p)

        marks = [
            (2, 0, 0, 1),
            (1, 0, 0, 2),
            (0, 0, 0, 3),
            (1, 1, 1, 2),
            (0, 1, 1, 3),
            (0, 2, 2, 3),
        ]

        for col, row, inner_idx, outer_idx in marks:
            cx = col * sp
            cy = -row * sp

            solid = self._cross_region(cx, cy, arm, aw, tip)
            insert_region(layers[inner_idx], solid)

            outer_cross = self._cross_region(cx, cy, arm + clr + wall, aw + 2*(clr + wall), tip + wall)
            gap_cross = self._cross_region(cx, cy, arm + clr, aw + 2*clr, tip + clr)
            frame = outer_cross - gap_cross
            insert_region(layers[outer_idx], frame)
