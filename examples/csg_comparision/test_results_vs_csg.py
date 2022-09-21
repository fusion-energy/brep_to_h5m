import openmc

import os


inner_blanket_radius = 100.0
blanket_thickness = 1.0
blanket_height = 5.0
lower_blanket_thickness = 1.0
upper_blanket_thickness = 1.0
blanket_vv_gap = 20.0
upper_vv_thickness = 1.0
vv_thickness = 1.0
lower_vv_thickness = 1.0


mat_vessel_cell_lower = openmc.Material(1, name="lower_vessel")
mat_vessel_cell_upper = openmc.Material(2, name="upper_vessel")
mat_vessel_cell_cylinder = openmc.Material(3, name="vessel")
mat_blanket_cell_cylinder = openmc.Material(name="blanket")
mat_blanket_cell_upper = openmc.Material(5, name="upper_blanket")
mat_blanket_cell_lower = openmc.Material(6, name="lower_blanket")

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

materials = openmc.Materials(
    [
        mat_vessel_cell_lower,
        mat_vessel_cell_upper,
        mat_vessel_cell_cylinder,
        mat_blanket_cell_cylinder,
        mat_blanket_cell_upper,
        mat_blanket_cell_lower,
    ]
)

# surfaces
inner_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius)
outer_blanket_cylinder = openmc.ZCylinder(r=inner_blanket_radius + blanket_thickness)

inner_vessel_cylinder = openmc.ZCylinder(
    r=inner_blanket_radius + blanket_thickness + blanket_vv_gap
)
outer_vessel_cylinder = openmc.ZCylinder(
    r=inner_blanket_radius + blanket_thickness + blanket_vv_gap + vv_thickness,
    boundary_type="vacuum",
)

upper_vessel_bottom = openmc.ZPlane(
    z0=blanket_height + lower_vv_thickness + lower_blanket_thickness
)
upper_vessel_top = openmc.ZPlane(
    z0=blanket_height
    + lower_vv_thickness
    + lower_blanket_thickness
    + upper_vv_thickness
)

lower_blanket_top = openmc.ZPlane(z0=lower_vv_thickness + lower_blanket_thickness)
lower_blanket_bottom = openmc.ZPlane(z0=lower_vv_thickness)

upper_blanket_bottom = upper_vessel_top
upper_blanket_top = openmc.ZPlane(
    z0=blanket_height
    + lower_vv_thickness
    + lower_blanket_thickness
    + upper_vv_thickness
    + upper_blanket_thickness,
    boundary_type="vacuum",
)

lower_vessel_top = lower_blanket_bottom
lower_vessel_bottom = openmc.ZPlane(z0=0, boundary_type="vacuum")

# regions
inner_void_region = -upper_vessel_bottom & +lower_blanket_top & -inner_blanket_cylinder
blanket_region = (
    -upper_vessel_bottom
    & +lower_blanket_top
    & +inner_blanket_cylinder
    & -outer_blanket_cylinder
)

blanket_upper_region = (
    -inner_vessel_cylinder & -upper_blanket_top & +upper_blanket_bottom
)
blanket_lower_region = (
    -inner_vessel_cylinder & -lower_blanket_top & +lower_blanket_bottom
)

outer_void_region = (
    -upper_vessel_bottom
    & +lower_blanket_top
    & -inner_vessel_cylinder
    & +outer_blanket_cylinder
)

vessel_region = (
    -upper_blanket_top
    & +lower_vessel_bottom
    & -outer_vessel_cylinder
    & +inner_vessel_cylinder
)
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
material_filter = openmc.MaterialFilter(materials)
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
settings.batches = 100
settings.particles = 100000
settings.source = my_source


model = openmc.model.Model(geom, materials, settings, tallies)
sp_filename = model.run()
sp = openmc.StatePoint(sp_filename)

flux_tally = sp.get_tally(name="flux")
df_csg = flux_tally.get_pandas_dataframe()
# flux_tally_result = df["mean"].sum()


os.system("rm summary.h5")
os.system("rm *.h5")

import paramak


reactor = paramak.FlfSystemCodeReactor(
    inner_blanket_radius=inner_blanket_radius,
    blanket_thickness=blanket_thickness,
    blanket_height=blanket_height,
    lower_blanket_thickness=lower_blanket_thickness,
    upper_blanket_thickness=upper_blanket_thickness,
    blanket_vv_gap=blanket_vv_gap,
    upper_vv_thickness=upper_vv_thickness,
    vv_thickness=vv_thickness,
    lower_vv_thickness=lower_vv_thickness,
    rotation_angle=360,
)
reactor.export_dagmc_h5m(
    "dagmc.h5m",
    min_mesh_size=3,
    max_mesh_size=5,
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


def get_material_by_id(id, materials=materials):
    for mat in materials:
        if mat.id == id:
            return mat


df_csg.insert(
    2,
    "mat name",
    [get_material_by_id(mat).name for mat in list(df_csg["material"])],
    True,
)
df_cad.insert(
    2,
    "mat name",
    [get_material_by_id(mat).name for mat in list(df_cad["material"])],
    True,
)

df_csg = df_csg.rename(columns={"mean": "mean_csg", "std. dev.": "std. dev. csg"})
df_cad = df_cad.rename(columns={"mean": "mean_cad", "std. dev.": "std. dev. cad"})

print(df_csg)
print(df_cad)


# 1.5549438439898378 1.3299269766930735 1.1691949041114118
# 4.696257920584921 4.082150417026734 1.150437255079267
# 16.280557821798954 16.393471191004384 0.993112296481334
# 244.29074065403037 243.0492716648376 1.0051078901849364
# 7.388731296232558 6.053608101678864 1.2205499880614044
# 18.260504975139252 16.17669213676271 1.1288157566923664

# b=100, p=100000
# 1.5543477244251156 1.3260859262024258 1.172131981580088
# 4.705491823101355 4.0944750312429745 1.1492295806412312
# 16.295530080793952 16.404948339511964 0.9933301674315869
# 244.15947278289914 242.90406162239725 1.0051683415753396
# 7.386152149233408 6.022996641814896 1.226325131572339
# 18.274382238545524 16.16970741424977 1.1301615898405792

# b=100, p=1000000
# lower_vessel 1.555600644251345 1.3274032147242805 1.1719126690336246
# upper_vessel 4.699525539589862 4.08746316614407 1.1497413795714237
# vessel 16.298482851950833 16.40484357969663 0.993516504608588
# blanket 244.09717056955716 242.83685556747457 1.0051899659099828
# upper_blanket 7.385768007201486 6.011820069342225 1.2285410943793582
# lower_blanket 18.283485117031383 16.19514968903729 1.1289482016586554


# for row_csg, row_cad in zip(df_csg, df_cad):

for (index_csg, row_csg), (index_cad, row_cad) in zip(
    df_csg.iterrows(), df_cad.iterrows()
):
    print(
        row_csg["mat name"],
        row_csg["mean_csg"],
        row_cad["mean_cad"],
        row_csg["mean_csg"] / row_cad["mean_cad"],
    )
