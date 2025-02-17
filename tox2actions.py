# tox2actions
import re
import sys
from io import StringIO
from typing import Generator, Iterable, Iterator

import tox
import yaml
from packaging.version import Version


def main():
    envs = get_tox_envs()
    versions = extract_versions(envs)
    valid_versions = filter(is_python_version_valid, versions)
    replace_strategy_matrix(valid_versions)


def get_tox_envs() -> Iterator[str]:
    with Capturing() as envs:
        tox.main(['-l'])
    return envs


class Capturing(list):

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class Versions:

    def __init__(self, python_version: Version, django_version: Version):
        self.python_version = python_version
        self.django_version = django_version


def extract_versions(tox_envs: list[str]) -> Generator[Versions, None, None]:
    for env in tox_envs:
        [py_env, django_env] = env.split('-')
        py_match = re.match(r'py(\d)(\d+)', py_env)
        django_match = re.match(r'django(\d)(\d+)', django_env)
        if py_match and django_match:
            python_version = Version(f'{py_match.group(1)}.{py_match.group(2)}')
            django_version = Version(f'{django_match.group(1)}.{django_match.group(2)}')
            versions = Versions(python_version=python_version, django_version=django_version)
            yield versions


def is_python_version_valid(versions: Versions) -> bool:
    return versions.python_version >= Version('3.8')


def replace_strategy_matrix(versions: Iterable[Versions], path='.github/workflows/actions.yml'):
    include = map(versions_as_include, versions)

    with open(path, 'r') as file:
        yaml_content = yaml.safe_load(file)

    with open(path, mode='w') as file:
        yaml_content['jobs']['build']['strategy']['matrix']['include'] = list(include)
        yaml.dump(yaml_content, file)


def versions_as_include(versions: Versions):
    include = {
        'python-version': str(versions.python_version),
        'django-version': str(versions.django_version),
    }
    return include


if __name__ == '__main__':
    main()
