@rule
def orbit(count, radius):
    """Uma regra é uma função reutilizável, não um bloco fixo."""
    palette = ["#d5e99b", "#e8a16f", "#9fbcaf", "#e9d3aa"]
    objects = []
    for i in range(count):
        angle = i * TAU / count
        distance = radius + random(-0.3, 0.8)
        height = 2.5 + sin(angle * 3) * 1.7
        node = sphere(radius=random(0.09, 0.28),
                      position=[cos(angle) * distance, height,
                                sin(angle) * distance],
                      color=choose(palette), name=f"Partícula {i}")
        objects.append(node)
    return objects
