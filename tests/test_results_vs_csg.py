import openmc


inner_blanket_radius = 100.0
blanket_thickness = 70.0
blanket_height = 500.0
lower_blanket_thickness = 50.0
upper_blanket_thickness = 40.0
blanket_vv_gap = 20.0
upper_vv_thickness = 10.0
vv_thickness = 10.0
lower_vv_thickness = 10.0


mat_vessel_cell_lower = openmc.Material(1, name='lower_vessel')
mat_vessel_cell_upper = openmc.Material(2, name='upper_vessel')
mat_vessel_cell_cylinder = openmc.Material(3, name='vessel')
mat_blanket_cell_cylinder = openmc.Material(name='blanket')
mat_blanket_cell_upper = openmc.Material(5, name='upper_blanket')
mat_blanket_cell_lower = openmc.Material(6, name='lower_blanket')

for mat in [mat_vessel_cell_lower, mat_vessel_cell_upper, mat_vessel_cell_cylinder]:
    mat.add_element("Fe", 89)
    mat.add_element("Cr", 9.1)
    mat.add_element("Mo", 1)
    mat.add_element("Mn", 0.5)
    mat.add_element("Si", 0.4)
    mat.set_density("g/cm3", 7.96)

for mat in [mat_blanket_cell_cylinder, mat_blanket_cell_upper, mat_blanket_cell_lower]:
    mat.add_element("Li", 100)
    mat.set_density("g/cm3", 0.5)

materials = openmc.Materials([
    mat_vessel_cell_lower,
    mat_vessel_cell_upper,
    mat_vessel_cell_cylinder,
    mat_blanket_cell_cylinder,
    mat_blanket_cell_upper,
    mat_blanket_cell_lower,
])

# surfaces
inner_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius)
outer_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius + blanket_thickness)

inner_vessel_cylinder = openmc.ZCylinder(r=inner_blanket_radius + blanket_thickness + blanket_vv_gap)
outer_vessel_cylinder = openmc.ZCylinder(
    r=inner_blanket_radius + blanket_thickness + blanket_vv_gap + vv_thickness,
    boundary_type="vacuum",
)

upper_vessel_bottom = openmc.ZPlane(z0=blanket_height + lower_vv_thickness + lower_blanket_thickness)
upper_vessel_top = openmc.ZPlane(z0=blanket_height + lower_vv_thickness + lower_blanket_thickness + upper_vv_thickness)

lower_blanket_top = openmc.ZPlane(z0=lower_vv_thickness + lower_blanket_thickness)
lower_blanket_bottom = openmc.ZPlane(z0=lower_vv_thickness)

upper_blanket_bottom = upper_vessel_top
upper_blanket_top = openmc.ZPlane(
    z0=blanket_height + lower_vv_thickness + lower_blanket_thickness + upper_vv_thickness + upper_blanket_thickness,
    boundary_type="vacuum",
)

lower_vessel_top = lower_blanket_bottom
lower_vessel_bottom = openmc.ZPlane(z0=0, boundary_type="vacuum")

# regions
inner_void_region = -upper_vessel_bottom & +lower_blanket_top & -inner_blanket_cylinder
blanket_region = -upper_vessel_bottom & +lower_blanket_top & +inner_blanket_cylinder & -outer_blanket_cylinder

blanket_upper_region = -inner_vessel_cylinder & -upper_blanket_top & +upper_blanket_bottom
blanket_lower_region = -inner_vessel_cylinder & -lower_blanket_top & +lower_blanket_bottom

outer_void_region = -upper_vessel_bottom & +lower_blanket_top & -inner_vessel_cylinder & +outer_blanket_cylinder

vessel_region = -upper_blanket_top & +lower_vessel_bottom & -outer_vessel_cylinder & +inner_vessel_cylinder
vessel_upper_region = -upper_vessel_top & +upper_vessel_bottom & -inner_vessel_cylinder
vessel_lower_region = -lower_vessel_top & +lower_vessel_bottom & -inner_vessel_cylinder

# cells
vessel_cell_lower = openmc.Cell(region=vessel_lower_region)
vessel_cell_upper = openmc.Cell(region=vessel_upper_region)
vessel_cell_cylinder = openmc.Cell(region=vessel_region)
vessel_cell_lower.fill = mat_vessel_cell_lower
vessel_cell_upper.fill = mat_vessel_cell_upper
vessel_cell_cylinder.fill = mat_vessel_cell_cylinder

blanket_cell_cylinder = openmc.Cell(region=blanket_region)
blanket_cell_upper = openmc.Cell(region=blanket_upper_region)
blanket_cell_lower = openmc.Cell(region=blanket_lower_region)
blanket_cell_cylinder.fill = mat_blanket_cell_cylinder
blanket_cell_upper.fill = mat_blanket_cell_upper
blanket_cell_lower.fill = mat_blanket_cell_lower

void_cell1 = openmc.Cell(region=inner_void_region)
void_cell2 = openmc.Cell(region=outer_void_region)

universe = openmc.Universe(
    cells=[
        void_cell1,
        void_cell2,
        vessel_cell_lower,
        vessel_cell_upper,
        vessel_cell_cylinder,
        blanket_cell_cylinder,
        blanket_cell_upper,
        blanket_cell_lower,
    ]
)

geom = openmc.Geometry(universe)

tallies = openmc.Tallies()
# cell_filter = openmc.CellFilter(
#     [
#         vessel_cell_lower,
#         vessel_cell_upper,
#         vessel_cell_cylinder,
#         blanket_cell_cylinder,
#         blanket_cell_upper,
#         blanket_cell_lower,
#     ]
# )
material_filter = openmc.MaterialFilter(
    materials
)
flux_tally = openmc.Tally(name="flux")
flux_tally.filters = [material_filter]
flux_tally.scores = ["flux"]
tallies.append(flux_tally)

max_source_height = blanket_height + lower_vv_thickness + lower_blanket_thickness
min_source_height = lower_vv_thickness + lower_blanket_thickness
range_of_source_heights = max_source_height - min_source_height
# 0.5 is fractional_height_of_source
absolute_height_of_source = (0.5 * range_of_source_heights) + min_source_height


# initialises a new source object
my_source = openmc.Source()

# sets the location of the source to x=0 y=0 z=0
my_source.space = openmc.stats.Point((0, 0, absolute_height_of_source))

# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()

# sets the energy distribution to 100% 14MeV neutrons
my_source.energy = openmc.stats.Discrete([14e6], [1])


settings = openmc.Settings()
settings.inactive = 0
settings.run_mode = "fixed source"
settings.batches = 10
settings.particles = 10000
settings.source = my_source


model = openmc.model.Model(geom, materials, settings, tallies)
sp_filename = model.run()
sp = openmc.StatePoint(sp_filename)

flux_tally = sp.get_tally(name="flux")
df_csg = flux_tally.get_pandas_dataframe()
# flux_tally_result = df["mean"].sum()

import os
os.system('rm summary.h5')
os.system('rm *.h5')

import paramak

reactor = paramak.FlfSystemCodeReactor(
    inner_blanket_radius = 100.0,
    blanket_thickness = 70.0,
    blanket_height = 500.0,
    lower_blanket_thickness = 50.0,
    upper_blanket_thickness = 40.0,
    blanket_vv_gap = 20.0,
    upper_vv_thickness = 10.0,
    vv_thickness = 10.0,
    lower_vv_thickness = 10.0,
    rotation_angle=360
)
reactor.export_dagmc_h5m(
    "dagmc.h5m",
    min_mesh_size = 1.0,
    max_mesh_size = 1.5,
)

dag_univ = openmc.DAGMCUniverse(filename="dagmc.h5m")
bound_dag_univ = dag_univ.bounded_universe()
geometry = openmc.Geometry(root=bound_dag_univ)

model = openmc.model.Model(geometry, materials, settings, tallies)

sp_filename = model.run()
sp = openmc.StatePoint(sp_filename)

flux_tally = sp.get_tally(name="flux")
df_cad = flux_tally.get_pandas_dataframe()
# flux_tally_result = df["mean"].sum()
print(df_csg)
print(df_cad)

#    material nuclide score     mean  std. dev.
# 0         1   total  flux 1.58e+00   2.49e-02
# 1         2   total  flux 4.64e+00   5.93e-02
# 2         3   total  flux 1.63e+01   8.00e-02
# 3         4   total  flux 2.45e+02   5.40e-01
# 4         5   total  flux 7.25e+00   1.06e-01
# 5         6   total  flux 1.84e+01   1.57e-01
#    material nuclide score     mean  std. dev.
# 0         1   total  flux 1.32e+00   2.20e-02
# 1         2   total  flux 4.04e+00   6.26e-02
# 2         3   total  flux 1.64e+01   9.60e-02
# 3         4   total  flux 2.43e+02   5.31e-01
# 4         5   total  flux 5.93e+00   8.33e-02
# 5         6   total  flux 1.62e+01   1.11e-01


#    material nuclide score     mean  std. dev.
# 0         1   total  flux 1.58e+00   2.49e-02
# 1         2   total  flux 4.64e+00   5.93e-02
# 2         3   total  flux 1.63e+01   8.00e-02
# 3         4   total  flux 2.45e+02   5.40e-01
# 4         5   total  flux 7.25e+00   1.06e-01
# 5         6   total  flux 1.84e+01   1.57e-01
#    material nuclide score     mean  std. dev.
# 0         1   total  flux 1.34e+00   2.06e-02
# 1         2   total  flux 4.01e+00   6.03e-02
# 2         3   total  flux 1.64e+01   9.30e-02
# 3         4   total  flux 2.43e+02   5.37e-01
# 4         5   total  flux 5.81e+00   7.16e-02
# 5         6   total  flux 1.63e+01   1.10e-01
