# OAtlas

`OAtlas` is an OSINT tool with 35+ functions to aid your investigations. It is the opensourced version of `Atlas` (hence open-atlas). `oatlas` can perform manual tool calling only which makes it very useful for industry experts who know what they're doing.

To know more about `atlas` on which this is based, refer to the [atlas](#atlas) section in the end.

## Installation

Installing `oatlas` is easy. Its written purely in python with some rust bindings for binwalk. Atlas will install all the necessary **external** dependencies by itself.

> Clone the repo

```sh
git clone https://github.com/FauvidoTechnologies/open-atlas.git
cd open-atlas/
```

> You need to install and use poetry for virtual enviornment mangement

```sh
pip install poetry
```
> Install all python dependencies using poetry

```sh
poetry install
```

And you're golden! For oatlas usage, refer the [usage](#usage) section.

## Usage

You will need the following API keys for all the functions to be available (set them in the `.env.private` file):

```
project_id=None
ip_info_token=None
perplexity_default_key=None
picarta_api_key=None
hibp-api-key=None
hunter_api_key=None
isgen_api_key=None
isgen_bearer=None
```

- The `project_id` is for a VertexAI project under which you have sufficient credits. We're slowly working towards an OpenAI port as well for all the functions that are currently using VertexAI.
- You will need a perplexity key for basic searches.
- A [hunter](https://hunter.io/) api key (you can use the free-tier ones or paid as per your choice) if you wish to use reverse-email lookups
- HIBP for HaveIBeenPwned searches
- [isgen](https://isgen.ai) is an AI image detection service. It can tell if images were altered/modified by the use of AI tools. We're working on support for getting these keys automatically through browser sessions (it looks like its possible!).
(You can choose to login and get these credentials by checkout out your POST request to the `/functions/v1/detect-image` endpoint, try it out its fun)

Below is an example to show all the functions supported for `oatlas`:

```sh
poetry run python3 oatlas.py --show-all-functions
```

Then you can choose any function to start the recursive engine (use `-v` for verbose mode):

```sh
poetry run python3 oatlas.py -f "<function-name>" -v
```

Once you finish running a function, `oatlas` will ask you if you want to run more functions and if yes, then choose which ones and run them.

### Web support

We're also working on a WebUI. It will be a while before its fully functional. To run the webUI use:

```sh
poetry run python3 oatlas.py --start-web-server
```

## Atlas

Atlas is a fully-automated (through AI) OSINT tool. It can do all your work for you. Watch a demo here -> [demo](https://drive.google.com/file/d/1foBa7mQOJqXcLsD4xpSen7tXMjR2nQ8R/view?usp=drive_link).
Contact me at [achintya.jai@owasp.org](mailto:achintya.jai@owasp.org) if you wish to know more!

## Acknowledgements

Thanks to [OWASP Nettacker](https://github.com/OWASP/Nettacker) for inspiring the code design!
