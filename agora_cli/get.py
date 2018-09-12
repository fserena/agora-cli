#!/usr/bin/env python
# coding=utf-8
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

from Queue import Queue, Empty
from datetime import datetime
from threading import Thread

import click
from agora import RedisCache
from agora.engine.plan.agp import extend_uri
from agora.engine.utils import Semaphore
from agora_graphql.gql.data import DataGraph
from agora_wot.gateway import Gateway
from rdflib import URIRef, RDF, Graph

from agora_cli.root import cli
from agora_cli.utils import show_thing, split_arg, check_init

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def get(ctx):
    check_init(ctx)


@get.command('resource')
@click.argument('uri')
@click.option('--host', default='agora')
@click.option('--port', default=80)
@click.option('--turtle', default=False, is_flag=True)
@click.option('--raw', default=False, is_flag=True)
@click.pass_context
def get_resource(ctx, uri, host, port, turtle, raw):
    gw = ctx.obj['gw']
    ted = gw.ted
    dgw = Gateway(gw.agora, ted, cache=None, port=port, server_name=host)
    g, headers = dgw.loader(uri)

    uri_ref = URIRef(uri)
    prefixes = gw.agora.fountain.prefixes
    type_uris = set([extend_uri(t, prefixes) for t in gw.agora.fountain.types])

    resource_types = set(g.objects(uri_ref, RDF.type))
    known_types = set.intersection(type_uris, resource_types)
    ag = Graph()
    for prefix, uri in prefixes.items():
        ag.bind(prefix, uri)

    if raw:
        ag.__iadd__(g)
    else:
        known_types_n3 = [t.n3(ag.namespace_manager) for t in known_types]
        known_props = reduce(lambda x, y: x.union(set(gw.agora.fountain.get_type(y)['properties'])), known_types_n3, set())
        known_props_uri = set([extend_uri(p, prefixes) for p in known_props])
        known_refs = reduce(lambda x, y: x.union(set(gw.agora.fountain.get_type(y)['refs'])), known_types_n3, set())
        known_refs_uri = set([extend_uri(p, prefixes) for p in known_refs])
        for (s, p, o) in g:
            if s == uri_ref and ((p == RDF.type and o in known_types) or p in known_props_uri):
                ag.add((s, p, o))
            if o == uri_ref and p in known_refs_uri:
                ag.add((s, p, o))

    show_thing(ag, format='text/turtle' if turtle else 'application/ld+json')


def gen_thread(status, queue, fragment):
    try:
        gen = fragment['generator']
        plan = fragment['plan']
        prefixes = fragment['prefixes']
        first = True
        best_mime = 'text/turtle'  # ''application/agora-quad'
        min_quads = '-min' in best_mime
        if best_mime.startswith('application/agora-quad'):
            for c, s, p, o in gen:
                if min_quads:
                    quad = u'{}·{}·{}·{}\n'.format(c, s.n3(plan.namespace_manager),
                                                   p.n3(plan.namespace_manager), o.n3(plan.namespace_manager))
                else:
                    quad = u'{}·{}·{}·{}\n'.format(c, s.n3(), p.n3(), o.n3())

                queue.put(quad)
        else:
            if first:
                for prefix, uri in prefixes.items():
                    queue.put('@prefix {}: <{}> .\n'.format(prefix, uri))
                queue.put('\n')
            for c, s, p, o in gen:
                triple = u'{} {} {} .\n'.format(s.n3(plan.namespace_manager),
                                                p.n3(plan.namespace_manager), o.n3(plan.namespace_manager))

                queue.put(triple)
    except Exception as e:
        status['exception'] = e

    status['completed'] = True


def gen_queue(status, stop_event, queue):
    with stop_event:
        while not status['completed'] or not queue.empty():
            status['last'] = datetime.now()
            try:
                for chunk in queue.get(timeout=1.0):
                    yield chunk
            except Empty:
                if not status['completed']:
                    pass
                elif status['exception']:
                    raise Exception(status['exception'].message)


@get.command()
@click.argument('q')
@click.option('--arg', multiple=True)
@click.option('--ignore-cycles', is_flag=True, default=False)
@click.option('--cache-file')
@click.option('--cache-host')
@click.option('--cache-port')
@click.option('--cache-db')
@click.option('--resource-cache', is_flag=True, default=False)
@click.option('--fragment-cache', is_flag=True, default=False)
@click.option('--host', default='agora')
@click.option('--port', default=80)
@click.pass_context
def fragment(ctx, q, arg, ignore_cycles, cache_file, cache_host, cache_port, cache_db, resource_cache, fragment_cache, host, port):
    args = dict(map(lambda a: split_arg(a), arg))
    if cache_file:
        path_parts = cache_file.split('/')
        cache_base = '/'.join(cache_file.split('/')[:-1])
        cache_file = path_parts[-1]

    if resource_cache or fragment_cache:
        remote_cache = all([cache_host, cache_port, cache_db])
        cache = RedisCache(redis_file=None if remote_cache else (cache_file or 'data.db'),
                           base='.agora/store' if not cache_file else cache_base,
                           path='',
                           redis_host=cache_host,
                           redis_db=cache_db,
                           redis_port=cache_port)
    else:
        cache = None
    stop = Semaphore()
    queue = Queue()

    dgw = ctx.obj['gw'].data(q, cache=cache, lazy=False, server_name=host, port=port, base='.agora/store/fragments')

    gen = dgw.fragment(q, stop_event=stop, scholar=fragment_cache, follow_cycles=not ignore_cycles, **args)
    request_status = {
        'completed': False,
        'exception': None
    }
    stream_th = Thread(target=gen_thread, args=(request_status, queue, gen))
    stream_th.daemon = False
    stream_th.start()

    for chunk in gen_queue(request_status, stop, queue):
        click.echo(chunk, nl=False)
