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
from agora_graphql.gql import GraphQLProcessor

from agora_cli.root import cli
from agora_cli.utils import split_arg, check_init

__author__ = 'Fernando Serena'


@cli.group()
@click.pass_context
def compute(ctx):
    check_init(ctx)


@compute.command('search-plan')
@click.pass_context
@click.argument('query')
@click.option('--arg', multiple=True)
def search_plan(ctx, query, arg):
    args = dict(map(lambda a: split_arg(a), arg))
    gw = ctx.obj['gw']
    res = gw.fragment(query, **args)
    plan = res['plan']
    click.echo(plan.serialize(format='turtle'))


@compute.command('gql-schema')
@click.pass_context
def show_gql_schema(ctx):
    processor = GraphQLProcessor(ctx.obj['gw'])
    click.echo(processor.schema_text)
