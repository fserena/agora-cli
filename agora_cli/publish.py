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
from agora import RedisCache
from agora.server.fountain import build as fs
from agora.server.fragment import build as frs
from agora.server.planner import build as ps
from agora.server.sparql import build as ss
from agora_graphql.gql import GraphQLProcessor
from agora_graphql.server import AgoraGraphQLView
from agora_graphql.server.app import Application as GQLApplication
from agora_gw.server.app import Application
from agora_gw.server.worker import number_of_workers
from agora_wot.gateway import Gateway
from flask import Flask
from flask_cors import CORS

from agora_cli.root import cli
from agora_cli.utils import check_init

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def publish(ctx):
    check_init(ctx)


@publish.command('ecosystem')
@click.pass_context
@click.option('--query', required=True)
@click.option('--host', default='localhost')
@click.option('--port', default=5000)
@click.option('--cache-file')
def publish_ecosystem(ctx, query, host, port, cache_file):
    if cache_file:
        cache = RedisCache(redis_file=cache_file)
    else:
        cache = None
    ted = ctx.obj['gw'].discover(query, lazy=False)
    dgw = Gateway(ctx.obj['gw'].agora, ted, cache=cache, port=port, server_name=host)
    dgw.server.gw.config['ENV'] = 'development'

    dgw.server.gw.run(host='0.0.0.0', port=port, threaded=True)


@publish.command('gw')
@click.pass_context
@click.option('--port', default=8000)
def publish_gateway(ctx, port):
    try:
        options = {
            'bind': '%s:%s' % ('0.0.0.0', str(port)),
            'workers': number_of_workers(),
            'workerconnections': 1000,
            'timeout': 300,
            'errorlog': '-',
            'accesslog': '-',
            'gw': ctx.obj['gw'].eco
        }
        Application(options).run()
    except (KeyboardInterrupt, SystemExit, SystemError):
        pass


@publish.command('fountain')
@click.pass_context
@click.option('--port', default=5000)
def publish_fountain(ctx, port):
    fountain = ctx.obj['gw'].agora.fountain
    server = fs(fountain)
    server.run(host='0.0.0.0', port=port, threaded=True)


@publish.command('planner')
@click.pass_context
@click.option('--port', default=5000)
def publish_planner(ctx, port):
    planner = ctx.obj['gw'].agora.planner
    server = ps(planner)
    server.run(host='0.0.0.0', port=port, threaded=True)


def query_f(dgw, incremental, scholar, ignore_cycles):
    def wrapper(*args, **kwargs):
        kwargs['incremental'] = incremental
        kwargs['scholar'] = scholar
        kwargs['follow_cycles'] = not ignore_cycles
        return dgw.query(*args, **kwargs)

    return wrapper


@publish.command('sparql')
@click.option('--query', required=True)
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
def publish_sparql(ctx, query, incremental, ignore_cycles, cache_file, cache_host, cache_port, cache_db, resource_cache,
                   fragment_cache,
                   host,
                   port):
    check_init(ctx)

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

    click.echo('Discovering ecosystem...', nl=False)
    dgw = ctx.obj['gw'].data(query, cache=cache, lazy=False, server_name=host, port=port, base='.agora/store/fragments')
    click.echo('Done')

    server = ss(ctx.obj['gw'].agora, query_function=query_f(dgw, incremental, fragment_cache, ignore_cycles))
    server.run(host='0.0.0.0', port=port, threaded=True)
    click.echo()


def fragment_f(dgw, scholar, ignore_cycles):
    def wrapper(*args, **kwargs):
        kwargs['scholar'] = scholar
        kwargs['follow_cycles'] = not ignore_cycles
        return dgw.fragment(*args, **kwargs)

    return wrapper


@publish.command('fragment')
@click.option('--query', required=True)
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
def publish_fragment(ctx, query, ignore_cycles, cache_file, cache_host, cache_port, cache_db, resource_cache,
                     fragment_cache, host,
                     port):
    check_init(ctx)

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

    click.echo('Preparing...', nl=False)
    dgw = ctx.obj['gw'].data(query, cache=cache, lazy=False, server_name=host, port=port, base='.agora/store/fragments')
    click.echo('Ready')

    server = frs(ctx.obj['gw'].agora, fragment_function=fragment_f(dgw, fragment_cache, ignore_cycles))
    server.run(host='0.0.0.0', port=port, threaded=True)
    click.echo()


@publish.command('ui')
@click.option('--query', required=True)
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
def publish_ui(ctx, query, incremental, ignore_cycles, cache_file, cache_host, cache_port, cache_db, resource_cache,
               fragment_cache,
               host,
               port):
    check_init(ctx)

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

    click.echo('Discovering ecosystem...', nl=False)
    dgw = ctx.obj['gw'].data(query, cache=cache, lazy=False, server_name=host, port=80, base='.agora/store/fragments')
    click.echo('Done')

    server = fs(ctx.obj['gw'].agora.fountain)
    frs(ctx.obj['gw'].agora, server=server, fragment_function=fragment_f(dgw, fragment_cache, ignore_cycles))
    ss(ctx.obj['gw'].agora, server=server, query_function=query_f(dgw, incremental, fragment_cache, ignore_cycles))
    server.run(host='0.0.0.0', port=port, threaded=True)
    click.echo()


@publish.command('gql')
@click.option('--schema-file')
@click.option('--ignore-cycles', is_flag=True, default=False)
@click.option('--cache-file')
@click.option('--cache-host')
@click.option('--cache-port')
@click.option('--cache-db')
@click.option('--resource-cache', is_flag=True, default=False)
@click.option('--fragment-cache', is_flag=True, default=False)
@click.option('--age-gql-cache', type=int, default=300)
@click.option('--len-gql-cache', type=int, default=1000000)
@click.option('--host', default='agora')
@click.option('--port', default=80)
@click.pass_context
def publish_gql(ctx, schema_file, ignore_cycles, cache_file, cache_host, cache_port, cache_db, resource_cache,
                fragment_cache, age_gql_cache, len_gql_cache, host, port):
    check_init(ctx)

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

    app = Flask(__name__)
    CORS(app)

    ctx.obj['gw'].data_cache = cache
    gql_processor = GraphQLProcessor(ctx.obj['gw'], schema_path=schema_file, scholar=fragment_cache, server_name=host,
                                     port=80, follow_cycles=not ignore_cycles, base='.agora/store/fragments',
                                     data_gw_cache={'max_age_seconds': age_gql_cache, 'max_len': len_gql_cache})

    app.add_url_rule('/graphql',
                     view_func=AgoraGraphQLView.as_view('graphql', schema=gql_processor.schema,
                                                        executor=gql_processor.executor,
                                                        middleware=gql_processor.middleware,
                                                        graphiql=True))

    options = {
        'bind': '%s:%s' % ('0.0.0.0', str(port)),
        'workers': 1,
        'threads': number_of_workers(),
        'workerconnections': 1000,
        'timeout': 4000,
        'workerclass': 'gthread',
        'errorlog': '-',
        'accesslog': '-'
    }
    GQLApplication(app, options).run()
