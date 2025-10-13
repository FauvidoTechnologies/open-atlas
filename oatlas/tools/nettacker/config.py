import inspect
from pathlib import Path

NETTACKER_PATH = Path(__file__).parent


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

    #### Nettacker's database support

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
    name = str(NETTACKER_PATH / ".nettacker/nettacker.db")
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
    user_agent = "Nettacker 0.4.3 QUIN"
    usernames = None
    usernames_list = None
    verbose_event = False
    verbose_mode = False
    scan_compare_id = None
    compare_report_path_filename = ""
    max_retries = 3
    retry_delay = 0.1


class Files:
    # Nettacker's configurations
    nettacker_database_file = NETTACKER_PATH / ".nettacker/nettacker.db"
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


class Config:
    path = Files()
    nettacker = NettackerConfig()
