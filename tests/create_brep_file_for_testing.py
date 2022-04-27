import paramak

my_reactor = paramak.FlfSystemCodeReactor()
my_reactor.export_brep("test_brep_file.brep")

my_cube_1 = paramak.ExtrudeStraightShape(
    name='my_cube_1',
    points=[
        [0,0],    
        [0,10],    
        [10,10],    
        [10,0],    
    ],
    distance=5
)
my_cube_2 = paramak.ExtrudeStraightShape(
    name='my_cube_2',
    points=[
        [0,0],    
        [0,10],    
        [-10,10],    
        [-10,0],    
    ],
    distance=5
)
my_cubes=paramak.Reactor([my_cube_1, my_cube_2])
my_cubes.export_brep("test_two_cubes.brep")
