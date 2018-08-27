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
import logging

import click
from agora import setup_logging, Agora
from agora_gw import Gateway

from agora_cli.utils import load_config, mute_logger, load_host_replacements

__author__ = 'Fernando Serena'

mute_logger('jsonpath_ng')
mute_logger('rdflib')
mute_logger('agora')


@click.group()
@click.option('--debug', is_flag=True, default=False)
@click.version_option()
@click.pass_context
def cli(ctx, debug):
    config = load_config()
    if config is not None:
        if debug:
            setup_logging(logging.DEBUG)

        gw = Gateway(**config)
        ctx.call_on_close(lambda: Agora.close())
        ctx.obj = {'gw': gw, 'config': config, 'repls': load_host_replacements()}
