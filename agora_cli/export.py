#!/usr/bin/env python
"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2018 Fernando Serena
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

import click

from agora_cli.root import cli
from agora_cli.utils import check_init, compress, is_init, extract

__author__ = 'Fernando Serena'


@cli.command('export')
@click.pass_context
def export(ctx):
    check_init(ctx)
    compress('.agora', 'agora.zip')


@cli.command('import')
@click.pass_context
@click.argument('file', type=click.Path(exists=True))
def import_from_file(ctx, file):
    if is_init():
        click.echo('[FAIL] Agora is already initialized: ', nl=False)
        ctx.abort()
    extract(file)
    if is_init():
        click.echo('[ OK ] Agora was successfully imported')

