# Getting Started

1. Start a new mkdocs site

   ```bash
   mkdocs new my-docs
   cd my-docs
   ```
   
2. Add the plugin to the `requirements.txt`

   ```
   git+https://github.com/pivotal/mkdocs-plugins.git#egg=mkdocs-jinja2&subdirectory=mkdocs-jinja2
   git+https://github.com/pivotal/mkdocs-plugins.git#egg=markdown-code-excerpt&subdirectory=markdown-code-excerpt
   ```
   
3. Add to the list of plugins and markdown extensions in `mkdocs.yml`

   ```yaml
   plugins:
   - jinja2: {}
   markdown_extensions:
   - markdown-code-excerpt:
       sections:
         namespace: directory-to-look-for-code-snippets
   ```
  
4. Enjoy with `mkdocs serve`.

# mkdocs-jinja2

This enables [Jinja2](http://jinja.pocoo.org/) as a templating language for the markdown files.
It adds functionality to have logic. 
