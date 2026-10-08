player = sphere(radius=0.5, position=[0, 0.5, 0],
                color="#d5e99b", name="Jogador")
speed = param("speed", 4.0, min=1, max=10, step=0.5)
for i in range(12):
    cone(radius=0.3, height=0.9,
         position=[random(-7, 7), 0.45, random(-7, 7)],
         color="#e8a16f", name=f"Marco {i}")
print("Clique na cena e mova com as setas ou WASD.")

def update(t, dt):
    dx = int("ArrowRight" in keys or "d" in keys)
    dx -= int("ArrowLeft" in keys or "a" in keys)
    dz = int("ArrowDown" in keys or "s" in keys)
    dz -= int("ArrowUp" in keys or "w" in keys)
    player.translate(x=dx * speed * dt, z=dz * speed * dt)
