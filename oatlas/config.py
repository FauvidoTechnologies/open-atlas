import inspect
import os
import uuid
from functools import lru_cache
from pathlib import Path

from oatlas import version


def read_file(filename: str) -> str:
    """
    Returns a string form a file, a normal read operation
    Args:
        filename: Path to the file
    """
    with Path(filename).open() as file:
        return file.read()


HOME = Path.home()
CWD = Path.cwd()
PARENT_PATH = Path(__file__).parent

date_time_format = "%Y-%m-%d"  # For logging purposes


@lru_cache(maxsize=128)
def version_info():
    """
    version information of the framework

    Returns:
        an array of version and code name
    """

    return version.version


class ConfigBase:
    @classmethod
    def as_dict(cls):
        return {attr_name: getattr(cls, attr_name) for attr_name in cls()}

    def __init__(self) -> None:
        self.attributes = sorted(
            (
                attribute[0]
                for attribute in inspect.getmembers(self)
                if not attribute[0].startswith("_") and not inspect.ismethod(attribute[1])
            )
        )
        self.idx = 0

    def __iter__(self):
        yield from self.attributes


class Database(ConfigBase):
    """
    For SQLite (APSW) -> Default:
        engine: sqlite
        name: location for the database
        leave the journal and synchronous modes as defaults unless you know what you're doing

    For MySQL:
        engine: mysql
        name: name of the database
        username, password, host and port: as the server is configured (default port is 3306)

    For PostgreSQL:
        engine: postgres
        name: name of the database
        username, password, host and port: as the server is configured (default port is 5432)
        ssl_mode: "disable" if not using encryptions, and "require" if using encryption
    """

    engine = "sqlite"
    name = str(PARENT_PATH / "data/oatlas.db")
    host = ""
    port = ""
    username = ""
    password = ""
    journal_mode = "WAL"  # For APSW
    synchronous_mode = "NORMAL"  # For APSW
    ssl_mode = "disable"  # For PostgreSQL


class WebConfig:
    """
    Web configurations for the Atlas webserver, yet to implement some stuff here
    """

    api_access_key = uuid.uuid4().hex
    start_api_server = False

    app_name = "OAtlas"
    app_path = CWD / "oatlas/webserver/main.py"


class Settings:
    show_version = False
    show_help_menu = False
    location = "us-central1"  # Server location for VertexAI
    model = "gemini-2.5-pro"
    openai_model = "gpt-5"

    # Keys => These will be called using os.getenv().
    openai_api_key = "openai_api_key"  # The key used will be os.getenv("openai_api_key")
    gemini_api_key = "gemini_api_key"
    project_id = "project_id"
    vertexai = True  # I know it seems dumb to keep this here but we'll use it later when we port to different models as well
    timeout = 0.1
    paid_keys = None
    show_api_services = None
    show_all_functions = None
    # according to their benchmarks, this works very well for human images
    DeepFace_model_name = "GhostFaceNet"
    # Depending on what you want
    DeepFace_fast_backend = "opencv"
    DeepFace_accurate_backend = "retinaface"
    dom_tag_truncate_thershold = 100
    disposable_tags = ["script", "style", "meta", "link", "noscript"]
    useful_tags = ["a", "button", "input", "textarea", "select"]
    useful_attributes = [
        "id",
        "name",
        "type",
        "value",
        "placeholder",
        "aria-label",
        "role",
        "href",
    ]
    verbose_mode = False
    functions = None
    use_openai = False


class Files:
    user_agents_file = CWD / "oatlas/files/user_agents.txt"
    emails = CWD / "oatlas/files/emails.txt"
    banner_file = PARENT_PATH / "banner.txt"
    results_path = PARENT_PATH / "data"
    database_file = PARENT_PATH / "data/oatlas.db"
    instagram_scraped_dir = CWD / "oatlas/tools/reverse_instagram_lookup/utils/scraped"
    methods_path = CWD / "oatlas/methods/methods.yaml"
    trufflehog_rules = CWD / "oatlas/tools/github_apis/trufflehog/static/rules.yml"
    deepface_base_dir = HOME / ".deepface" / "weights"
    username_search_urls = CWD / "oatlas/tools/username_search/utils/data.json"
    binwalk_extracted_output_dir = results_path / "extraction_outputs"
    perplexity_text_output = PARENT_PATH / "utils/prompts/perpelxity_text_output.txt"
    APIListingStructure = PARENT_PATH / "utils/prompts/APIListingStructure.txt"
    PerplexitySystemInstruction = PARENT_PATH / "utils/prompts/PerplexitySystemInstruction.txt"
    GeolocateImageVertexAI = PARENT_PATH / "utils/prompts/GeolocateImageVertexAI.txt"


class Messages:
    """
    Special prompts for models
    """

    PERPLEXITY_SYSTEM_INSTRUCTION = read_file(Files.PerplexitySystemInstruction)


class Reddit:
    comments = "https://www.reddit.com/user/{0}/comments.json?limit={1}"
    about = "https://www.reddit.com/user/{0}/about.json"
    post_details = "https://www.reddit.com/r/{0}/comments/{1}.json"
    user_submissions = "https://www.reddit.com/user/{0}/submitted.json"

    # sort can be "hot|new|top|relevance", restrict_sr=true|false, t=all|day|week|month|year
    search_post_across_reddit = "https://www.reddit.com/search.json?q={q}&sort={sort}&limit={limit}&restrict_sr={restrict_sr}&t={t}&type={type}"
    search_post_across_subreddit = "https://www.reddit.com/r/{subreddit}/search.json?q={q}&sort={sort}&limit={limit}&restrict_sr={restrict_sr}&t={t}&type={type}"


class Instagram:
    base_url = "https://instagram.com/{username}"


class GitHub:
    about_url = "https://api.github.com/users/{username}"
    repos_url = "https://api.github.com/users/{username}/repos"


class Perplexity:
    endpoint_url = "https://api.perplexity.ai/chat/completions"
    default_perplexity_model = "sonar"
    search_perplexity_model_pro = "sonar-pro"
    default_pplx_reasoning_model = "sonar-reasoning"
    reasoning_pplx_model_pro = "sonar-reasoning-pro"
    deep_research_pplx_model = "sonar-deep-research"
    system_instruction = Messages.PERPLEXITY_SYSTEM_INSTRUCTION


class IPinfo:
    api_token = "ip_info_token"
    base_url = "https://api.ipinfo.io/lite/{ipaddress}?token={api_token}"  # For the free version, the code will escape as necessary
    core_api_token = "core_ip_info_token"  # This should be defined inside .env.private
    core_base_url_ipaddress = "https://api.ipinfo.io/lookup/{ipaddress}?token={api_token}"
    core_base_url_asn = "https://ipinfo.io/{ASN_number}?token={api_token}"


class Picarta:
    api_key = "picarta_api_key"
    url = "https://picarta.ai/classify"


class HIBP:
    url = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"


class Hunter:
    domain = "https://api.hunter.io/v2/domain-search?domain={domain_name}&api_key={hunter_api_key}"
    person_domain_email = "https://api.hunter.io/v2/email-finder?domain={domain_name}&first_name={person_first_name}&last_name={person_last_name}&api_key={hunter_api_key}"


class IsGen(ConfigBase):
    base_url = "https://isgen.ai"
    endpoint_url = (
        "https://api.isgen.ai/functions/v1/detect-image"  # For the API, we aren't using this
    )
    image_detection_url = "https://isgen.ai/ai-image-detector"
    api_key = os.getenv("isgen_api_key")  # This is a common JWT token -> can be found easily


class UserAgents:
    common_linux = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    instagram_ = "Mozilla/5.0"  # Do not use the full user-agent here because then insta will put you behind the login


class OathNet:
    base_url = "https://oathnet.org/api/service/"
    init_url = "https://oathnet.org/api/service/search/init"
    search_stealer_url = "https://oathnet.org/api/service/search-stealer/"
    search_breach_url = "https://oathnet.org/api/service/search-breach/"


class API:
    reddit = Reddit()
    instagram = Instagram()
    ipinfo = IPinfo()
    perplexity = Perplexity()
    picarta = Picarta()
    github = GitHub()
    isgen = IsGen()
    oathnet = OathNet()


class Request:
    user_agents = UserAgents()


class BA:
    # By default I am including all login sites which are coded in the library

    # default_login_sites = ["instagram", "facebook", "gmail"]
    default_login_sites = None  # We'll keep this at none. For setting the default you will have to edit your .env file.
    # Set the required usernames and passwords for the required login site in your .env file

    handle_dependencies = True

    class Database(ConfigBase):
        engine = "sqlite"  # This can be sqlite, postgres or mysql
        name = "/tmp/pyba.db"  # In case of postgres or mysql, change this to the database name
        username = ""
        password = ""
        host = ""
        port = ""
        ssl_mode = "disabled"  # Set to required if using postgres and want encrypted databases

    generate_code = False
    code_output_path = (
        "/tmp/pyba_script.py"  # Saving the automation script if using the generate_code feature
    )
    database_mode = False
    enable_tracing = False
    trace_save_directory = "/tmp/pyba/"
    headless = False  # Run Oatlas no-code browser automation in headless mode
    use_logger = True  # Start and use the pyba logger
    mode = None
    max_depth = 10
    max_breadth = 10


class Config:
    path = Files()
    settings = Settings()
    messages = Messages()
    web = WebConfig()
    API = API()
    browserautomations = BA()
