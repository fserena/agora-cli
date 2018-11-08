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
from agora_gw.gateway import GatewayError, ConflictError, NotFoundError

from agora_cli.root import cli
from agora_cli.utils import check_init, store_host_replacements, jsonify, error, show_thing

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def add(ctx):
    check_init(ctx)


@add.command('resource')
@click.argument('uri')
@click.option('--type', multiple=True)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def add_resource(ctx, uri, type, turtle):
    gw = ctx.obj['gw']
    try:
        r = gw.add_resource(uri, type)
        show_thing(r.to_graph(), format='text/turtle' if turtle else 'application/ld+json')
    except ConflictError:
        error('The seed URI "{}" is already added'.format(uri))
    except GatewayError as e:
        error(e.message)


@add.command('td')
@click.argument('id')
@click.option('--type', multiple=True)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def add_td(ctx, id, type, turtle):
    gw = ctx.obj['gw']
    try:
        td = gw.add_description(id, type)
        show_thing(td.to_graph(), format='text/turtle' if turtle else 'application/ld+json')
    except ConflictError:
        error('A TD called "{}" is already added'.format(id))
    except GatewayError as e:
        error(e.message)


@add.command('am')
@click.argument('id')
@click.argument('link')
@click.pass_context
def add_access_mapping(ctx, id, link):
    gw = ctx.obj['gw']
    try:
        am = gw.add_access_mapping(id, link)
        click.echo(am.id)
    except NotFoundError:
        error('There is not TD called {}'.format(id))
    except ConflictError as e:
        error('Conflict with {}'.format(e.message))
    except GatewayError as e:
        error(e.message)


@add.command('mapping')
@click.argument('id')
@click.argument('amid')
@click.option('--predicate', required=True)
@click.option('--key', required=True)
@click.option('--jsonpath')
@click.option('--root', default=False, is_flag=True)
@click.option('--transformed-by')
@click.pass_context
def add_mapping(ctx, id, amid, predicate, key, jsonpath, root, transformed_by):
    gw = ctx.obj['gw']
    try:
        m = gw.add_mapping(id, amid, predicate, key, jsonpath, root, transformed_by)
        click.echo(m.id)
    except NotFoundError as e:
        error('The entity {} does not exist'.format(e.message))
    except ConflictError as e:
        error('Conflict with {}'.format(e.message))
    except GatewayError as e:
        error(e.message)


@add.group('host')
@click.pass_context
def add_host(ctx):
    pass


@add_host.command('replacement')
@click.argument('base')
@click.argument('replace')
@click.pass_context
def add_host_replacement(ctx, base, replace):
    ctx.obj['repls'][base] = replace
    store_host_replacements(ctx.obj['repls'])


@add.command('prefix')
@click.argument('prefix')
@click.argument('ns')
@click.pass_context
def add_prefix(ctx, prefix, ns):
    gw = ctx.obj['gw']
    gw.agora.fountain.add_prefixes({prefix: ns})
    print jsonify(gw.agora.fountain.prefixes)
