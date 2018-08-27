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
from agora_wot.blocks.utils import describe
from agora_wot.gateway import Gateway
from rdflib import Graph, URIRef, RDF, BNode

from agora_cli.root import cli
from agora_cli.utils import show_ted, check_init, store_host_replacements

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def learn(ctx):
    check_init(ctx)


@learn.command('extension')
@click.pass_context
@click.argument('name')
@click.argument('file', type=click.Path(exists=True))
def learn_extension(ctx, name, file):
    gw = ctx.obj['gw']
    with open(file, 'r') as f:
        g = Graph().parse(f, format='turtle')
    gw.add_extension(name, g)


@learn.command('descriptions')
@click.argument('file', type=click.Path(exists=True))
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def learn_descriptions(ctx, file, turtle):
    with open(file, 'r') as f:
        g = Graph().parse(f, format='turtle')
    ted = ctx.obj['gw'].add_description(g)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')


@learn.command('thing')
@click.argument('id')
@click.argument('file', type=click.Path(exists=True))
@click.option('--turtle', default=False, is_flag=True)
@click.pass_context
def learn_descriptions(ctx, id, file, turtle):
    gw = ctx.obj['gw']

    td = gw.get_description(id)
    if not td:
        raise AttributeError('Unknown description: {}'.format(id))

    g = td.to_graph()
    td.resource.to_graph(graph=g)

    with open(file, 'r') as f:
        lg = Graph().parse(f, format='turtle')

    for s, p, o in describe(lg, td.resource.node):
        g.add((s, p, o))

    rg = Graph()
    for prefix, uri in g.namespaces():
        rg.bind(prefix, uri)

    resource_node = td.resource.node
    td_node = BNode()
    th_node = BNode()
    for s, p, o in g:
        if s == td.node:
            s = td_node
        if o == td.node:
            o = td_node

        if s == resource_node:
            s = th_node
        if o == resource_node:
            o = th_node

        rg.add((s, p, o))

    ted = ctx.obj['gw'].add_description(rg)
    show_ted(ted, format='text/turtle' if turtle else 'application/ld+json')
