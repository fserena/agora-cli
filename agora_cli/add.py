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
from agora.engine.plan.agp import extend_uri
from agora_wot.blocks.endpoint import Endpoint
from agora_wot.blocks.td import TD, Mapping, AccessMapping, ResourceTransform
from agora_wot.gateway import Gateway
from rdflib import Graph, URIRef, RDF

from agora_cli.root import cli
from agora_cli.utils import show_ted, check_init, store_host_replacements, jsonify

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def add(ctx):
    check_init(ctx)


@add.command('thing')
@click.argument('uri')
@click.option('--type', multiple=True)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def add_thing(ctx, uri, type, turtle):
    gw = ctx.obj['gw']
    agora = gw.agora
    if not all([t in agora.fountain.types for t in type]):
        raise AttributeError('Unknown type')

    g = Graph()
    prefixes = agora.fountain.prefixes

    uri_ref = URIRef(uri)
    if not type:
        ted = gw.ted
        dgw = Gateway(gw.agora, ted, cache=None)
        rg, headers = dgw.loader(uri)

        type_uris = set([extend_uri(t, prefixes) for t in agora.fountain.types])

        resource_types = set(rg.objects(uri_ref, RDF.type))
        type = tuple(set.intersection(type_uris, resource_types))

    for t in type:
        g.add((uri_ref, RDF.type, URIRef(extend_uri(t, prefixes))))

    ted = ctx.obj['gw'].add_description(g)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')


@add.command('td')
@click.argument('id')
@click.option('--type', multiple=True)
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def add_td(ctx, id, type, turtle):
    gw = ctx.obj['gw']
    agora = gw.agora
    if not all([t in agora.fountain.types for t in type]):
        raise AttributeError('Unknown type')

    prefixes = agora.fountain.prefixes
    type_uris = [extend_uri(t, prefixes) for t in type]
    td = TD.from_types(types=type_uris, id=id)
    g = td.to_graph(th_nodes={})

    ted = ctx.obj['gw'].add_description(g)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')


@add.command('am')
@click.argument('id')
@click.argument('link')
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def add_access_mapping(ctx, id, link, turtle):
    gw = ctx.obj['gw']

    td = gw.get_description(id)
    if not td:
        raise AttributeError('Unknown description: {}'.format(id))

    endpoint_hrefs = map(lambda e: u'{}'.format(e.href), td.endpoints)
    if link in endpoint_hrefs:
        raise AttributeError('Link already mapped')

    e = Endpoint(href=link)
    am = AccessMapping(e)
    td.add_access_mapping(am)
    g = td.to_graph(th_nodes={})

    ted = ctx.obj['gw'].add_description(g)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')
    click.echo(am.id)


@add.command('mapping')
@click.argument('id')
@click.argument('amid')
@click.option('--predicate', required=True)
@click.option('--key', required=True)
@click.option('--jsonpath')
@click.option('--root', default=False, is_flag=True)
@click.option('--transformed-by')
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def add_mapping(ctx, id, amid, predicate, key, jsonpath, root, transformed_by, turtle):
    gw = ctx.obj['gw']

    td = gw.get_description(id)
    if not td:
        raise AttributeError('Unknown description: {}'.format(id))

    transform_td = None
    if transformed_by:
        transform_td = gw.get_description(transformed_by)

    target_am = [am for am in td.access_mappings if str(am.id) == amid or am.endpoint.href.toPython() == amid]
    if not target_am:
        raise AttributeError('Unknown access mapping')

    target_am = target_am.pop()

    m = Mapping(key=key, predicate=URIRef(extend_uri(predicate, gw.agora.fountain.prefixes)), root=root, path=jsonpath,
                transform=ResourceTransform(transform_td) if transform_td else None)
    target_am.mappings.add(m)
    g = td.to_graph(th_nodes={})

    ted = ctx.obj['gw'].add_description(g)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')
    click.echo(m.id)


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

