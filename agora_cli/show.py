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
from agora_gw.gateway import NotFoundError, GatewayError

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
    try:
        g = gw.get_extension(name)
        click.echo(g.serialize(format='turtle'))
    except NotFoundError:
        error(u"The extension '{}' doesn't exist".format(name))


@show.command('prefixes')
@click.pass_context
def show_prefixes(ctx):
    gw = ctx.obj['gw']
    click.echo(jsonify(gw.agora.fountain.prefixes))


@show.command('type')
@click.pass_context
@click.argument('name')
def show_type(ctx, name):
    gw = ctx.obj['gw']
    try:
        click.echo(jsonify(gw.get_type(name)))
    except NotFoundError:
        error('There is no known type called "{}"'.format(name))


@show.command('property')
@click.pass_context
@click.argument('name')
def show_property(ctx, name):
    gw = ctx.obj['gw']
    try:
        click.echo(jsonify(gw.get_property(name)))
    except NotFoundError:
        error('There is no known property called "{}"'.format(name))


@show.command('paths')
@click.pass_context
@click.argument('source')
@click.argument('dest')
def show_paths(ctx, source, dest):
    gw = ctx.obj['gw']
    try:
        click.echo(jsonify(
            gw.agora.fountain.get_paths(dest,
                                        force_seed=[('<{}-uri>'.format(source.lower()).replace(':', '-'), source)])))
    except TypeError:
        error('Source and/or destination are unknown')


@show.command('ted')
@click.pass_context
@click.option('--turtle', default=False, is_flag=True)
def _show_ted(ctx, turtle):
    try:
        ted = ctx.obj['gw'].ted
        show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')
    except GatewayError as e:
        error(e.message)


@show.command('td')
@click.argument('id', type=unicode)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def _show_td(ctx, id, turtle):
    try:
        td = ctx.obj['gw'].get_description(id)
        show_td(td, format='text/turtle' if turtle else 'application/ld+json')
    except NotFoundError:
        error('There is no known TD identified as {}'.format(id))


@show.command('thing')
@click.argument('id', type=unicode)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def _show_thing(ctx, id, turtle):
    try:
        g = ctx.obj['gw'].get_thing(id).to_graph()
        show_thing(g, format='text/turtle' if turtle else 'application/ld+json')
    except NotFoundError:
        error('There is no known thing identified as {}'.format(id))


@show.command('args')
@click.pass_context
def show_args(ctx):
    args = ctx.obj['gw'].args
    click.echo(jsonify(args))


@show.command('config')
@click.pass_context
def show_config(ctx):
    click.echo(jsonify(load_config()))
