import pya
import math

SPACING = 1.5
LIB_NAME = "ECE120A_NMOS"


class CorneredResistor(pya.PCellDeclarationHelper):

    def __init__(self):
        super(CorneredResistor, self).__init__()

        self.param("w", self.TypeDouble, "Width", default=10.0)
        self.param("o_w", self.TypeDouble, "Outer Width", default=50.0)
        self.param("r", self.TypeDouble, "Resistance", default=1000.0)
        self.param("rs", self.TypeDouble, "Sheet Resistance", default=15.0)
        self.param("t", self.TypeInt, "Turns", readonly=True)

    def display_text_impl(self):
        return "CorneredResistor(Width={:.3f},Res={:.3f})".format(self.w, self.r)

    def coerce_parameters_impl(self):
        if self.w <= 4.5:
            self.w = 4.5
        if self.o_w <= 3 * self.w:
            self.o_w = 3 * self.w
        if self.rs <= 0:
            self.rs = 0.001
        if self.r <= 0:
            self.r = 0.001
        self.t = math.floor(self.r / (self.rs * (0.414 + (self.o_w / self.w))))

    def produce_impl(self):
        ly = self.layout
        layer_index = ly.layer(1, 0)

        dbu = ly.dbu
        width_dbu = int(self.w / dbu)
        length_dbu = int(self.o_w / dbu)
        five_dbu = width_dbu  # original uses int(width/dbu) for both

        for i in range(self.t):
            seg = pya.Box(
                i * (width_dbu + five_dbu), 0,
                width_dbu + i * (width_dbu + five_dbu), length_dbu,
            )
            if (i % 2) == 0:
                corn = pya.Box(
                    i * (width_dbu + five_dbu), length_dbu - width_dbu,
                    2 * width_dbu + five_dbu + i * (width_dbu + five_dbu), length_dbu,
                )
            else:
                corn = pya.Box(
                    i * (width_dbu + five_dbu), 0,
                    2 * width_dbu + five_dbu + i * (width_dbu + five_dbu), width_dbu,
                )
            self.cell.shapes(layer_index).insert(seg)
            self.cell.shapes(layer_index).insert(corn)

        r_prime = self.t * (self.o_w / self.w + 0.414) * self.rs
        l_prime = (self.r - r_prime) / self.rs * self.w
        l_prime_dbu = int(l_prime / dbu)

        if (self.t % 2) == 0:
            tail = pya.Box(
                self.t * (width_dbu + five_dbu), 0,
                width_dbu + self.t * (width_dbu + five_dbu), l_prime_dbu,
            )
            t2 = pya.Trans(pya.Point(
                self.t * (width_dbu + five_dbu), l_prime_dbu))
        else:
            tail = pya.Box(
                self.t * (width_dbu + five_dbu), length_dbu,
                width_dbu + self.t * (width_dbu + five_dbu),
                length_dbu - l_prime_dbu,
            )
            t2 = pya.Trans(pya.Point(
                self.t * (width_dbu + five_dbu),
                length_dbu - l_prime_dbu - width_dbu))

        self.cell.shapes(layer_index).insert(tail)

        via_params = {
            "w": self.w - (2 * SPACING),
            "l": self.w - (2 * SPACING),
        }
        via_cell = ly.create_cell("Via", LIB_NAME, via_params)

        t1 = pya.Trans(pya.Point(0, 0))
        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t1))
        self.cell.insert(pya.CellInstArray(via_cell.cell_index(), t2))
