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
from agora_cli.utils import store_config, is_init, init_base

__author__ = 'Fernando Serena'


@cli.command()
@click.option('--host')
@click.option('--port', type=int)
@click.option('--extension-base', default='http://agora.org/extensions/')
@click.option('--repository-base', default='http://agora.org/data/')
@click.option('--repo-sparql-host', default=None)   # http://localhost:7200/repositories/tds
@click.option('--repo-update-host', default=None)   # http://localhost:7200/repositories/tds/statements
@click.option('--repo-cache-host', default=None)
@click.option('--repo-cache-db', default=1)
@click.option('--repo-cache-port', default=None)
@click.pass_context
def init(ctx, **kwargs):
    if is_init():
        click.echo("[FAIL] Couldn't init Agora: ", nl=False, err=True)
        ctx.abort()

    init_base()
    store_config(**kwargs)
    click.echo('[ OK ] Agora is ready')
