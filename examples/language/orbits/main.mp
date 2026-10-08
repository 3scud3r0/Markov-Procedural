from shapes import orbit

# Modifique o código. Os parâmetros viram controles no Studio.
count = param("particles", 36, min=8, max=120, step=1)
radius = param("radius", 5.0, min=2, max=9, step=0.25)
speed = param("speed", 0.25, min=0, max=2, step=0.05)

scene.background = "#10141d"
scene.ground_color = "#1b2329"
scene.camera = {"target": [0, 2.5, 0], "radius": 19}

core = sphere(radius=1.1, position=[0, 2.5, 0],
              color="#e6edcc", name="Núcleo")
rings = []
for i in range(3):
    ring = torus(radius=radius * (0.6 + i * 0.17),
                 thickness=0.06, position=[0, 2.5, 0],
                 rotation=[0.25 + i * 0.55, 0, i * 0.7],
                 color=choose(["#a9c7b3", "#e8a16f", "#d4d6aa"]),
                 name=f"Órbita {i + 1}")
    rings.append(ring)

particles = orbit(count, radius)
print(f"Markov 1.0 · {len(scene.objects)} objetos gerados")
print("Altere a função orbit em shapes.mp ou crie a sua própria.")
emit("composition.json", {"seed": seed(), "particles": count,
                          "radius": radius})

def update(t, dt):
    for i, ring in enumerate(rings):
        ring.rotate(y=dt * speed * (i + 1))
    core.resize(1 + sin(t * 1.5) * 0.05)
