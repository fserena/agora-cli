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
from Queue import Empty, Queue
from datetime import datetime
from threading import Thread

import click
from agora import RedisCache
from agora.engine.utils import Semaphore
from rdflib import URIRef, BNode

from agora_cli.root import cli
from agora_cli.utils import split_arg, check_init

__author__ = 'Fernando Serena'


def head(row):
    return {'vars': list(row.labels)}


def value_type(value):
    if isinstance(value, URIRef):
        return 'uri'
    elif isinstance(value, BNode):
        return 'bnode'
    else:
        if value.datatype is not None:
            return 'typed-literal'
        return 'literal'


def result(row):
    def r_dict(l):
        value = row[l]
        type = value_type(value)
        value_p = value.toPython()
        if isinstance(value_p, datetime):
            value_p = str(value_p)
        res = {"type": type, "value": value_p}
        if 'literal' in type:
            if value.datatype:
                res['datatype'] = value.datatype.toPython()
            if value.language:
                res['xml:lang'] = str(value.language)
        return res

    return {l: r_dict(l) for l in row.labels if row[l] is not None}


def gen_thread(status, queue, gen):
    first = True
    try:
        for row in gen:
            if first:
                queue.put(u'{\n')
                queue.put(u'  "head": %s,\n  "results": {\n    "bindings": [\n' % json.dumps(head(row)))
                first = False
            else:
                queue.put(',\n')
            queue.put(u'      {}'.format(json.dumps(result(row), ensure_ascii=False)))
        if first:
            queue.put('{\n')
            queue.put('  "head": [],\n  "results": {\n    "bindings": []\n  }\n')
        else:
            queue.put('\n    ]\n  }\n')
        queue.put('}')
    except Exception, e:
        exception = e
        print e.message

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


@cli.command('query')
@click.argument('q')
@click.option('--arg', multiple=True)
@click.option('--incremental', is_flag=True, default=False)
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
def query(ctx, q, arg, incremental, ignore_cycles, cache_file, cache_host, cache_port, cache_db, resource_cache,
          fragment_cache, host, port):
    check_init(ctx)

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
    gen = dgw.query(q, incremental=incremental, stop_event=stop, scholar=fragment_cache, follow_cycles=not ignore_cycles,
                    **args)

    request_status = {
        'completed': False,
        'exception': None
    }
    stream_th = Thread(target=gen_thread, args=(request_status, queue, gen))
    stream_th.daemon = False
    stream_th.start()

    for chunk in gen_queue(request_status, stop, queue):
        click.echo(chunk, nl=False)

    click.echo()
