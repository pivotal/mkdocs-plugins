from distutils.core import setup

setup(
    name='mkdocs-jinja2',
    version='0.0.1',
    author='JT Archie',
    author_email='jarchie@pivotal',
    packages=['mkdocs_jinja2'],
    description='Uses jinja2 and file system loader (for include and partials)',
    install_requires=['regex'],
    entry_points={
        'mkdocs.plugins': [
            'jinja2 = mkdocs_jinja2:JinjaMkDocPlugin',
        ]
    }
)