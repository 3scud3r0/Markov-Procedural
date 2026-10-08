"""Procedural recipes from the command line."""
import argparse
import json
from pathlib import Path
from .registry import default_registry
from .pipeline import run_project
from ..paths import data_root


def main(argv=None):
    parser=argparse.ArgumentParser(description='Generate code, custom languages, text, data and scenes from seeded recipes.')
    parser.add_argument('recipe',nargs='?',type=Path)
    parser.add_argument('--output',type=Path,default=Path('generated'))
    parser.add_argument('--seed',type=int)
    parser.add_argument('--base',type=Path,default=data_root())
    parser.add_argument('--plugin',type=Path,action='append',default=[],help='Explicitly load a Python file defining register(registry)')
    parser.add_argument('--list-targets',action='store_true')
    args=parser.parse_args(argv)
    registry=default_registry()
    try:
        for plugin in args.plugin:registry.load_plugin(plugin)
        if args.list_targets:
            print('Generators: '+', '.join(registry.generators))
            for name,target in registry.targets.items():print(f'{name}: {", ".join(sorted(target.kinds))}')
            return
        if args.recipe is None:parser.error('provide a recipe JSON or --list-targets')
        recipe=json.loads(args.recipe.read_text(encoding='utf-8'))
        manifest=run_project(recipe,args.output,seed=args.seed,registry=registry,base=args.base)
    except (ValueError,OSError,KeyError,TypeError) as exc:
        parser.exit(2,f'Generation failed: {exc}\n')
    for job in manifest['jobs']:
        print(f'{job["name"]}: {job["kind"]}, seed={job["seed"]}, outputs={len(job["outputs"])}')
    print(f'Manifest: {args.output / "manifest.json"}')
