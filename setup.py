"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Ontology Engineering Group
        http://www.oeg-upm.net/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2017 Ontology Engineering Group.
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

from setuptools import setup, find_packages

__author__ = 'Fernando Serena'

with open("agora_cli/metadata.json", 'r') as stream:
    metadata = json.load(stream)

setup(
    name="agora-cli",
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['email'],
    description=metadata['description'],
    license="Apache 2",
    keywords=["agora", "discovery", "linked data"],
    url=metadata['github'],
    download_url="https://github.com/fserena/agora-cli/tarball/{}".format(metadata['version']),
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=['click', 'rdflib==4.2.1', 'SPARQLWrapper', 'pyld', 'rdflib-jsonld', 'shortuuid', 'agora-py',
                      'agora-wot', 'agora-gw', 'agora-graphql'],
    classifiers=[],
    include_package_data=True,
    package_dir={'agora_cli': 'agora_cli'},
    package_data={'agora_cli': ['metadata.json']},
    #scripts=['agora'],
    entry_points={
        'console_scripts': ['agora=agora_cli.root:cli']
    }

)