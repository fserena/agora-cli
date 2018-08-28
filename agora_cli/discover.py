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
from agora_wot.gateway import Gateway

from agora_cli.root import cli
from agora_cli.show import show_ted
from agora_cli.utils import split_arg, jsonify, check_init

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def discover(ctx):
    check_init(ctx)


@discover.command()
@click.pass_obj
@click.option('--turtle', default=False, is_flag=True)
def show(obj, turtle):
    show_ted(obj['ted'], format='text/turtle' if turtle else 'application/ld+json')


@discover.command()
@click.option('--query', required=True)
@click.option('--arg', multiple=True)
@click.option('--host', default='agora')
@click.option('--port', default=80)
@click.pass_context
def seeds(ctx, eco_query, arg, host, port):
    args = dict(map(lambda a: split_arg(a), arg))
    ted = ctx.obj['gw'].discover(eco_query, lazy=False)
    dgw = Gateway(ctx.obj['gw'].agora, ted, cache=None, port=port, server_name=host)
    seeds = dgw.proxy.instantiate_seeds(**args)
    seed_uris = set(reduce(lambda x, y: x + y, seeds.values(), []))
    click.echo(jsonify(list(seed_uris)))
