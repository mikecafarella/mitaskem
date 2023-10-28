# mitaskem


This repository contains the code and products produced by the MIT team as part of the DAPRA [Automating Scientific Knowledge Extraction and Modeling (ASKEM) project](https://www.darpa.mil/program/automating-scientific-knowledge-extraction-and-modeling).

The MIT team consists of (in alphabetical order):
- [Michael Cafarella](https://www.csail.mit.edu/person/michael-cafarella)
- [Peter Baile Chen](https://peterbaile.github.io/)
- [Wenjia He](https://web.eecs.umich.edu/~wenjiah/)
- [Chunwei Liu](https://people.csail.mit.edu/chunwei/)
- [Markos Markakis](https://people.csail.mit.edu/markakis/)
- [Oscar Moll](https://www.csail.mit.edu/person/oscar-ricardo-moll-thomae)
- [Theo Olausson](https://theoxo.xyz/)
- [Anna Zeng](https://people.csail.mit.edu/annazeng/)

## installing: 
`pip install -e .`

## developing and testing
From within mitaskm root:
`uvicorn --reload --reload-dir=./mitaskem/ mitaskem.api.server:app`

This will hot-reload the project as you change files.

## testing:
`pytest --nbmake --overwrite  ./demos/2023-07/*ipynb`
This will run the july scenarios


## Public API

Our functionality is provided via a public API available [here](http://3.83.68.208/). Many of the calls also require you to provide a GPT key, which you can obtain from [OpenAI](https://beta.openai.com/login/).

For examples of usage, you can refer to our most recent demo [here](https://github.com/mikecafarella/mitaskem/blob/d26ccfb57b3605e54dd0068510f18c9b19f0b599/demos/2023-02-01/mit-feb1-demo.ipynb).