from google.genai.types import FunctionDeclaration

from oatlas.config import Config
from oatlas.utils.common import nettacker_module_names
from oatlas.utils.tool_descriptions import FunctionTools

known_reddit_function_1 = FunctionDeclaration(
    name="fetch_comments",
    description=FunctionTools.KnownRedditFunctions.fetch_comments,
    parameters={
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "The reddit username"},
            "limit": {
                "type": "number",
                "description": "The number of comments to fetch, starting from most recent ones",
                "default": 25,
            },
        },
        "required": ["username"],
    },
)

known_reddit_function_2 = FunctionDeclaration(
    name="fetch_about",
    description=FunctionTools.KnownRedditFunctions.fetch_about,
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "The reddit username to learn more about",
            },
        },
        "required": ["username"],
    },
)

known_reddit_function_3 = FunctionDeclaration(
    name="fetch_user_posts",
    description=FunctionTools.KnownRedditFunctions.fetch_user_posts,
    parameters={
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "The username to fetch the posts from"},
        },
        "required": ["username"],
    },
)

unknown_reddit_function_1 = FunctionDeclaration(
    name="search_reddit_posts",
    description=FunctionTools.UnknownRedditFunctions.search_reddit_posts,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The keywords for searching through reddit posts and filtering them",
            },
            "subreddit": {
                "type": "string",
                "description": "The subreddit to restrict the search to",
                "default": None,
            },
            "t": {
                "type": "string",
                "description": "Time filtering for results. This specifies how far back do you want to search the posts from",
                "enum": ["hour", "day", "week", "month", "year", "all"],
                "default": "all",
            },
            "limit": {
                "type": "number",
                "description": "The number of posts to return",
                "default": 25,
            },
            "sort": {
                "type": "string",
                "description": "Specify the kind of posts. We sort with new if we have relevance in general",
                "enum": ["relevance", "hot", "top", "new", "comments"],
                "default": "relevance",
            },
            "restrict_sr": {
                "type": "string",
                "description": "This tells if we want to restrict to a subreddit while searching for posts",
                "enum": ["true", "false"],
                "default": "true",
            },
            "type": {
                "type": "string",
                "description": "",
                "enum": ["link", "sr", "user"],
                "default": "link",
            },
        },
        "required": ["query"],
    },
)

unknown_reddit_function_2 = FunctionDeclaration(
    name="fetch_post_details",
    description=FunctionTools.UnknownRedditFunctions.fetch_post_details,
    parameters={
        "type": "object",
        "properties": {
            "post_id": {
                "type": "string",
                "description": "The post_id for the post you want more information about",
            },
            "subreddit": {
                "type": "string",
                "description": "The subreddit to restrict the search to",
                "default": None,
            },
        },
        "required": ["post_id", "subreddit"],
    },
)

email_check_function = FunctionDeclaration(
    name="verify_email_address",
    description=FunctionTools.VerifyEmailFunctions.verify_email_address,
    parameters={
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address that you want to verify",
            }
        },
        "required": ["email"],
    },
)

static_image_analysis_function_1 = FunctionDeclaration(
    name="extract_metadata",
    description=FunctionTools.StaticImageExtraction.extract_metadata,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "The full path to the image. This will be present in the state",
            }
        },
        "required": ["image_path"],
    },
)


static_image_analysis_function_2 = FunctionDeclaration(
    name="scan_firmware",
    description=FunctionTools.StaticImageExtraction.scan_firmware,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "The file path to the file you want to scan",
            }
        },
        "required": ["image_path"],
    },
)

static_image_analysis_function_3 = FunctionDeclaration(
    name="extract_firmware",
    description=FunctionTools.StaticImageExtraction.extract_firmware,
    parameters={
        "type": "object",
        "properties": {
            "input_path": {
                "type": "string",
                "description": "The file path to the file you want to extract bytes from",
            },
            "skip": {
                "type": "number",
                "description": "The number of blocks to skip in the binary before copying",
            },
            "count": {
                "type": "number",
                "description": "The number of blocks to copy which are of 1 byte each by default",
            },
            "output_file_name": {"type": "string", "description": "The name of the output file"},
            "block_size": {
                "type": "number",
                "description": "The block size, usually set to 1 for targeted extraction",
            },
        },
        "required": ["input_path", "skip", "count", "output_file_name"],
    },
)

static_image_analysis_function_4 = FunctionDeclaration(
    name="extract_strings",
    description=FunctionTools.StaticImageExtraction.extract_strings,
    parameters={
        "type": "object",
        "properties": {
            "input_path": {
                "type": "string",
                "description": "The file path to the file you want to extract the ASCII strings from",
            },
            "min_length": {
                "type": "number",
                "description": "The minimum length of bytes that must be present in a valid sequence",
            },
        },
        "required": ["input_path"],
    },
)

active_image_analysis_function_1 = FunctionDeclaration(
    name="verify_similar_faces",
    description=FunctionTools.DeepScanEngine.verify_similar_faces,
    parameters={
        "type": "object",
        "properties": {
            "image_path_1": {
                "type": "string",
                "description": "Image path for the first image",
            },
            "image_path_2": {"type": "string", "description": "Image path for the second image"},
        },
        "required": ["image_path_1", "image_path_2"],
    },
)

active_image_analysis_function_2 = FunctionDeclaration(
    name="face_attribute_analysis",
    description=FunctionTools.DeepScanEngine.face_attribute_analysis,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the image file",
            }
        },
        "required": ["image_path"],
    },
)

active_image_analysis_function_3 = FunctionDeclaration(
    name="OCR_analysis",
    description=FunctionTools.DeepScanEngine.OCR_analysis,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the image file for which you want to extract the text of",
            }
        },
        "required": ["image_path"],
    },
)

image_geolocation_function_1 = FunctionDeclaration(
    name="geolocate_local_image",
    description=FunctionTools.ImageGeolocationEngine.geolocate_local_image,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the local image file for which you want to do geolocation for",
            },
            "top_k": {
                "type": "number",
                "description": "The top 'k' location matches to return, default at 10, can go upto 100",
                "default": 10,
            },
            "country_code": {
                "type": "string",
                "description": "This is a 2-letter (e.g., 'US', 'FR'', 'DE') country code to narrow down the search. If unsure about the country, a worldwide search can be perform by using the default value of None",
                "default": None,
            },
            "center_latitude": {
                "type": "number",
                "description": "The latitute for the central point of the location if its known. If this is unsure, then use the default value of None for a worldwide search",
                "default": None,
            },
            "center_longitude": {
                "type": "number",
                "description": "The longitude for the central point of the location if its known. If this is unsure, then use the default value of None for a worldwide search",
                "default": None,
            },
            "radius": {
                "type": "number",
                "description": "The radius from the centeral point to search within. This is in Kilometers. If this is unsure, then use the default value of None",
                "default": None,
            },
        },
        "required": ["image_path"],
    },
)

image_geolocation_function_2 = FunctionDeclaration(
    name="geolocate_online_image",
    description=FunctionTools.ImageGeolocationEngine.geolocate_online_image,
    parameters={
        "type": "object",
        "properties": {
            "image_url": {
                "type": "string",
                "description": "The online image URL for which geolocation needs to be performed",
            },
            "top_k": {
                "type": "number",
                "description": "The top 'k' location matches to return, default at 10, can go upto 100",
                "default": 10,
            },
            "country_code": {
                "type": "string",
                "description": "This is a 2-letter (e.g., 'US', 'FR'', 'DE') country code to narrow down the search. If unsure about the country, a worldwide search can be perform by using the default value of None",
                "default": None,
            },
            "center_latitude": {
                "type": "number",
                "description": "The latitude for the central point of the location if its known. If this is unsure, then use the default value of None for a worldwide search",
                "default": None,
            },
            "center_longitude": {
                "type": "number",
                "description": "The longitude for the central point of the location if its known. If this is unsure, then use the default value of None for a worldwide search",
                "default": None,
            },
            "radius": {
                "type": "number",
                "description": "The radius from the central point to search within. This is in Kilometers. If this is unsure, then use the default value of None",
                "default": None,
            },
        },
        "required": ["image_url"],
    },
)

image_geolocation_function_3 = FunctionDeclaration(
    name="geolocate_using_LLMs",
    description=FunctionTools.ImageGeolocationEngine.geolocate_using_LLMs,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "The image path for which geolocation using vertexai needs to be performed",
            },
            "prompt": {
                "type": "string",
                "description": "Short information stub if any information is known about the image to guide the model",
                "default": None,
            },
        },
        "required": ["image_path"],
    },
)

image_geolocation_function_4 = FunctionDeclaration(
    name="combined_llm_deeplearning_analysis",
    description=FunctionTools.ImageGeolocationEngine.combined_llm_deeplearning_analysis,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the local image file for which you want to do geolocation for",
            },
            "top_k": {
                "type": "number",
                "description": "The top 'k' location matches to return, default at 10, can go upto 100",
                "default": 10,
            },
            "country_code": {
                "type": "string",
                "description": "This is a 2-letter (e.g., 'US', 'FR'', 'DE') country code to narrow down the search. If unsure about the country, a worldwide search can be perform by using the default value of None",
                "default": None,
            },
            "center_latitude": {
                "type": "number",
                "description": "The latitude for the central point of the location if its known. If this is unsure, then use the default value of None for a worldwide search",
                "default": None,
            },
            "center_longitude": {
                "type": "number",
                "description": "The longitude for the central point of the location if its known. If this is unsure, then use the default value of None for a worldwide search",
                "default": None,
            },
            "radius": {
                "type": "number",
                "description": "The radius from the central point to search within. This is in Kilometers. If this is unsure, then use the default value of None",
                "default": None,
            },
            "prompt": {
                "type": "string",
                "description": "Short information stub if any information is known about the image to guide the model",
                "default": None,
            },
        },
        "required": ["image_path"],
    },
)

instagram_engine_function_1 = FunctionDeclaration(
    name="fetch_account_information",
    description=FunctionTools.InstagramEngine.fetch_account_information,
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "The instagram username to fetch the basic information about",
            }
        },
        "required": ["username"],
    },
)

instagram_engine_function_2 = FunctionDeclaration(
    name="fetch_public_account_posts",
    description=FunctionTools.InstagramEngine.fetch_public_account_posts,
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "The instagram username to fetch detailed information using browser automations",
            }
        },
        "required": ["username"],
    },
)

ipinfo_engine_function_1 = FunctionDeclaration(
    name="basic_ip_lookup",
    description=FunctionTools.IPinfoEngine.basic_ip_lookup,
    parameters={
        "type": "object",
        "properties": {
            "ipaddress": {
                "type": "string",
                "description": "The IPaddress that needs to be scanned",
            }
        },
        "required": ["ipaddress"],
    },
)

ipinfo_engine_function_2 = FunctionDeclaration(
    name="core_api_lookups",
    description=FunctionTools.IPinfoEngine.core_api_lookups,
    parameters={
        "type": "object",
        "properties": {
            "ipaddress": {
                "type": "string",
                "description": "The IPaddress that needs to be scanned",
            }
        },
        "required": ["ipaddress"],
    },
)

ipinfo_engine_function_3 = FunctionDeclaration(
    name="core_api_lookups_asn",
    description=FunctionTools.IPinfoEngine.core_api_lookups_asn,
    parameters={
        "type": "object",
        "properties": {
            "asn_number": {
                "type": "string",
                "description": "The ASN (Autonomous System Number) to be scanned",
            }
        },
        "required": ["asn_number"],
    },
)

perplexity_engine_function_1 = FunctionDeclaration(
    name="search_perplexity_text",
    description=FunctionTools.PerplexityEngine.search_perplexity_text,
    parameters={
        "type": "object",
        "properties": {
            "search_request": {
                "type": "string",
                "description": "The query which needs to be passed to perplexity",
            }
        },
        "required": ["search_request"],
    },
)

perplexity_engine_function_2 = FunctionDeclaration(
    name="search_perplexity_images",
    description=FunctionTools.PerplexityEngine.search_perplexity_images,
    parameters={
        "type": "object",
        "properties": {
            "search_request": {
                "type": "string",
                "description": "the query which needs to be passed to perplexity",
            }
        },
        "required": ["search_request"],
    },
)

username_check_engine_function_1 = FunctionDeclaration(
    name="check_usernames",
    description=FunctionTools.UsernameCheckEngine.check_usernames,
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "The username which needs to be tested on multiple social media and other sites",
            }
        },
        "required": ["username"],
    },
)

github_engine_function_1 = FunctionDeclaration(
    name="fetch_about",
    description=FunctionTools.GitHubEngine.fetch_about,
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "The GitHub username for which the 'about' information is to be extracted",
            }
        },
        "required": ["username"],
    },
)

github_engine_function_2 = FunctionDeclaration(
    name="fetch_repos",
    description=FunctionTools.GitHubEngine.fetch_repos,
    parameters={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "The GitHub username for which the repository information needs to be extracted",
            }
        },
        "required": ["username"],
    },
)

github_engine_function_3 = FunctionDeclaration(
    name="get_repo_secrets",
    description=FunctionTools.GitHubEngine.get_repo_secrets,
    parameters={
        "type": "object",
        "properties": {
            "repository_names": {
                "type": "array",
                "items": {
                    "type": "string",
                    "pattern": r"^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$",
                },
                "description": "The GitHub repositories which need to be analysed for secrets. Each entry must be a valid repository URL in the format: https://github.com/username/repository",
            },
            "rules_file": {
                "type": "string",
                "description": "The YAML rules configuration file",
                "default": str(Config.path.trufflehog_rules),
            },
            "processes": {
                "type": "number",
                "description": "The number of CPU cores to utilize. If the number of repositories is high, increase this number",
                "default": 4,
            },
            "verbose": {
                "type": "number",
                "description": "The verbose level. Keep this 0 if verbose logs aren't important (they usually aren't)",
                "default": 0,
            },
        },
        "required": ["repository_names"],
    },
)

# The anyOf isn't working as I expected!
nettacker_parameters = {
    "type": "object",
    "properties": {
        "targets": {
            "type": "string",
            "description": "Comma-separated target hosts/IPs/domains to scan (e.g. 'example.com,10.0.0.1').",
        },
        "selected_modules": {
            "type": "string",
            "description": "Comma-separated module names to run for the scan (e.g. 'port_scan,dir_scan').",  # we'll have to use oneOf here!
            "enum": nettacker_module_names(),
        },
        "targets_list": {
            "type": "string",
            "description": "Path to a file containing targets (one per line).",
            "default": None,
        },
        "profiles": {
            "type": "string",
            "description": "Comma-separated profile name(s) or path to a profile file to apply predefined scan settings.",
            "default": None,
        },
        "excluded_modules": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Modules to exclude from the scan.",
            "default": None,
        },
        "excluded_ports": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Ports (or port ranges) to exclude from scanning (e.g. ['22', '80-90']).",
            "default": None,
        },
        "usernames": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of usernames to use for credential-based modules.",
            "default": None,
        },
        "usernames_list": {
            "type": "string",
            "description": "Path to a file with usernames (one per line).",
            "default": None,
        },
        "passwords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of passwords to use for credential-based modules.",
            "default": None,
        },
        "passwords_list": {
            "type": "string",
            "description": "Path to a file with passwords (one per line).",
            "default": None,
        },
        "ports": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Ports or port ranges to scan (e.g. ['1-65535','80']).",
            "default": None,
        },
        "user_agent": {
            "type": "string",
            "description": "HTTP User-Agent string to use for web requests.",
            "default": "Nettacker 0.4.0 QUIN",
        },
        "timeout": {
            "type": "number",
            "description": "Per-request timeout in seconds.",
            "default": 3.0,
        },
        "time_sleep_between_requests": {
            "type": "number",
            "description": "Delay (seconds) between individual requests to the same target.",
            "default": 0.0,
        },
        "scan_ip_range": {
            "type": "boolean",
            "description": "If true, treat targets as IP ranges and expand them.",
            "default": False,
        },
        "scan_subdomains": {
            "type": "boolean",
            "description": "If true, attempt to enumerate and scan subdomains of supplied domains.",
            "default": False,
        },
        "skip_service_discovery": {
            "type": "boolean",
            "description": "If true, skip performing service discovery i.e skip port scanning.",
            "default": True,
        },
        "thread_per_host": {
            "type": "integer",
            "description": "Number of threads to spawn per host.",
            "default": 100,
        },
        "parallel_module_scan": {
            "type": "integer",
            "description": "Number of modules to run in parallel. If you're choosing more than one modules, increase this number",
            "default": 1,
        },
        "set_hardware_usage": {
            "type": "integer",
            "description": "Percentage (0-100) or internal knob to limit resource usage. You can choose to leave this at default without affecting much",
            "default": 21,
        },
        "socks_proxy": {
            "type": "string",
            "description": "SOCKS proxy URL (e.g. 'socks5://127.0.0.1:9050') to route traffic through.",
            "default": None,
        },
        "retries": {
            "type": "integer",
            "description": "Number of retries for transient request failures.",
            "default": 1,
        },
        "ping_before_scan": {
            "type": "boolean",
            "description": "If true, ping hosts before attempting scans to check reachability.",
            "default": False,
        },
        "read_from_file": {
            "type": "string",
            "description": "Path to an input file containing serialized scan configuration/results to read from.",
            "default": "",
        },
        "http_header": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Extra HTTP headers to send with requests (each entry like 'Header: value').",
            "default": None,
        },
    },
    "required": ["targets", "selected_modules"],
}

nettacker_engine_function_1 = FunctionDeclaration(
    name="nettacker_run",  # yep the function is simply called run
    description=FunctionTools.NettackerEngine.nettacker_run,
    parameters=nettacker_parameters,
)

haveibeenpwned_engine_function_1 = FunctionDeclaration(
    name="check_email_against_breach_data",
    description=FunctionTools.HaveIBeenPwnedEngine.check_email_against_breach_data,
    parameters={
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address to check for data breach",
            }
        },
        "required": ["email"],
    },
)

ProfessionalEmailFinder_engine_function_1 = FunctionDeclaration(
    name="find_emails_for_domain",
    description=FunctionTools.ProfessionalEmailFinderEngine.find_emails_for_domain,
    parameters={
        "type": "object",
        "properties": {
            "domain_name": {
                "type": "string",
                "description": "The company domain name (e.g., 'stripe.com') for which professional emails need to be retrieved.",
            }
        },
        "required": ["domain_name"],
    },
)

ProfessionalEmailFinder_engine_function_2 = FunctionDeclaration(
    name="find_emails_for_person",
    description=FunctionTools.ProfessionalEmailFinderEngine.find_emails_for_person,
    parameters={
        "type": "object",
        "properties": {
            "domain_name": {
                "type": "string",
                "description": "The company domain name (e.g., 'reddit.com', 'owasp.org').",
            },
            "first_name": {
                "type": "string",
                "description": "The first name of the person.",
            },
            "last_name": {
                "type": "string",
                "description": "The last name of the person.",
            },
        },
        "required": ["domain_name", "first_name", "last_name"],
    },
)

GetPages_engine_function_1 = FunctionDeclaration(
    name="fetch_get_page",
    description=FunctionTools.GetPagesEngine.fetch_get_page,
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL you want to make the GET request to",
            },
        },
        "required": ["url"],
    },
)

GetPages_engine_function_2 = FunctionDeclaration(
    name="fetch_get_pages_bulk",
    description=FunctionTools.GetPagesEngine.fetch_get_pages_bulk,
    parameters={
        "type": "object",
        "properties": {
            "urls": {
                "type": "array",
                "description": "A list of URLs which need to be tests to make a GET request on",
            }
        },
        "required": ["urls"],
    },
)

HyperlinkExtract_engine_function_1 = FunctionDeclaration(
    name="hyperlinks_for_single_url",
    description=FunctionTools.HyperlinkExtractEngine.hyperlinks_for_single_url,
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL for which you want to extract all the hyperlinks for",
            }
        },
        "required": ["url"],
    },
)

HyperlinkExtract_engine_function_2 = FunctionDeclaration(
    name="hyperlinks_for_multiple_urls",
    description=FunctionTools.HyperlinkExtractEngine.hyperlinks_for_multiple_urls,
    parameters={
        "type": "object",
        "properties": {
            "urls": {
                "type": "array",
                "description": "The URLs for which you want to extract all the hyperlinks for in an array",
            }
        },
        "required": ["urls"],
    },
)

VerifyAIGeneratedImage_engine_function_1 = FunctionDeclaration(
    name="metadata_analysis",
    description=FunctionTools.VerifyAIGeneratedImageEngine.metadata_analysis,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the image which needs to be analysed. This needs to be the full absolute path",
            }
        },
        "required": ["image_path"],
    },
)

VerifyAIGeneratedImage_engine_function_2 = FunctionDeclaration(
    name="deepscan_fake_image_verification",
    description=FunctionTools.VerifyAIGeneratedImageEngine.deepscan_fake_image_verification,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the image which needs to be analysed. This needs to be the full absolute path",
            }
        },
        "required": ["image_path"],
    },
)

VerifyAIGeneratedImage_engine_function_3 = FunctionDeclaration(
    name="isgsenAI",
    description=FunctionTools.VerifyAIGeneratedImageEngine.isgsenAI,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the image which needs to be analysed. This needs to be the full absolute path",
            }
        },
        "required": ["image_path"],
    },
)

VerifyAIGeneratedImage_engine_function_4 = FunctionDeclaration(
    name="combined_AI_image_verification",
    description=FunctionTools.VerifyAIGeneratedImageEngine.combined_AI_image_verification,
    parameters={
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the image which needs to be analysed. This needs to be the full absolute path",
            }
        },
        "required": ["image_path"],
    },
)

# Query this based on the class and feed the arguments with **args to the functions
class_function_dict = {
    "RedditKnownEngine": [
        known_reddit_function_1,
        known_reddit_function_2,
        known_reddit_function_3,
    ],
    "RedditUnknownEngine": [unknown_reddit_function_1, unknown_reddit_function_2],
    "EmailCheckEngine": [email_check_function],
    "StaticImageExtractionEngine": [
        static_image_analysis_function_1,
        static_image_analysis_function_2,
        static_image_analysis_function_3,
        static_image_analysis_function_4,
    ],
    "DeepScanEngine": [
        active_image_analysis_function_1,
        active_image_analysis_function_2,
        active_image_analysis_function_3,
    ],
    "ImageGeolocationEngine": [
        image_geolocation_function_1,
        image_geolocation_function_2,
        image_geolocation_function_3,
        image_geolocation_function_4,
    ],
    "InstagramEngine": [
        instagram_engine_function_1,
        instagram_engine_function_2,
    ],
    "IPinfoEngine": [
        ipinfo_engine_function_1,
        ipinfo_engine_function_2,
        ipinfo_engine_function_3,
    ],
    "PerplexityEngine": [
        perplexity_engine_function_1,
        perplexity_engine_function_2,
    ],
    "UsernameCheckEngine": [
        username_check_engine_function_1,
    ],
    "GitHubEngine": [
        github_engine_function_1,
        github_engine_function_2,
        github_engine_function_3,
    ],
    "NettackerEngine": [
        nettacker_engine_function_1,
    ],
    "HaveIBeenPwnedEngine": [
        haveibeenpwned_engine_function_1,
    ],
    "ProfessionalEmailFinderEngine": [
        ProfessionalEmailFinder_engine_function_1,
        ProfessionalEmailFinder_engine_function_2,
    ],
    "GetPagesEngine": [GetPages_engine_function_1, GetPages_engine_function_2],
    "HyperlinkExtractEngine": [
        HyperlinkExtract_engine_function_1,
        HyperlinkExtract_engine_function_2,
    ],
    "VerifyAIGeneratedImageEngine": [
        VerifyAIGeneratedImage_engine_function_1,
        VerifyAIGeneratedImage_engine_function_2,
        VerifyAIGeneratedImage_engine_function_3,
        VerifyAIGeneratedImage_engine_function_4,
    ],
}
