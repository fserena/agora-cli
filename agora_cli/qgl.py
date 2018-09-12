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
from agora_cli.utils import split_arg, check_init, jsonify
from agora_graphql.gql import GraphQLProcessor

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def gql(ctx):
    check_init(ctx)


@gql.command()
@click.argument('q')
@click.option('--schema-file', type=click.Path(exists=True))
# @click.option('--incremental', is_flag=True, default=False)
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
def query(ctx, q, schema_file, ignore_cycles, cache_file, cache_host, cache_port, cache_db, resource_cache, fragment_cache, host,
          port):
    check_init(ctx)

    q = q.replace("'", '"')
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

    ctx.obj['gw'].data_cache = cache
    processor = GraphQLProcessor(ctx.obj['gw'], schema_path=schema_file, scholar=fragment_cache, server_name=host,
                                 port=80, follow_cycles=not ignore_cycles, base='.agora/store/fragments')
    res = processor.query(q)
    click.echo(jsonify(res.to_dict()))
