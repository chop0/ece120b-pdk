import pya

SPACING = 1.5
LIB_NAME = "ECE120A_NMOS"


class Resistor(pya.PCellDeclarationHelper):

    def __init__(self):
        super(Resistor, self).__init__()

        self.param("w", self.TypeDouble, "Width", default=10.0)
        self.param("r", self.TypeDouble, "Resistance", default=1000.0)
        self.param("rs", self.TypeDouble, "Sheet Resistance", default=15.0)
        self.param("l", self.TypeDouble, "length", readonly=True)

    def display_text_impl(self):
        return "Resistor(Width={:.3f},Res={:.3f})".format(self.w, self.r)

    def coerce_parameters_impl(self):
        if self.w <= 4.5:
            self.w = 4.5
        if self.rs <= 0:
            self.rs = 0.001
        if self.r <= 0:
            self.r = 0.001
        self.l = self.r * self.w / self.rs

    def produce_impl(self):
        ly = self.layout
        layer_index = ly.layer(1, 0)

        dbu = ly.dbu
        width_dbu = int(self.w / dbu)
        length_dbu = int(self.l / dbu)

        diffusion = pya.Box(0, 0, width_dbu, length_dbu)
        self.cell.shapes(layer_index).insert(diffusion)

        via_params = {
            "w": self.w - (2 * SPACING),
            "l": self.w - (2 * SPACING),
        }
        via_cell = ly.create_cell("Via", LIB_NAME, via_params)

        t1 = pya.Trans(pya.Point(0, -width_dbu))
        t2 = pya.Trans(pya.Point(0, length_dbu))

        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t1))
        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t2))
