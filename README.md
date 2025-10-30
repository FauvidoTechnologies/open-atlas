# OAtlas

**OAtlas** is an OSINT tool with 35+ functions to aid investigations. Imagine 

- **reverse email/username lookups**
- **no-code browser automations**
- **GitHub secrets extraction**
- **reddit/instagram/twitter information extraction**
- **IP lookups**, **geolocation**
- **image metadata and exif extraction**
- **AI generated/tweaked image checker** 

etc. all combined into one tool!

> [!IMPORTANT]
> We have created a library for fully no-code exploratory browser automations which we are using with oatlas!

Check out no-code browser automation using an OpenAI or VertexAI key with `-f run_automated_browser_instance`. Also look at [pyba](https://github.com/FauvidoTechnologies/PyBrowserAutomation/) if you're interested in no-code automations.

## Features

1. `Variety of functions` at your disposal -> You can run Social media OSINT, image geolocations, web-domain enumerations, binary analysis, all from just one tool!
2. `Looped execution` of functions -> Quickly run one, get an output, analyse it and run another
3. `Plug-and-play` architecture -> Need some specific tool you must have? Add it to the cycle in under 5 mins. Read the [docs](./docs/adding_new_tools.md)!
4. `Save logs` in a database -> Every function and every output is saved in a database. It supports `sqlite`, `mysql` and `postgresql` as of now. This makes report making easier.
5. `Installs its dependencies` on its own -> Its very easy to setup, all you need to do is follow the instructions (which are just 2, clone and install), everything else will be handled for.

## All available tools

For all the tools available currently, checkout the [tools section](./oatlas/tools/README.md)

## About Atlas

`OAtlas` is a port of `Atlas` which is an upcoming **fully automated** OSINT tool. For more information about [Atlas](#atlas), refer to the section at the end.

## Installation

`OAtlas` is written in Python, with some Rust bindings for binwalk. The tool will automatically install all required external dependencies.

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
make maturin-develop # If you wish to run binwalk
```

And you're golden! For oatlas usage, refer the [usage](#usage) section.

> Note that `oatlas` will work only on linux and darwin systems for now. It hasn't been tested on freebsd or windows or others yet.

## Usage

> If you need help obtaining API keys for certain functions, contact me at the email provided below. I can provide you with the necessary credentials.

Some functions require API keys. Place them in the `.env.private` file:

```
project_id=None
openai_api_key=None
ip_info_token=None
perplexity_default_key=None
picarta_api_key=None
hibp-api-key=None
hunter_api_key=None
isgen_api_key=None
isgen_bearer=None
oathnet_api_key=None
```

> NOTE: All API keys are optional. Functions that don’t require them will work without issue.


- `project_id` - If you wish to use VertexAI for running any agent present in the architecture.
- `openai_api_key` - If you wish to use OpenAI models for running any agent present in the architecture.
- `perplexity_default_key` - Required for search-based functions. You can get free ones at [perplexity's website](https://www.perplexity.ai/help-center/en/articles/10352995-api-settings).
- `hunter_api_key` - Required for reverse-email lookups using [Hunter](https://hunter.io). Free-tier keys are sufficient.
- `hibp_api_key` - Required for `HaveIBeenPwned` searches, this only has paid subscriptions sadly!
- `isgen_api_key` & `isgen_bearer` - For AI image detection using [isgen](https://isgen.ai).
- `oathnet_api_kee` - For getting data from breaches -> This uses the OathNet API service for retrieving this data. Its a [paid software however](https://oathnet.org/pricing)!

> NOTE: You will require LLMs if you wish to run functions like for geolocation, you will need either one of the two API keys

--

#### Finding isgen API and auth keys

> The bearer token contains some PII and expires quickly. To obtain the API key and bearer token:

1. Go to https://isgen.ai/ai-image-detector.
2. Login (bearer tokens differ for logged-in vs. logged-out users). For more information, read [this document](./docs/isgen_mystery.md) and see if you can help!
3. Upload any image.
4. Open your browser's Inspect tool → `Network` tab.
5. Click the Upload button and observe requests, particularly to:
```
	https://api.isgen.ai/functions/v1/detect-image
```
6. You will see the bearer token and API key in the request headers.

> Note: The bearer token is temporary. You may need to generate a fresh one for each session.

> [!TIP]
> The recommended approach to this is to let OAtlas install playwright browsers during the start and run AI image detections using that


#### Listing functions

Below is an example to show all the functions supported for `oatlas`:

```sh
poetry run python3 oatlas.py --show-all-functions
```

To get a list of all the APIs that `oatlas` is using:

```sh
poetry run python3 oatlas.py --show-api-services
```

Then you can choose any function to start the recursive engine (use `-v` for verbose mode):

```sh
poetry run python3 oatlas.py -f "<function-name>" -v
```

Once you finish running a function, `oatlas` will ask you if you want to run more functions and if yes, then choose which ones and run them.

You can enable OpenAI models using the `-o` flag:

```sh
poetry run python3 oatlas.py -f "<function-name-that-uses-LLMs>" -v -o
```

### Web support

We're also working on a WebUI. It will be a while before its fully functional. To run the webUI use:

```sh
poetry run python3 oatlas.py --start-web-server
```

## Atlas

Atlas is a fully-automated (through AI) OSINT tool. Its still under development. It can do all the grunt work for you, for example, doing a full analysis on a target, displaying and saving logs, making a report and more. 

> [!IMPORTANT]
> It also sports a server, so your team can launch one locally, start multiple scans, take a coffee break and viola a few minutes later all the hardwork of trail-and-error has been done for you. Your team can now focus on the more harder parts of the investigation!

Watch a demo here -> [demo](https://drive.google.com/file/d/1foBa7mQOJqXcLsD4xpSen7tXMjR2nQ8R/view?usp=drive_link).

Atlas supports two modes, `AA` and `SAR`. The `AA` mode is the one you're using right now. It just aggregates and analyses information. The `SAR` mode is fully automatic which makes its own plans, executes them, infers and continues from thereon.

PS: Most of the architecture that you see here is to support `atlas`!

> Contact me at [achintya.jai@owasp.org](mailto:achintya.jai@owasp.org) if you wish to know more!

## Acknowledgements

Thanks to [OWASP Nettacker](https://github.com/OWASP/Nettacker) for inspiring the code design!
