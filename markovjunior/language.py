"""Markov 1.0: Python-compatible procedural programming runtime.

This executes user programs; it is not a security sandbox. Browser isolation is
provided by the Web Worker and the browser. Use only trusted code with the CLI.
"""
from __future__ import annotations
import ast
import base64
import contextlib
import importlib.abc
import importlib.util
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import time
import traceback
import types
from .core import DotNetRandom

VERSION = '1.0.0'
SCENE_SCHEMA = 'markov.scene/1'
PROJECT_SCHEMA = 'markov.project/1'
MAX_OBJECTS = 5000


def vector(value, label='vector'):
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f'{label}: expected three numbers')
    result = [float(v) for v in value]
    if not all(math.isfinite(v) and abs(v) <= 1_000_000 for v in result):
        raise ValueError(f'{label}: finite coordinates within ±1,000,000 required')
    return result


def positive(value, label, maximum=10000):
    value = float(value)
    if not math.isfinite(value) or not 0 < value <= maximum:
        raise ValueError(f'{label}: expected a number in (0, {maximum}]')
    return value


def color(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
        raise ValueError('color: use a hexadecimal color such as #f0c674')
    return value


def filename(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('invalid file name')
    path = PurePosixPath(name)
    if path.is_absolute() or any(p in ('.', '..') for p in name.split('/')):
        raise ValueError('file name must stay within the project')
    if not re.fullmatch(r'[A-Za-z0-9_./-]{1,160}', name):
        raise ValueError('file name contains unsupported characters')
    return name


class Output(io.TextIOBase):
    def __init__(self):
        self.parts = []
        self.size = 0
        self.truncated = False

    def write(self, text):
        text = str(text)
        remaining = max(0, 100_000 - self.size)
        self.parts.append(text[:remaining])
        self.size += min(len(text), remaining)
        self.truncated |= len(text) > remaining
        return len(text)

    def getvalue(self):
        return ''.join(self.parts) + ('\n[output truncated at 100,000 characters]\n' if self.truncated else '')


class Budget:
    def __init__(self, seconds=8, lines=1_000_000):
        self.seconds, self.lines = seconds, lines
        self.steps = 0

    def __enter__(self):
        self.deadline = time.monotonic() + self.seconds
        self.previous = sys.gettrace()
        sys.settrace(self.trace)
        return self

    def trace(self, frame, event, arg):
        if event == 'line' and frame.f_code.co_filename.endswith(('.mp', '.py')):
            self.steps += 1
            if self.steps > self.lines or (self.steps % 1000 == 0 and time.monotonic() > self.deadline):
                raise TimeoutError('Execution budget exceeded. Simplify the program or stop it in the editor.')
        return self.trace

    def __exit__(self, *_):
        sys.settrace(self.previous)


class Node:
    def __init__(self, runtime, kind, geometry, name, position, rotation, scale, tint):
        self.runtime = runtime
        self.id = f'node_{runtime.next_id}'
        runtime.next_id += 1
        self.kind, self.geometry = kind, geometry
        self.name = str(name or self.id)
        self.position = vector(position, 'position')
        self.rotation = vector(rotation, 'rotation')
        self.scaling = vector(scale, 'scale')
        self.color = color(tint)
        self.visible = True
        self.tags = []

    def translate(self, x=0, y=0, z=0):
        self.position = [a + b for a, b in zip(self.position, vector([x, y, z]))]
        return self

    def rotate(self, x=0, y=0, z=0):
        self.rotation = [a + b for a, b in zip(self.rotation, vector([x, y, z]))]
        return self

    def resize(self, x=1, y=None, z=None):
        self.scaling = vector([x, x if y is None else y, x if z is None else z], 'scale')
        return self

    def remove(self):
        self.runtime.nodes.pop(self.id, None)

    def to_data(self):
        return {'id': self.id, 'name': self.name, 'kind': self.kind,
                'geometry': self.geometry, 'color': color(self.color),
                'position': vector(self.position, 'position'),
                'rotation': vector(self.rotation, 'rotation'),
                'scaling': vector(self.scaling, 'scale'), 'visible': bool(self.visible),
                'tags': [str(v) for v in self.tags]}


class Scene:
    def __init__(self, runtime):
        self.runtime = runtime
        self.background = '#10141d'
        self.ground = True
        self.ground_color = '#1b2329'
        self.ground_size = 40
        self.camera = {'target': [0, 2, 0], 'radius': 24, 'alpha': -1.15, 'elevation': .5}

    @property
    def objects(self):
        return list(self.runtime.nodes.values())

    def clear(self):
        self.runtime.nodes.clear()

    def find(self, name):
        return next((node for node in self.objects if node.name == name), None)

    def to_data(self):
        camera = dict(self.camera)
        camera['target'] = vector(camera.get('target', [0, 2, 0]), 'camera target')
        for key, default in [('radius', 24), ('alpha', -1.15), ('elevation', .5)]:
            value = float(camera.get(key, default))
            if not math.isfinite(value):
                raise ValueError('camera values must be finite')
            camera[key] = value
        camera['radius'] = positive(camera['radius'], 'camera radius')
        return {'schema': SCENE_SCHEMA, 'background': color(self.background),
                'ground': bool(self.ground), 'ground_color': color(self.ground_color),
                'ground_size': positive(self.ground_size, 'ground size'),
                'camera': camera, 'objects': [node.to_data() for node in self.objects]}


class Runtime:
    def __init__(self, seed=42, parameters=None):
        self.nodes, self.files, self.parameters, self.rules = {}, {}, {}, {}
        self.next_id = 0
        self.supplied = parameters or {}
        self.scene = Scene(self)
        self.keys = set()
        self.mouse = {'x': 0, 'y': 0, 'pressed': False}
        self.seed(seed)

    def seed(self, value=None):
        if value is None:
            return self.seed_value
        if type(value) is not int or not -2147483648 <= value <= 2147483647:
            raise ValueError('seed must be a signed 32-bit integer')
        self.seed_value = value
        self.rng = DotNetRandom(value)
        return value

    def random(self, minimum=0, maximum=1):
        minimum, maximum = float(minimum), float(maximum)
        if not all(math.isfinite(v) for v in (minimum, maximum, maximum - minimum)) or maximum < minimum:
            raise ValueError('random requires a finite ordered interval')
        return minimum + self.rng.double() * (maximum - minimum)

    def randint(self, minimum, maximum):
        if type(minimum) is not int or type(maximum) is not int or not minimum <= maximum or maximum - minimum > 2147483645:
            raise ValueError('randint requires an ordered integer interval of at most 2,147,483,646 values')
        return minimum + self.rng.next(maximum - minimum + 1)

    def choose(self, values, weights=None):
        values = list(values)
        if not values:
            raise ValueError('choose needs at least one value')
        if weights is None:
            return values[self.rng.next(len(values))]
        weights = list(weights)
        if len(weights) != len(values) or any(not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0 for w in weights):
            raise ValueError('choose weights must be positive and match the values')
        point = self.rng.double() * sum(weights)
        for value, weight in zip(values, weights):
            point -= weight
            if point <= 0:
                return value
        return values[-1]

    def noise(self, x, y=0, z=0):
        point = vector([x, y, z], 'noise coordinates')
        origin = [math.floor(v) for v in point]
        blend = [(v - base) ** 2 * (3 - 2 * (v - base)) for v, base in zip(point, origin)]
        def lattice(a, b, c):
            value = ((a * 73856093) ^ (b * 19349663) ^ (c * 83492791) ^ self.seed_value) & 0xffffffff
            value = ((value ^ (value >> 13)) * 1274126177) & 0xffffffff
            return (value ^ (value >> 16)) / 4294967295
        result = 0
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    weight = math.prod(t if bit else 1 - t for t, bit in zip(blend, (dx, dy, dz)))
                    result += lattice(origin[0] + dx, origin[1] + dy, origin[2] + dz) * weight
        return result

    def param(self, name, default, min=None, max=None, step=None):
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,63}', name):
            raise ValueError('invalid parameter name')
        if type(default) not in (int, float, bool, str):
            raise ValueError('parameter defaults must be numbers, booleans or strings')
        for bound in (min, max, step):
            if bound is not None and (type(bound) not in (int, float) or not math.isfinite(bound)):
                raise ValueError(f'{name}: bounds and step must be finite numbers')
        if min is not None and max is not None and min > max or step is not None and step <= 0:
            raise ValueError(f'{name}: invalid bounds or step')
        value = self.supplied.get(name, default)
        if type(default) is bool:
            if type(value) is not bool: raise ValueError(f'{name}: expected a boolean')
        elif type(default) is str:
            if not isinstance(value, str) or len(value) > 500: raise ValueError(f'{name}: expected a short string')
        else:
            if type(value) not in (int, float) or not math.isfinite(value): raise ValueError(f'{name}: expected a finite number')
            if type(default) is int and int(value) != value: raise ValueError(f'{name}: expected an integer')
            if min is not None and value < min or max is not None and value > max: raise ValueError(f'{name}: value outside parameter limits')
            value = int(value) if type(default) is int else float(value)
        self.parameters[name] = {'name': name, 'default': default, 'value': value, 'min': min, 'max': max, 'step': step}
        return value

    def rule(self, function):
        if not callable(function): raise TypeError('rule decorates a function')
        self.rules[function.__name__] = function
        return function

    def node(self, kind, geometry, *, name=None, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1), color='#e8bb80'):
        if len(self.nodes) >= MAX_OBJECTS: raise ValueError(f'Scene limit: {MAX_OBJECTS} objects')
        node = Node(self, kind, geometry, name, position, rotation, scale, color)
        self.nodes[node.id] = node
        return node

    def sphere(self, radius=1, **options):
        return self.node('sphere', {'radius': positive(radius, 'radius')}, **options)

    def box(self, size=(1, 1, 1), **options):
        if isinstance(size, (int, float)): size = [size] * 3
        return self.node('box', {'size': [positive(v, 'size') for v in vector(size)]}, **options)

    def cylinder(self, radius=.5, height=2, **options):
        return self.node('cylinder', {'radius': positive(radius, 'radius'), 'height': positive(height, 'height')}, **options)

    def cone(self, radius=1, height=2, **options):
        return self.node('cone', {'radius': positive(radius, 'radius'), 'height': positive(height, 'height')}, **options)

    def torus(self, radius=1, thickness=.2, **options):
        radius, thickness = positive(radius, 'radius'), positive(thickness, 'thickness')
        if thickness >= radius * 2: raise ValueError('torus thickness must be smaller than its diameter')
        return self.node('torus', {'radius': radius, 'thickness': thickness}, **options)

    def plane(self, width=2, depth=2, **options):
        return self.node('plane', {'width': positive(width, 'width'), 'depth': positive(depth, 'depth')}, **options)

    def line(self, points, width=.05, **options):
        points = list(points)
        if not 2 <= len(points) <= 10000: raise ValueError('line requires 2..10,000 points')
        return self.node('line', {'points': [vector(p) for p in points], 'width': positive(width, 'width')}, **options)

    def mesh(self, vertices, faces, **options):
        vertices, faces = list(vertices), list(faces)
        if not 3 <= len(vertices) <= 10000 or not 1 <= len(faces) <= 20000: raise ValueError('mesh geometry budget exceeded')
        vertices = [vector(v, 'vertex') for v in vertices]
        triangles = []
        for face in faces:
            if not isinstance(face, (list, tuple)) or len(face) != 3 or any(type(i) is not int or not 0 <= i < len(vertices) for i in face):
                raise ValueError('mesh faces must contain three valid vertex indices')
            triangles.append(list(face))
        return self.node('mesh', {'vertices': vertices, 'faces': triangles}, **options)

    def emit(self, name, value, media_type=None):
        name = filename(name)
        if isinstance(value, bytes):
            file = {'name': name, 'content': base64.b64encode(value).decode(), 'encoding': 'base64', 'media_type': media_type or 'application/octet-stream'}
            size = len(value)
        else:
            content = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)
            size = len(content.encode())
            file = {'name': name, 'content': content, 'media_type': media_type or ('application/json' if not isinstance(value, str) else 'text/plain')}
        if size > 5_000_000 or name not in self.files and len(self.files) >= 100: raise ValueError('output file budget exceeded')
        self.files[name] = file
        return name

    def grammar(self, rules, start='<start>', max_depth=8):
        from .procedural.generators import Grammar
        return Grammar(rules).expand(start, self.rng, max_depth=max_depth)[0]

    def generate(self, generator, params=None, targets=None, name='generated'):
        from .procedural import Context, default_registry
        from .paths import data_root
        registry = default_registry()
        doc = registry.generate(generator, params or {}, Context(self.seed_value, self.rng, data_root()))
        for target in targets or ['json']:
            for artifact in registry.render(doc, target, name):
                self.emit(artifact.filename, artifact.content, artifact.media_type)
        return doc.value.to_data() if hasattr(doc.value, 'to_data') else doc.value

    def exports(self):
        names = ['seed', 'random', 'randint', 'choose', 'noise', 'param', 'rule', 'sphere', 'box', 'cylinder', 'cone', 'torus', 'plane', 'line', 'mesh', 'emit', 'grammar', 'generate']
        values = {name: getattr(self, name) for name in names}
        values.update(scene=self.scene, keys=self.keys, mouse=self.mouse, PI=math.pi, TAU=math.tau,
                      sin=math.sin, cos=math.cos, sqrt=math.sqrt,
                      lerp=lambda a, b, t: a + (b - a) * t,
                      clamp=lambda value, minimum, maximum: max(minimum, min(maximum, value)))
        return values


class ProjectImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, sources, exports):
        self.sources, self.exports = sources, exports
        self.loaded = set()

    def find_spec(self, fullname, path=None, target=None):
        name = fullname.replace('.', '/')
        for suffix in ('.mp', '.py'):
            if name + '/__init__' + suffix in self.sources:
                return importlib.util.spec_from_loader(fullname, self,
                    origin=name + '/__init__' + suffix, is_package=True)
        for suffix in ('.mp', '.py'):
            if name + suffix in self.sources:
                return importlib.util.spec_from_loader(fullname, self, origin=name + suffix)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        name = module.__spec__.origin
        module.__dict__.update(self.exports)
        module.__file__ = name
        self.loaded.add(module.__name__)
        exec(compile(self.sources[name], name, 'exec'), module.__dict__)


class Session:
    def __init__(self):
        self.runtime = None
        self.namespace = {}
        self.elapsed = 0
        self.output = Output()
        self.importer = None
        self.previous_modules = {}
        self.temp = None

    def close(self):
        if self.importer:
            for name in self.importer.loaded:
                sys.modules.pop(name, None)
        self.importer = None
        for name, value in self.previous_modules.items():
            if value is None: sys.modules.pop(name, None)
            else: sys.modules[name] = value
        self.previous_modules = {}
        if self.temp: self.temp.cleanup()
        self.temp = None

    def error(self, error):
        frames = traceback.extract_tb(error.__traceback__)
        user = [f for f in frames if f.filename.endswith('.mp') or f.filename in (self.importer.sources if self.importer else {})]
        frame = user[-1] if user else None
        return {'type': type(error).__name__, 'message': str(error),
                'line': error.lineno if isinstance(error, SyntaxError) else frame.lineno if frame else None,
                'column': error.offset if isinstance(error, SyntaxError) else None,
                'file': error.filename if isinstance(error, SyntaxError) else frame.filename if frame else None,
                'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}

    @contextlib.contextmanager
    def environment(self):
        import os
        previous_cwd = os.getcwd()
        previous_path = list(sys.path)
        sys.meta_path.insert(0, self.importer)
        sys.path.insert(0, self.temp.name)
        os.chdir(self.temp.name)
        try:
            with contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.output):
                yield
        finally:
            os.chdir(previous_cwd)
            sys.path[:] = previous_path
            if self.importer in sys.meta_path: sys.meta_path.remove(self.importer)

    def execute(self, project):
        self.close()
        self.runtime = None
        self.namespace = {}
        self.output = Output()
        error = None
        started = time.perf_counter()
        try:
            if not isinstance(project, dict) or project.get('schema') != PROJECT_SCHEMA:
                raise ValueError('expected a markov.project/1 project')
            sources = project.get('files', [])
            if not isinstance(sources, list) or not 1 <= len(sources) <= 50:
                raise ValueError('project requires 1..50 source files')
            checked = {}
            for file in sources:
                name = filename(file['name'])
                source = file['content']
                if name in checked or not isinstance(source, str) or len(source) > 1_000_000:
                    raise ValueError('duplicate name or invalid source contents')
                checked[name] = source
            entry = project.get('entry', 'main.mp')
            if entry not in checked: raise ValueError('entry file does not exist')
            if sum(len(source) for source in checked.values()) > 2_000_000: raise ValueError('project source budget exceeded')
            self.runtime = Runtime(project.get('seed', 42), project.get('parameters', {}))
            exports = self.runtime.exports()
            self.importer = ProjectImporter(checked, exports)
            self.temp = tempfile.TemporaryDirectory()
            for name, source in checked.items():
                target = Path(self.temp.name) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(source)
            self.previous_modules['markov'] = sys.modules.get('markov')
            module = types.ModuleType('markov')
            module.__dict__.update(exports)
            module.__all__ = list(exports)
            sys.modules['markov'] = module
            # Project modules are refreshed when their sources change between runs.
            for name in checked:
                if name.endswith(('.mp', '.py')):
                    module_name = name.rsplit('.', 1)[0].replace('/', '.')
                    if module_name in sys.modules:
                        self.previous_modules[module_name] = sys.modules.pop(module_name)
            self.namespace = {'__name__': '__main__', '__file__': entry, **exports}
            tree = ast.parse(checked[entry], filename=entry)
            with self.environment(), Budget():
                exec(compile(tree, entry, 'exec'), self.namespace)
            # Capture ordinary files written by the program as well as emit() outputs.
            for path in Path(self.temp.name).rglob('*'):
                if path.is_file():
                    name = path.relative_to(self.temp.name).as_posix()
                    if name not in checked and '__pycache__' not in path.parts:
                        self.runtime.emit(name, path.read_bytes())
        except Exception as exception:
            error = self.error(exception)
        self.elapsed = (time.perf_counter() - started) * 1000
        return self.result(error)

    def result(self, error=None):
        try:
            scene = self.runtime.scene.to_data() if self.runtime else {'schema': SCENE_SCHEMA, 'objects': []}
        except Exception as exception:
            scene = {'schema': SCENE_SCHEMA, 'objects': []}
            error = self.error(exception)
        return {'version': VERSION, 'ok': error is None, 'error': error,
                'stdout': self.output.getvalue(), 'scene': scene,
                'files': list(self.runtime.files.values()) if self.runtime else [],
                'parameters': list(self.runtime.parameters.values()) if self.runtime else [],
                'rules': list(self.runtime.rules) if self.runtime else [],
                'animation': error is None and callable(self.namespace.get('update')),
                'elapsed_ms': round(self.elapsed, 3)}

    def frame(self, t, dt, inputs=None):
        if not self.runtime or not callable(self.namespace.get('update')):
            return self.result()
        inputs = inputs or {}
        self.runtime.keys.clear()
        self.runtime.keys.update(str(key) for key in inputs.get('keys', []))
        self.runtime.mouse.update(inputs.get('mouse', {}))
        error = None
        try:
            with self.environment(), Budget(seconds=1, lines=100_000):
                self.namespace['update'](float(t), float(dt))
        except Exception as exception:
            error = self.error(exception)
        return self.result(error)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description='Execute a Markov procedural program (.mp / Python syntax)')
    parser.add_argument('source', type=Path)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', type=Path, default=Path('output'))
    args = parser.parse_args(argv)
    files = [{'name': p.relative_to(args.source.parent).as_posix(), 'content': p.read_text()}
             for p in args.source.parent.rglob('*') if p.is_file() and p.suffix in ('.mp', '.py')]
    session = Session()
    result = session.execute({'schema': PROJECT_SCHEMA, 'seed': args.seed, 'files': files, 'entry': args.source.name})
    print(result['stdout'], end='')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'scene.json').write_text(json.dumps(result['scene'], ensure_ascii=False, indent=2))
    for file in result['files']:
        path = args.output / file['name']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(file['content']) if file.get('encoding') == 'base64' else file['content'].encode())
    session.close()
    if not result['ok']:
        print(result['error']['traceback'], file=sys.stderr)
        return 1
    print(f"{len(result['scene']['objects'])} objects · {result['elapsed_ms']:.1f} ms")
    return 0
