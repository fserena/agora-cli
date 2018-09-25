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
from agora_wot.blocks.td import TD

from agora_cli.root import cli
from agora_cli.utils import jsonify, show_ted, show_td, show_thing, check_init, load_config, error

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def show(ctx):
    check_init(ctx)


@show.command('extension')
@click.pass_context
@click.argument('name')
def show_extension(ctx, name):
    gw = ctx.obj['gw']
    g = gw.get_extension(name)
    click.echo(g.serialize(format='turtle'))


@show.command('prefixes')
@click.pass_context
def show_prefixes(ctx):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.agora.fountain.prefixes))


@show.command('type')
@click.pass_context
@click.argument('name')
def show_prefixes(ctx, name):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.agora.fountain.get_type(name)))


@show.command('property')
@click.pass_context
@click.argument('name')
def show_prefixes(ctx, name):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.agora.fountain.get_property(name)))


@show.command('paths')
@click.pass_context
@click.argument('source')
@click.argument('dest')
def show_paths(ctx, source, dest):
    gw = ctx.obj['gw']
    click.echo(jsonify(
        gw.agora.fountain.get_paths(dest, force_seed=[('<{}-uri>'.format(source.lower()).replace(':', '-'), source)])))


@show.command('ted')
@click.pass_context
@click.option('--turtle', default=False, is_flag=True)
def _show_ted(ctx, turtle):
    ted = ctx.obj['gw'].ted
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')


@show.command('td')
@click.argument('id', type=unicode)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def _show_td(ctx, id, turtle):
    try:
        td = ctx.obj['gw'].get_description(id)
        show_td(td, format='text/turtle' if turtle else 'application/ld+json')
    except Exception as e:
        error(u'{},{}'.format(type(e), e.message))


@show.command('thing')
@click.argument('id', type=unicode)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def _show_thing(ctx, id, turtle):
    g = ctx.obj['gw'].get_thing(id).to_graph()
    show_thing(g, format='text/turtle' if turtle else 'application/ld+json')


@show.command('ted-args')
@click.pass_obj
def show_ted_args(obj):
    td_roots = list(filter(lambda r: isinstance(r, TD), obj['ted'].ecosystem.roots))
    res = {}
    for td in td_roots:
        res[td.id] = list(obj['ted'].ecosystem.root_vars(td))

    click.echo(jsonify(res))


@show.command('config')
@click.pass_context
def show_config(ctx):
    click.echo(jsonify(load_config()))
