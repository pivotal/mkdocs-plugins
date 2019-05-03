__version__ = '0.0.1'

from jinja2 import Environment, FileSystemLoader, lexer, nodes, TemplateRuntimeError
from jinja2.ext import Extension
from mkdocs import plugins, config
import os
import regex
import subprocess


class CodeSnippetExtension(Extension):
    tags = {'code_snippet'}

    class CouldNotFindSnippet(Exception):
        pass

    def __init__(self, environment):
        super(CodeSnippetExtension, self).__init__(environment)
        environment.extend(dependent_sections={}, code_snippets={})

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = [parser.parse_expression()]
        parser.stream.skip_if('comma')
        args.append(parser.parse_expression())
        return nodes.Output([
            self.call_method('_code_snippet', args, lineno=lineno)
            ], lineno=lineno)


    def _code_snippet(self, repo_name, code_name):
        if self.environment.dependent_sections.get(repo_name):
            repo = self.environment.dependent_sections[repo_name]
            root = os.path.abspath(repo)

            if repo_name not in self.environment.code_snippets:
                snippets = {}
                names = []
                try:
                    # this uses `rg` as searching across files is not something we need to reprogram
                    output = subprocess.check_output(['rg', '-m', '1', '-l', 'code_snippet [\w-]+ start', root])
                    names = output.splitlines()
                except subprocess.CalledProcessError as e:
                    names = []
                finder = regex.compile(r"""code_snippet ([\w-]+) start (\w+)\n(.*)\n.*?code_snippet \1 end""", regex.MULTILINE | regex.DOTALL)
                for name in names:
                    path = os.path.join(root, name.decode())
                    f = open(path, 'r')
                    matches = finder.findall(f.read(), overlapped=True)
                    for match in matches:
                        snippets[match[0]] = """\n\n```%s\n%s\n```\n\n""" % (match[1], match[2])
                self.environment.code_snippets[repo_name] = snippets

            if code_name in self.environment.code_snippets[repo_name]:
                return self.environment.code_snippets[repo_name][code_name]

            raise TemplateRuntimeError('could not find code snippet "%s" under repo "%s" -- please check for "rg" or entry in ".gitignore"' % (code_name, repo_name))
        else:
            raise TemplateRuntimeError('dependent section "%s" not defined in mkdocs.yml' % (repo_name))


class JinjaMkDocPlugin(plugins.BasePlugin):
    config_scheme = [
        ('dependent_sections', config.config_options.OptionallyRequired(default=dict()))
    ]


    def on_page_markdown(self, markdown, page, config, files):
        env = Environment(
            loader=FileSystemLoader([
                os.path.dirname(page.file.abs_src_path),
                config['docs_dir'],
            ]),
            extensions=[CodeSnippetExtension],
            )
        env.dependent_sections=self.config['dependent_sections']
        return env.from_string(markdown).render(config=config)
