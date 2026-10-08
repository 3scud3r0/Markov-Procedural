columns = param("columns", 12, min=4, max=30, step=1)
height = param("height", 4.0, min=2, max=8, step=0.25)
radius = param("radius", 5.0, min=2, max=9, step=0.25)

@rule
def pavilion(count, radius, height):
    for i in range(count):
        angle = i * TAU / count
        x, z = cos(angle) * radius, sin(angle) * radius
        cylinder(radius=0.16, height=height,
                 position=[x, height / 2, z], color="#d5c5aa",
                 name=f"Coluna {i + 1}")
    torus(radius=radius, thickness=0.35,
          position=[0, height, 0], color="#a5bea6", name="Cobertura")
    cylinder(radius=radius + 0.7, height=0.2,
             position=[0, 0.1, 0], color="#777c70", name="Base")

pavilion(columns, radius, height)
scene.camera = {"target": [0, height / 2, 0], "radius": radius * 4}
print(f"Pavilhão: {columns} colunas, altura {height}")
