import openmc
import openmc_data_downloader as odd
import math

# simplified material definitions have been used to keen this example minimal
mat_dag_material_tag = openmc.Material(name="dag_material_tag")
mat_dag_material_tag.add_element("H", 1, "ao")
mat_dag_material_tag.set_density("g/cm3", 0.00001)

materials = openmc.Materials(
    [
        mat_dag_material_tag,
    ]
)

# downloads the nuclear data and sets the openmc_cross_sections environmental variable
odd.just_in_time_library_generator(libraries="ENDFB-7.1-NNDC", materials=materials)

# makes use of the dagmc geometry
dag_univ = openmc.DAGMCUniverse("dagmc_from_coords.h5m")

# creates an edge of universe boundary surface
vac_surf = openmc.Sphere(r=10000, surface_id=9999, boundary_type="vacuum")

# specifies the region as below the universe boundary
region = -vac_surf

# creates a cell from the region and fills the cell with the dagmc geometry
containing_cell = openmc.Cell(cell_id=9999, region=region, fill=dag_univ)

geometry = openmc.Geometry(root=[containing_cell])

# initialises a new source object
my_source = openmc.Source()
# sets the location of the source to x=0 y=0 z=0
my_source.space = openmc.stats.Point((0, 0, 0))
# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()
# sets the energy distribution to 100% 14MeV neutrons
my_source.energy = openmc.stats.Discrete([14e6], [1])


# specifies the simulation computational intensity
settings = openmc.Settings()
settings.batches = 10
settings.particles = 10000
settings.inactive = 0
settings.run_mode = "fixed source"
settings.source = my_source

# adds a tally to record the heat deposited in entire geometry
cell_tally = openmc.Tally(name="heating")
cell_tally.scores = ["heating"]

# creates a mesh that covers the geometry
mesh = openmc.RegularMesh()
mesh.dimension = [100, 100, 100]
mesh.lower_left = [
    -10,
    -10,
    -10,
]  # x,y,z coordinates start at 0 as this is a sector model
mesh.upper_right = [10, 10, 10]

# makes a mesh tally using the previously created mesh and records heating on the mesh
mesh_tally = openmc.Tally(name="heating_on_mesh")
mesh_filter = openmc.MeshFilter(mesh)
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ["heating"]

# groups the two tallies
tallies = openmc.Tallies([cell_tally, mesh_tally])

# builds the openmc model
my_model = openmc.Model(
    materials=materials, geometry=geometry, settings=settings, tallies=tallies
)

# starts the simulation
my_model.run()
