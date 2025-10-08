# OAtlas

**OAtlas** is an OSINT tool with 35+ functions to aid investigations. Imagine 

- **reverse email/username lookups**
- **GitHub secrets extraction**
- **reddit/instagram/twitter information extraction**
- **IP lookups**, **geolocation**
- **image metadata and exif extraction**
- **AI generated/tweaked image checker** 

etc. all combined into one tool!

`OAtlas` is designed for manual tool execution, making it ideal for industry experts who know exactly what they want to do. It also has a `plug-and-play` architecture which makes adding tools extremely easy. (refer to the `docs/` for more information on this)

It is a port of `Atlas` which is an upcoming fully automated OSINT tool. For more information about [Atlas](#atlas), refer to the section at the end.

If you need help obtaining API keys for certain functions, contact me at the email provided below. I can provide you with the necessary credentials.

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
```

> NOTE: All API keys are optional. Functions that don’t require them will work without issue.


- `project_id` - If you wish to use VertexAI for running any agent present in the architecture.
- `openai_api_key` - If you wish to use OpenAI models for running any agent present in the architecture.
- `perplexity_default_key` - Required for search-based functions. You can get free ones at [perplexity's website](https://www.perplexity.ai/help-center/en/articles/10352995-api-settings).
- `hunter_api_key` - Required for reverse-email lookups using [Hunter](https://hunter.io). Free-tier keys are sufficient.
- `hibp_api_key` - Required for `HaveIBeenPwned` searches, this only has paid subscriptions sadly!
- `isgen_api_key` & `isgen_bearer` - For AI image detection using [isgen](https://isgen.ai).

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

Atlas is a fully-automated (through AI) OSINT tool. It can do all your work for you.

Watch a demo here -> [demo](https://drive.google.com/file/d/1foBa7mQOJqXcLsD4xpSen7tXMjR2nQ8R/view?usp=drive_link).

Atlas supports two modes, `AA` and `SAR`. The `AA` mode is the one you're using right now. It just aggregates and analyses information. The `SAR` mode is fully automatic which makes its own plans, executes them, infers and continues from thereon.

PS: Most of the architecture that you see here is to support `atlas`!

> Contact me at [achintya.jai@owasp.org](mailto:achintya.jai@owasp.org) if you wish to know more!

## Acknowledgements

Thanks to [OWASP Nettacker](https://github.com/OWASP/Nettacker) for inspiring the code design!
