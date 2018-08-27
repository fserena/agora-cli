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
from agora_cli.utils import jsonify, check_init

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def list(ctx):
    check_init(ctx)


@list.command('extensions')
@click.pass_context
def list_extensions(ctx):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.extensions))


@list.command('types')
@click.pass_context
def list_types(ctx):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.agora.fountain.types))


@list.command('properties')
@click.pass_context
def list_properties(ctx):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.agora.fountain.properties))


@list.command('prefixes')
@click.pass_context
def list_prefixes(ctx):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.agora.fountain.prefixes))


@list.command('tds')
@click.pass_context
def list_tds(ctx):
    ted = ctx.obj['gw'].ted
    td_ids = map(lambda x: x.id, ted.ecosystem.tds)
    click.echo(jsonify(td_ids))


@list.command('things')
@click.pass_context
def list_things(ctx):
    ted = ctx.obj['gw'].ted
    thing_ids = map(lambda x: x.id, ted.ecosystem.tds)
    thing_ids.extend(map(lambda x: x.node, ted.ecosystem.non_td_root_resources))
    click.echo(jsonify(thing_ids))
