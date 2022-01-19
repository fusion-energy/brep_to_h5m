import paramak

# stage 1 create a brep file
my_reactor = paramak.BallReactor(rotation_angle=180)
my_reactor.export_brep("my_brep_file_with_merged_surfaces.brep")
