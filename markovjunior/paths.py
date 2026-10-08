"""Locate assets in an extracted project or in an installed wheel."""
from pathlib import Path


def data_root():
    package=Path(__file__).resolve().parent
    source=package.parent
    if (source/'models.xml').is_file():
        return source
    bundled=package/'assets'
    if (bundled/'models.xml').is_file():
        return bundled
    raise FileNotFoundError('MarkovJunior model assets are missing; pass --base to a complete project')
