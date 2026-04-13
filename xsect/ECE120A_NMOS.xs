# ECE 120A NMOS - XSection process script

layers_file(File.join(File.dirname(__FILE__), "..", "ECE120A_NMOS_xsection.lyp"))

height(2.0)
depth(3.0)
extend(10.0)

diff  = layer("1/0")
gate  = layer("2/0")
via   = layer("3/0")
metal = layer("4/0")

substrate = bulk

# field oxidation — 500nm wet
field_ox = deposit(0.5)
mask(diff).etch(0.6, :into => field_ox)

# phosphorus predep
ndiff = mask(diff).grow(0.35, 0.05, :mode => :round, :into => substrate)

# drive-in oxidation — 325nm on bare Si
drivein_ox = mask(diff).grow(0.325)

# gate window etch
mask(gate).etch(0.4, :into => [drivein_ox, field_ox])

# gate oxidation — 45nm dry only
gate_ox = mask(gate).grow(0.045)

# via etch — clears all oxide at contacts
mask(via).etch(0.8, :into => [gate_ox, drivein_ox, field_ox])

# aluminum — 300nm, slight lateral for step coverage
aluminum = mask(metal).grow(0.3, 0.1, :mode => :round)

output("p-Si substrate (10/0)", substrate)
output("n+ diffusion (11/0)", ndiff)
output("Field oxide (12/0)", field_ox)
output("Drive-in oxide (13/0)", drivein_ox)
output("Gate oxide (14/0)", gate_ox)
output("Aluminum (15/0)", aluminum)
