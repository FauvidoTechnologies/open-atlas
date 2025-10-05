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

# We'll keep Nettacker's DIR serperate from the main one, including its paths
NETTACKER_PATH = PARENT_PATH / "tools/nettacker"

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

    Nettacker's database support

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
    name = str(PARENT_PATH / "data/atlas.db")
    host = ""
    port = ""
    username = ""
    password = ""
    journal_mode = "WAL"  # For APSW
    synchronous_mode = "NORMAL"  # For APSW
    ssl_mode = "disable"  # For PostgreSQL


# Some sensitive header fields for HTTP requests.
# Please edit this if you don't want your HTTP header to be present in the logs

# This is for Nettacker -> Its for a specific feature which we probably won't ever use but its there.
sensitive_headers = {
    "authorization",
    "proxy-authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "x-amz-security-token",
    "x-amz-credential",
    "x-amz-signature",
    "x-session-id",
    "x-csrf-token",
    "x-auth-token",
    "x-user-token",
    "x-id-token",
}


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


class NettackerConfig:
    """
    This is specifically for Nettacker systems -> Ensure to change the config path in its code

    # TODO:
    A lot of these shall be removed later! Cause they aren't being used!!
    """

    excluded_modules = None
    excluded_ports = None
    graph_name = "d3_tree_v2_graph"
    language = "en"
    parallel_module_scan = 1
    passwords = None
    passwords_list = None
    ping_before_scan = False
    ports = None
    profiles = None
    retries = 1
    scan_ip_range = False
    scan_subdomains = False
    selected_modules = None
    url_base_path = None
    http_header = None
    read_from_file = ""
    set_hardware_usage = "maximum"  # low, normal, high, maximum
    skip_service_discovery = False
    socks_proxy = None
    targets = None
    targets_list = None
    thread_per_host = 100
    time_sleep_between_requests = 0.0
    timeout = 3.0
    user_agent = "Nettacker {version_number} {version_code}".format(
        version_number=version_info()[0], version_code=version_info()[1]
    )
    usernames = None
    usernames_list = None
    verbose_event = False
    verbose_mode = False
    scan_compare_id = None
    compare_report_path_filename = ""
    max_retries = 3
    retry_delay = 0.1


class Files:
    user_agents_file = CWD / "oatlas/files/user_agents.txt"
    emails = CWD / "oatlas/files/emails.txt"
    banner_file = PARENT_PATH / "banner.txt"
    results_path = PARENT_PATH / "data"
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

    # Nettacker's configurations
    nettacker_data_dir = NETTACKER_PATH / ".nettacker/data"
    nettacker_database_file = NETTACKER_PATH / ".nettacker/data/nettacker.db"
    nettacker_locale_dir = NETTACKER_PATH / "locale"  # Gonna remove this later
    nettacker_module_protocols_dir = (
        NETTACKER_PATH / "core/lib"
    )  # Not sure if we're gonna use this
    nettacker_modules_dir = NETTACKER_PATH / "modules"
    nettacker_payloads_dir = NETTACKER_PATH / "lib/payloads"  # probably useful to have
    nettacker_tmp_dir = (
        NETTACKER_PATH / ".nettacker/data/tmp"
    )  # probably useful to have not sure...
    nettacker_cached_function_configs = NETTACKER_PATH / "nettacker_module_configs.json"


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


class API:
    reddit = Reddit()
    instagram = Instagram()
    ipinfo = IPinfo()
    perplexity = Perplexity()
    picarta = Picarta()
    github = GitHub()
    isgen = IsGen()


class Request:
    user_agents = UserAgents()


class Config:
    path = Files()
    settings = Settings()
    messages = Messages()
    web = WebConfig()
    API = API()
    nettacker = NettackerConfig()
