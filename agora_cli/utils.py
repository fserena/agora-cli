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
import os
import zipfile
import json
import logging

import click
from agora_gw.data.repository import CORE
from agora_gw.ecosystem.serialize import serialize_graph
from rdflib import URIRef, RDF
import os
import os.path as path

__author__ = 'Fernando Serena'


def split_arg(a):
    kv = tuple(a.split('='))
    if len(kv) == 1:
        kv = a, ''
    elif len(kv) > 2:
        kv = kv[:1]
    return kv


def show_ted(ted, format):
    g = ted.to_graph()
    ttl = serialize_graph(g, format, frame=CORE.ThingEcosystemDescription, skolem=False)
    click.echo(ttl)


def error(msg):
    click.echo('[FAIL]: ' + msg, err=True)


def show_td(td, format):
    g = td.to_graph()
    ttl = serialize_graph(g, format, frame=CORE.ThingDescription, skolem=False)
    click.echo(ttl)


def show_thing(g, format):
    th_node = g.identifier
    th_types = list(g.objects(URIRef(th_node), RDF.type))
    th_type = th_types.pop() if th_types else None
    ttl = serialize_graph(g, format, frame=th_type, skolem=False)
    click.echo(ttl)


def compress(path, out):
    def zipdir(ziph):
        for root, dirs, files in os.walk(path):
            for file in filter(lambda f: not f.endswith('.settings'), files):
                ziph.write(os.path.join(root, file))

    zipf = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    zipdir(zipf)
    zipf.close()


def extract(file):
    zipf = zipfile.ZipFile(file, 'r', zipfile.ZIP_DEFLATED)
    zipf.extractall()
    zipf.close()


def jsonify(obj):
    return json.dumps(obj, indent=3, sort_keys=True, ensure_ascii=False)


def store_config(**kwargs):
    host = kwargs['host']
    port = kwargs['port']
    if host and port:
        config = {
            'host': host,
            'port': port
        }
    else:
        remote_repo_cache = all([kwargs['repo_cache_host'], kwargs['repo_cache_db'], kwargs['repo_cache_port']])

        config = {
            "repository": {
                "extension_base": kwargs['extension_base'],
                "repository_base": kwargs['repository_base'],
                "data": {
                    "persist_mode": True,
                    "base": ".agora/store",
                    "path": "ted",
                    "sparql_host": kwargs['repo_sparql_host'],
                    "update_host": kwargs['repo_update_host'],
                    "cache": {
                        "file": None if remote_repo_cache else ".agora/store/ted/repo.db",
                        "host": kwargs['repo_cache_host'],
                        "port": kwargs['repo_cache_port'],
                        "db": kwargs['repo_cache_db']
                    }
                }
            },
            "engine": {
                "persist_mode": True,
                "base": ".agora/store",
                "path": "fountain",
                "redis_file": "fountain.db"
            }
        }

    with open('.agora/config', 'wb') as f:
        json.dump(config, f, indent=3)
    store_host_replacements({})


def load_config():
    if is_init():
        with open('.agora/config', 'r') as f:
            return json.load(f)


def check_init(ctx):
    if ctx.obj is None:
        click.echo('[FAIL] Agora is not initialized: ', nl=False)
        ctx.abort()


def is_init():
    return path.exists('.agora') and path.isdir('.agora') and path.exists('.agora/config')


def init_base():
    os.makedirs('.agora')


def mute_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.CRITICAL)
    ch = logging.StreamHandler()
    log.addHandler(ch)


def load_host_replacements():
    if is_init():
        with open('.agora/repls', 'r') as f:
            return json.load(f)


def store_host_replacements(repls):
    with open('.agora/repls', 'wb') as f:
        json.dump(repls, f, indent=3)
