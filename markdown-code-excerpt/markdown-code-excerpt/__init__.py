__version__ = '0.0.1'

import os
import re
import subprocess
import textwrap

import regex
from markdown import Extension
from markdown.preprocessors import Preprocessor


class ExcerptPreprocessor(Preprocessor):
    RE_EXCERPT = re.compile(
        r'''(?x)
        ^(?P<space>[ \t]*)
         -{2,}excerpt-{2,}[ \t]+
         (?P<excerpt>(?:"(?:\\"|[^"\n\r])+?"|'(?:\\'|[^'\n\r])+?'))(?![ \t])
        \r?$
        '''
    )

    def __init__(self, config, md):
        self.sections = config.get('sections')
        self.code_snippets = {}
        self.tab_length = md.tab_length
        super(ExcerptPreprocessor, self).__init__()

    def run(self, lines):
        """Process snippets."""

        self.seen = set()
        return self.parse_excerpts(lines)

    def parse_excerpts(self, lines):
        new_lines = []

        for line in lines:
            m = self.RE_EXCERPT.match(line)
            if m:
                space = m.group('space').expandtabs(self.tab_length)
                repo_name, excerpt_name = m.group('excerpt').strip()[1:-1].split('/')

                syntax, contents = self._code_excerpt(repo_name, excerpt_name)
                new_lines.append(space + "```" + syntax)
                new_lines.extend(
                    [space + l for l in contents],
                )
                new_lines.append(space + "```")

            else:
                new_lines.append(line)

        return new_lines

    def _code_excerpt(self, repo_name, excerpt_name):
        if self.sections.get(repo_name):
            repo = self.sections[repo_name]
            root = os.path.abspath(repo)

            if repo_name not in self.code_snippets:
                snippets = {}
                names = []
                try:
                    # this uses `rg` as searching across files is not something we need to reprogram
                    output = subprocess.check_output(['rg', '-m', '1', '-l', 'code_snippet [\w-]+ start', root])
                    names = output.splitlines()
                except subprocess.CalledProcessError as e:
                    names = []
                finder = regex.compile(r"""code_snippet ([\w-]+) start (\w+)\n(.*)\n.*?code_snippet \1 end""",
                                       regex.MULTILINE | regex.DOTALL)
                for name in names:
                    path = os.path.join(root, name.decode())
                    f = open(path, 'r')
                    matches = finder.findall(f.read(), overlapped=True)
                    for match in matches:
                        name, syntax, contents = match
                        contents = textwrap.dedent(
                            re.sub(r"""^\s*# code_snippet.*$\n?""", '', contents, 0, regex.MULTILINE))
                        snippets[name] = (syntax, contents.splitlines())

                self.code_snippets[repo_name] = snippets

            if excerpt_name in self.code_snippets[repo_name]:
                (syntax, contents) = self.code_snippets[repo_name][excerpt_name]
                return syntax, contents

            raise Exception(
                'could not find code snippet "%s" under repo "%s" -- please check for "rg" or entry in ".gitignore"' % (
                    excerpt_name, repo_name))
        else:
            raise Exception('dependent section "%s" not defined in mkdocs.yml' % (repo_name))


class ExcerptExtension(Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'sections': [{}, "hash-map of name and directory lookups"]
        }

        super(ExcerptExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        """Register the extension."""

        self.md = md
        md.registerExtension(self)
        config = self.getConfigs()
        snippet = ExcerptPreprocessor(config, md)
        md.preprocessors.register(snippet, "excerpt", 32)


def makeExtension(*args, **kwargs):
    """Return extension."""

    return ExcerptExtension(*args, **kwargs)
