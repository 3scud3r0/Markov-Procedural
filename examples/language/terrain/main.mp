resolution = param("resolution", 24, min=8, max=45, step=1)
height = param("height", 4.0, min=0.2, max=8, step=0.2)

vertices = []
faces = []
for z in range(resolution):
    for x in range(resolution):
        y = noise(x * 0.12, z * 0.12) * height
        y += noise(x * 0.35, z * 0.35) * height * 0.15
        vertices.append([x - resolution / 2, y, z - resolution / 2])

for z in range(resolution - 1):
    for x in range(resolution - 1):
        a = z * resolution + x
        faces.extend([[a, a + resolution, a + 1],
                      [a + 1, a + resolution, a + resolution + 1]])

mesh(vertices, faces, color="#9db593", name="Terreno")
scene.ground = False
scene.camera = {"radius": resolution * 1.4, "target": [0, 1, 0]}
print(f"Malha própria: {len(vertices)} vértices, {len(faces)} triângulos")
emit("terrain.json", {"vertices": vertices, "faces": faces})
