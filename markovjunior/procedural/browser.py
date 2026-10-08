"""Browser integration: real Python generation, no server or language emulation."""
import json
import math
from pathlib import Path
from .model import Document
from .generators import integer
from .registry import default_registry, json_target
from .pipeline import run_project


def scene3d(params, context):
    trees = integer(params, 'trees', 9, 1, 30)
    depth = integer(params, 'depth', 3, 1, 5)
    rng = context.random
    objects = []
    palette = ['#82d6ae', '#b9de8b', '#e8b16e', '#efcf9c']

    def branch(start, length, angle, remaining, radius, color):
        end = [start[0] + math.sin(angle) * length,
               start[1] + math.cos(angle) * length,
               start[2] + (rng.double() - .5) * length * .65]
        objects.append({'kind': 'branch', 'start': start, 'end': end,
                        'radius': radius, 'color': '#9a876d'})
        if remaining == 0:
            objects.append({'kind': 'leaf', 'position': end,
                            'radius': max(.18, length * .28), 'color': color})
        else:
            spread = .25 + rng.double() * .32
            for direction in (-1, 1):
                branch(end, length * (.63 + rng.double() * .12),
                       angle + direction * spread, remaining - 1, radius * .7, color)

    for index in range(trees):
        theta = index * math.tau / trees
        distance = 3 + rng.double() * 6
        branch([math.cos(theta) * distance, 0, math.sin(theta) * distance],
               1.9 + rng.double() * 1.3, (rng.double() - .5) * .18,
               depth, .13 + rng.double() * .09, palette[rng.next(len(palette))])
    return Document('scene3d', {'schema': 'markovjunior.scene3d/1',
                    'objects': objects}, {'entities': len(objects)})


def browser_generate(recipe):
    registry = default_registry()
    registry.register_generator('scene3d', scene3d)
    registry.register_target('scene3d-json', {'scene3d'}, json_target)
    # A fresh virtual output directory prevents stale results between browser requests.
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp)
        manifest = run_project(recipe, output, registry=registry)
        files = []
        scenes = []
        for job in manifest['jobs']:
            for entry in job['outputs']:
                text = (output / entry['path']).read_text()
                files.append({'name': entry['path'], 'content': text,
                              'media_type': entry['media_type']})
                if job['kind'] == 'scene3d' and entry['target'] == 'scene3d-json':
                    scenes.append(json.loads(text)['value'])
        return json.dumps({'files': files, 'scenes': scenes, 'manifest': manifest},
                          ensure_ascii=False, allow_nan=False)
