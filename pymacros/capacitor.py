import pya
import math

SPACING = 1.5
LIB_NAME = "ECE120A_NMOS"


class Capacitor(pya.PCellDeclarationHelper):

    def __init__(self):
        super(Capacitor, self).__init__()

        self.param("c", self.TypeDouble, "Capacitance", default=100.0)
        self.param("w", self.TypeInt, "Width", readonly=True)

    def display_text_impl(self):
        return "Capacitor(C={:.3f},Width={:.3f})".format(self.c, self.w)

    def coerce_parameters_impl(self):
        if self.c <= 1:
            self.c = 1
        self.w = math.sqrt(self.c / (6.85e-4))

    def produce_impl(self):
        ly = self.layout
        dbu = ly.dbu

        width_dbu   = int(self.w / dbu)
        spacing_dbu = int(SPACING / dbu)
        five_dbu    = int(5.0 / dbu)

        # Diffusion plate
        layer_diff = ly.layer(1, 0)
        self.cell.shapes(layer_diff).insert(
            pya.Box(0, 0,
                    width_dbu + 4 * five_dbu,
                    width_dbu + 4 * five_dbu))

        # Gate oxide
        layer_gate = ly.layer(2, 0)
        self.cell.shapes(layer_gate).insert(
            pya.Box(2 * five_dbu, 2 * five_dbu,
                    width_dbu + 2 * five_dbu,
                    width_dbu + 2 * five_dbu))

        # Gate metal
        layer_metal = ly.layer(4, 0)
        self.cell.shapes(layer_metal).insert(
            pya.Box(2 * five_dbu - spacing_dbu,
                    2 * five_dbu - spacing_dbu,
                    width_dbu + 2 * five_dbu + spacing_dbu,
                    width_dbu + 2 * five_dbu + spacing_dbu))

        # Vias (left/right columns, top row, bottom-left, bottom-right)
        via_params = {"w": 5.0, "l": self.w + 20 + 4 * SPACING}
        via_cell = ly.create_cell("Via", LIB_NAME, via_params)

        via_params2 = {"w": self.w + 20 + 4 * SPACING, "l": 5.0}
        via_cell2 = ly.create_cell("Via", LIB_NAME, via_params2)

        via_params3 = {"w": (self.w + 20 + 4 * SPACING) / 2, "l": 5.0}
        via_cell3 = ly.create_cell("Via", LIB_NAME, via_params3)

        via_params4 = {"w": (self.w + 20 + 2 * SPACING) / 2 - 10, "l": 5.0}
        via_cell4 = ly.create_cell("Via", LIB_NAME, via_params4)

        t1 = pya.Trans(pya.Point(
            int(-4.5 / 5 * five_dbu), -3 * spacing_dbu))
        t2 = pya.Trans(pya.Point(
            3 * five_dbu + width_dbu + spacing_dbu, -3 * spacing_dbu))
        t3 = pya.Trans(pya.Point(
            -3 * spacing_dbu,
            3 * five_dbu + width_dbu + spacing_dbu))
        t4 = pya.Trans(pya.Point(
            -3 * spacing_dbu, -3 * spacing_dbu))
        t5 = pya.Trans(pya.Point(
            int(((self.w + 20) / 2 + 10) / dbu), -3 * spacing_dbu))

        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t1))
        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t2))
        self.cell.insert(pya.CellInstArray(via_cell2.cell_index(), t3))
        self.cell.insert(pya.CellInstArray(via_cell3.cell_index(), t4))
        self.cell.insert(pya.CellInstArray(via_cell4.cell_index(), t5))
