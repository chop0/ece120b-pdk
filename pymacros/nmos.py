import pya

SPACING = 1.5
LIB_NAME = "ECE120A_NMOS"


class NMOS(pya.PCellDeclarationHelper):

    def __init__(self):
        super(NMOS, self).__init__()

        self.param("w", self.TypeDouble, "Width", default=100.0)
        self.param("l", self.TypeDouble, "length", default=10.0)

    def display_text_impl(self):
        return "NMOS(Width={:.3f},Length={:.3f})".format(self.w, self.l)

    def coerce_parameters_impl(self):
        if self.w <= 5:
            self.w = 5
        if self.l <= 3:
            self.l = 3

    def produce_impl(self):
        ly = self.layout
        dbu = ly.dbu

        width_dbu   = int(self.w / dbu)
        length_dbu  = int(self.l / dbu)
        zone_dbu    = int(20.0 / dbu)
        spacing_dbu = int(SPACING / dbu)
        five_dbu    = int(5.0 / dbu)

        # Diffusion (source and drain islands)
        layer_diff = ly.layer(1, 0)
        self.cell.shapes(layer_diff).insert(
            pya.Box(0, 0, zone_dbu, width_dbu))
        self.cell.shapes(layer_diff).insert(
            pya.Box(zone_dbu + length_dbu, 0,
                    2 * zone_dbu + length_dbu, width_dbu))

        # Gate oxide
        layer_gate = ly.layer(2, 0)
        self.cell.shapes(layer_gate).insert(
            pya.Box(zone_dbu - spacing_dbu, -spacing_dbu,
                    zone_dbu + length_dbu + spacing_dbu,
                    width_dbu + spacing_dbu))

        # Gate metal
        layer_metal = ly.layer(4, 0)
        self.cell.shapes(layer_metal).insert(
            pya.Box(zone_dbu - 2 * spacing_dbu, -2 * spacing_dbu,
                    zone_dbu + length_dbu + 2 * spacing_dbu,
                    width_dbu + 2 * spacing_dbu))

        # Source/drain vias
        via_params = {
            "w": 5.0,
            "l": self.w - (2 * SPACING),
        }
        via_cell = ly.create_cell("Via", LIB_NAME, via_params)

        t1 = pya.Trans(pya.Point(five_dbu - spacing_dbu, 0))
        t2 = pya.Trans(pya.Point(
            2 * five_dbu + zone_dbu + length_dbu - spacing_dbu, 0))

        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t1))
        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t2))
