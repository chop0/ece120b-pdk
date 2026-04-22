import pya

SPACING = 1.5


class Via(pya.PCellDeclarationHelper):

    def __init__(self):
        super(Via, self).__init__()

        self.param("w", self.TypeDouble, "Width", default=5)
        self.param("l", self.TypeDouble, "Length", default=5)

    def display_text_impl(self):
        return "Via(Width={:.3f},Length={:.3f})".format(self.w, self.l)

    def coerce_parameters_impl(self):
        if self.w <= 1.5:
            self.w = 1.5
        if self.l <= 1.5:
            self.l = 1.5

    def produce_impl(self):
        ly = self.layout

        layer_diff = ly.layer(1, 0)
        layer_via  = ly.layer(3, 0)
        layer_metal = ly.layer(4, 0)

        dbu = ly.dbu

        width_dbu = int(self.w / dbu)
        length_dbu = int(self.l / dbu)
        width_dm_dbu = int((self.w + 2 * SPACING) / dbu)
        length_dm_dbu = int((self.l + 2 * SPACING) / dbu)
        dx = int(SPACING / dbu)

        via_box = pya.Box(dx, dx, width_dbu + dx, length_dbu + dx)
        dm_box  = pya.Box(0, 0, width_dm_dbu, length_dm_dbu)

        self.cell.shapes(layer_diff).insert(dm_box)
        self.cell.shapes(layer_via).insert(via_box)
        self.cell.shapes(layer_metal).insert(dm_box)
