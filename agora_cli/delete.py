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

import json

import click
from agora import RedisCache
from agora.engine.utils.graph import get_triple_store
from agora_gw.data.repository import CORE
from rdflib import Graph, BNode, RDF, Literal

from agora_cli.root import cli
from agora_cli.utils import check_init, store_host_replacements, show_ted

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def delete(ctx):
    check_init(ctx)


@delete.command('extension')
@click.pass_context
@click.argument('name')
def delete_extension(ctx, name):
    gw = ctx.obj['gw']
    gw.delete_extension(name)


@delete.group('host')
@click.pass_context
def delete_host(ctx):
    pass


@delete_host.command('replacement')
@click.argument('base')
@click.pass_context
def delete_host_replacement(ctx, base):
    if base in ctx.obj['repls']:
        del ctx.obj['repls'][base]
        store_host_replacements(ctx.obj['repls'])


@delete.command('cache')
@click.pass_context
@click.option('--cache-file')
@click.option('--cache-host')
@click.option('--cache-port')
@click.option('--cache-db')
def delete_cache(ctx, cache_file, cache_host, cache_port, cache_db):
    remote_cache = all([cache_host, cache_port, cache_db])
    cache = RedisCache(redis_file=None if remote_cache else (cache_file or 'data.db'),
                       base='.agora/store',
                       path='',
                       redis_host=cache_host,
                       redis_db=cache_db,
                       redis_port=cache_port)
    cache.r.flushdb()
    g = get_triple_store(persist_mode=True, base='.agora/store/fragments')
    for c in g.contexts():
        g.remove_context(c)
    g.remove((None, None, None))


@delete.command('am')
@click.argument('id')
@click.argument('amid')
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def delete_access_mapping(ctx, id, amid, turtle):
    gw = ctx.obj['gw']

    td = gw.get_description(id)
    if not td:
        raise AttributeError('Unknown description: {}'.format(id))

    target_am = [am for am in td.access_mappings if str(am.id) == amid or am.endpoint.href.toPython() == amid]
    if not target_am:
        raise AttributeError('Unknown access mapping')

    target_am = target_am.pop()
    td.remove_access_mapping(target_am)
    g = td.to_graph(th_nodes={})

    ted = ctx.obj['gw'].add_description(g)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')
    click.echo(target_am.id)


@delete.command('mapping')
@click.argument('id')
@click.argument('mid')
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def delete_mapping(ctx, id, mid, turtle):
    gw = ctx.obj['gw']

    td = gw.get_description(id)
    if not td:
        raise AttributeError('Unknown description: {}'.format(id))

    target_m = None
    target_am = None
    for am in td.access_mappings:
        m = filter(lambda m: str(m.id) == mid, am.mappings)
        if m:
            target_m = m.pop()
            target_am = am
            break

    if not target_m:
        raise AttributeError('Unknown access mapping')

    target_am.mappings.remove(target_m)
    g = td.to_graph(th_nodes={})

    ted = ctx.obj['gw'].add_description(g)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')
    click.echo(target_m.id)


@delete.command('td')
@click.argument('id')
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def delete_description(ctx, id, turtle):
    gw = ctx.obj['gw']

    td = gw.get_description(id)
    if not td:
        raise AttributeError('Unknown description: {}'.format(id))

    ctx.obj['gw'].delete_description(id)
    #show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')
    click.echo(td.id)
