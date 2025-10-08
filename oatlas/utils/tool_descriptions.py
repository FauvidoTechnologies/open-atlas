class FunctionTools:
    """
    Holds the descriptions for the low-level model to figure out the best tool within a class for a task
    """

    class KnownRedditFunctions:
        """
        For the known username reddit reverse searching engine
        """

        fetch_comments = """
			The fetch_comments function uses the reddit username to fetch all previous comments made by the user.
			It returns a comprehensive dictionary detailing the subreddit, the title of the post and more.
		"""

        fetch_about = """
			The fetch_about function uses the reddit username to fetch everything it can about the user's profile.
			This include profile pictures, creation date etc.
		"""

        fetch_user_posts = """
			The fetch_user_posts function uses the reddit username to fetch a certain number of posts made by the user.
		"""

    class UnknownRedditFunctions:
        """
        For the unknown username reddit reverse searching engine
        """

        search_reddit_posts = """
			The search_reddit_posts function uses a query to search the entire reddit database (or a subreddit) for all
			posts that match that query.
			The query needs to include keywords for the type of posts you want to obtain.
		"""

        fetch_post_details = """
			The fetch_post_details function uses the post_id and the subreddit to fetch details about a specific post.
			This function is to be called when the post_id is available.
		"""

    class VerifyEmailFunctions:
        """
        For email verification using SMTP probes
        """

        verify_email_address = """
			The verify_email_address function takes in the email address and verifies if it is correct.
			It makes use of the following methods:

			1. Regex matching for a valid email syntax
			2. Verify the domain existence of the address
			3. Establish an SMTP using a random address and try to connect to the mailbox
		"""

    class StaticImageExtraction:
        """
        For static image analysis without deep learning models
        """

        extract_metadata = """

			The extract_metadata function analyzes an image file and gathers as much information as possible about its origin and properties. Specifically, it:

			1. Derives basic metadata when no EXIF data is present (e.g., dimensions, format, file size).
			2. Extracts full EXIF metadata if available, by running a subprocess with comprehensive flags to capture all possible details.
			3. Parses C2PA (Content Credentials) data if embedded, which can help trace the image’s source and authenticity.

			In practice, metadata extraction is the first and most reliable step when assessing whether an image is original or artificially generated.
		"""

        scan_firmware = """
			The scan_firmware function takes the path to a firmware image file and scans its binary contents
			using signature analysis and binwalk. It identifies embedded components such as images, text blocks, or file
			headers without extracting them.

			For each detected section, it returns a structured entry of the form:

			SignatureResult {
				offset: <starting byte offset of the signature>,
				id: <unique identifier>,
				size: <size in bytes>,
				name: <type of detected content, e.g., 'png', 'svg'>,
				confidence: <match confidence score>,
				description: <human-readable explanation>,
				always_display: <bool>,
				extraction_declined: <bool>,
				preferred_extractor: <optional extractor name>,
			}

			The function returns all results as a formatted string representing a list of such matches.
			This is useful for inspecting the internal structure of firmware without performing extraction.
		"""

        extract_firmware = """
			The extract_bytes function takes the path to a binary file, a starting offset, and a byte count to extract a specific chunk of data.
			It is a low-level utility for targeted extraction, often used after `scan_firmware` to pull out a component identified by its offset and size.
			The function creates a new file containing only the extracted bytes. 
			This is useful for isolating and further analyzing individual sections of a binary file.
		"""

        extract_strings = """
			Extract the ASCII strings from inside a binary
		"""

    class DeepScanEngine:
        """
        For active image analysis making use of deep learning models
        """

        verify_similar_faces = """
			Runs the DeepFace image verification scan (need not be potraits)
			Args:
			image_path_1: path to the first image as a string
			image_path_2: path to the second image as a string
			Return:
			Dictionary containing:
			- a boolean value for verification status,
			- value for how far apart the images really are
			- the confidence threshold for the prediction
		"""

        face_attribute_analysis = """
			Runs the DeepFace face analysis scan on a human face
			Args:
			image_path: path to the image file
			Returns:
			List<Dict> containing:
			- age
			- gender (dominant)
			- race (dominant)
			- emotion (dominant)
		"""

        OCR_analysis = """
			Extracts the text from a given image using pytesseract's OCR engine

			Args:
				image_path: path to the image file
			Returns:
				string of extracted text
		"""

    class ImageGeolocationEngine:
        """
        For image geolocation using APIs
        """

        geolocate_local_image = """
			This function performs image based geolocation for images present locally. It uses picarta's APIs to perform geolocation. This means it makes
            use of DeepLearning models and indexed databases for the task.

            It requires a URL which leads to the image and outputs a string like this for example:
				{
					"camera_maker": "<the comany that made the camera on which this image was shot>",
					"camera_model": "<the model for the camera>",
					"topk_predictions_dict": {
						'1': {
							'address': {
								'city': 'Sydney', 
								'country': 'Australia', 
								'province': 'New South Wales'
								}, 
							'confidence': 0.9438701868057251, 
							'gps': [-33.86357, 151.20209]
							}, 
						'2': {
							'address': {
								'city': 'North Adelaide', 
								'country': 'Australia', 
								'province': 'South Australia'
								}, 
							'confidence': 0.9391460204124451, 
							'gps': [-34.915462, 138.59592]
							},
						...
					},
				}

			This is a json dump on a dictionary.
		"""

        geolocate_online_image = """
			This function performs image based geolocation for images found online. It uses picarta's APIs to perform geolocation. This means it makes
            use of DeepLearning models and indexed databases for the task.

            It requires a URL which leads to the image and outputs a string like this for example:

				{
					"camera_maker": "<the comany that made the camera on which this image was shot>",
					"camera_model": "<the model for the camera>",
					"topk_predictions_dict": {
						'1': {
							'address': {
								'city': 'Sydney', 
								'country': 'Australia', 
								'province': 'New South Wales'
								}, 
							'confidence': 0.9438701868057251, 
							'gps': [-33.86357, 151.20209]
							}, 
						'2': {
							'address': {
								'city': 'North Adelaide', 
								'country': 'Australia', 
								'province': 'South Australia'
								}, 
							'confidence': 0.9391460204124451, 
							'gps': [-34.915462, 138.59592]
							},
						...
					},
				}

			This is a json dump on a dictionary.
		"""

        geolocate_using_LLMs = """
            This function performs image based geolocation for images stored locally. It uses VertexAI's gemini-2.5-pro and OpenAI's GPT-5o to perform geolocation.
            It returns a pydantic BaseModel with the following fields:

            Initial_observations: what is visible
            Geographical_clues: e.g. climate, vegetation, terrain
            Cultural_structural_clues: e.g. architecture, signs, vehicles, infrastructure
            reasoning: how the model narrowed it down
            final_estimate: coordinates or place name
        """

        combined_llm_deeplearning_analysis = """

            This is a combined function which returns a dictionary contains geolocation performed by picarta's APIs through Deeplearning models and VertexAI using
            Gemini-2.5-pro. The output of this function is something like this for example:

            {
                "picarta": json.dumps({
                        "camera_maker": "<the comany that made the camera on which this image was shot>",
                        "camera_model": "<the model for the camera>",
                        "topk_predictions_dict": {
                            '1': {
                                'address': {
                                    'city': 'Sydney', 
                                    'country': 'Australia', 
                                    'province': 'New South Wales'
                                    }, 
                                'confidence': 0.9438701868057251, 
                                'gps': [-33.86357, 151.20209]
                                }, 
                            '2': {
                                'address': {
                                    'city': 'North Adelaide', 
                                    'country': 'Australia', 
                                    'province': 'South Australia'
                                    }, 
                                'confidence': 0.9391460204124451, 
                                'gps': [-34.915462, 138.59592]
                                },
                            ...
                        },
                    }
                ),
                "vertexai": <pydantic BaseModel> 
                    Initial_observations: what is visible
                    Geographical_clues: e.g. climate, vegetation, terrain
                    Cultural_structural_clues: e.g. architecture, signs, vehicles, infrastructure
                    reasoning: how the model narrowed it down
                    final_estimate: coordinates or place name
            }

        """

    class InstagramEngine:
        """
        For instagram lookups treading gray areas
        """

        fetch_account_information = """
			Fetch metadata from an Instagram account (public or private). Extract number of followers, following, total posts, bio text, profile picture URL, and perform deep learning analysis on the profile picture (including age, race, gender and emotion guessing).
            Parameters:
            - username (string, required): Instagram handle.

            Returns:
            - followers (int): Number of followers.
            - following (int): Number of accounts followed.
            - posts (int): Total number of posts.
            - bio (string): User biography.
            - profile_picture_url (string): URL of profile picture.
            - profile_picture_analysis (object): Analysis of profile picture with:
                - age
                - race
                - emotion
                - gender
                - is_deepfake - boolean True/False (AI generated image)
		"""

        fetch_public_account_posts = """
            Automates visiting a public Instagram profile using Playwright to extract up to 12 recent posts. For each post, it gathers the thumbnail URL, number of likes, and number of comments. It performs image analysis using DeepLearning models on each image and adds the inference to the output.

            Parameters:
            - username (string, required): Instagram handle of the public profile.

            Returns:
            - posts (list of objects): List of posts with fields:
                - thumbnail_url (string): URL of the post thumbnail image.
                - likes (int): Number of likes on the post.
                - comments (int): Number of comments on the post.
                - thumbnail_analysis (string): Description of the thumbnail
        """

    class IPinfoEngine:
        """
        For IPaddress lookups
        """

        basic_ip_lookup = """
			Performs a basic IP lookup using the IPinfo API (free tier).
			The function retrieves the API token from environment variables, constructs the request URL, and queries IPinfo with the specified IP address. The request includes a Linux user-agent and asks for JSON (Accept: application/json).
			It returns the API response as a formatted JSON string for easy readability and downstream consumption.

			Inputs:
				ipaddress (str) → The IP address to be queried.
			Outputs:
				(str) → JSON response from IPinfo, pretty-printed with indentation.
		"""

        core_api_lookups = """
        	Performs an advanced lookup using the ipaddress provided.

        	IMPORTANT: This requries the paid API called "core" for the IPinfo tool. Please verify if the API token is available before using this!

			The function retrieves the API token from environment variables, constructs the request URL, and queries IPinfo with the specified IP address. The request includes a Linux user-agent and asks for JSON (Accept: application/json).
			It returns the API response as a formatted JSON string for easy readability and downstream consumption.

			Inputs:
				ipaddress (str) → The IP address to be queried.
			Outputs:
				(str) → JSON response from IPinfo, pretty-printed with indentation.
		
			The output includes detailed geolocation including latitute and longitutes, while also providing some more metadata on the same.	
		"""

        core_api_lookups_asn = """
			Performs an advanced lookup using the ASN value provided.

			IMPORTANT: This requries the paid API called "core" for the IPinfo tool. Please verify if the API token is available before using this!

			The function retrieves the API token from environment variables, constructs the request URL, and queries IPinfo with the specified IP address. The request includes a Linux user-agent and asks for JSON (Accept: application/json).
			It returns the API response as a formatted JSON string for easy readability and downstream consumption.

			Inputs:
				asn_number (str) → The ASN to be queried.
			Outputs:
				(str) → JSON response from IPinfo, pretty-printed with indentation.
		
			The output includes detailed geolocation information incluing registry, domain, netblocks, allocation dates and many more.
		"""

    class PerplexityEngine:
        """
        For perplexity functions
        """

        search_perplexity_text = """
			- This function uses perplexity's APIs to make search queries. It takes in an input the query to be given to perplexity and outputs a detailed analysis that perplexity performs.
			- Use this tool whenever you need up-to-date factual data from the internet. This data can be about anything.
			- It does not generate reasoning or analysis — it only retrieves and summarizes information from external sources.
		"""

        search_perplexity_images = """
			- This function uses perplexity's APIs to make search queries. It takes in an input the query to be given to perplexity and outputs a detailed analysis that perplexity performs.
			- Use this tool whenever you need to find relevant images about a anything from the internet.
			- It does not generate reasoning or analysis — it only retrieves the image URLs from external sources.
		"""

    class UsernameCheckEngine:
        """
        For username searching functions
        """

        check_usernames = """
			Performs a username check across ~700 websites using the WhatsMyName dataset.

			The function takes in a username, constructs profile URLs based on each site's pattern,
			and queries them in a threaded manner to maximize speed. The response from each site is
			interpreted according to its detection rules (status codes, regex matches, etc.) to 
			determine if the username exists on that platform.

			Inputs:
				username (str) → The username to be checked across supported websites.

			Returns a dictionary of all matches with keys as the site name and values as the matched URI which includes the username
		"""

    class GitHubEngine:
        """
        For GitHub reverse lookups
        """

        fetch_about = """	
			Pick this tool when:
				- The user asks for a user’s profile-level information: name, username, bio, company, blog, location, twitter handle, follower count, when they joined GitHub, or their avatar/profile picture.
				- Use it to verify identity (avatar URL, name) or to get last profile-update time for activity checks.
		"""

        fetch_repos = """
			Pick this tool when:
				- The user asks for a list or summary of repositories belonging to username (names, descriptions, language, whether forked, license, created/updated dates, stars, etc.).
				- Use this to produce inventories, identify popular projects, or extract metadata for each repo.
		"""

        get_repo_secrets = """
			This tool is an implementation of trufflehog, a GitHub repository secrets scanner. It takes in a list of GitHub URLs to scan
			and scans for API keys, secret tokens, RSA keys, any other confidencial key that it can find! This includes API keys, database passwords, private encryption keys, and more...
			
			This tool can look for secrets in many places including Git, chats, wikis, logs, API testing platforms, object stores, filesystems and more
		
			TruffleHog classifies over 800 secret types, mapping them back to the specific identity they belong to. Is it an AWS secret? Stripe secret? Cloudflare secret?
			Postgres password? SSL Private key? Sometimes it's hard to tell looking at it, so TruffleHog classifies everything it finds.
		"""

    class NettackerEngine:
        """
        For running nettacker
        """

        nettacker_run = """
            Nettacker automates tasks like port scanning, service detection, subdomain enumeration, network mapping, vulnerability scanning, credential brute-force testing making it a powerful
            tool for identifying weaknesses in networks, web applications, IoT devices and APIs. It supports HTTP/HTTPS, FTP, SSH, SMB, SMTP, ICMP, TELNET, XML-RPC, and can run scans in parallel for speed.

            - Accepts single IPv4s, IP ranges, CIDR blocks, domain names, and full HTTP/HTTPS URLs.
            - Use it to automate reconnaissance, misconfiguration checks, service discovery, and vulnerability scanning.
        """

    class HaveIBeenPwnedEngine:
        """
        For running HIBP API calls
        """

        check_email_against_breach_data = """
            Use this function to check if a given email address has been exposed in any known data breaches. The function queries the Have I Been Pwned database and returns details of all breached accounts associated with that email.
            Provide the email as input, and the function will list the breaches, including service names, dates, and types of compromised data.

            # Parameters:
               - email (string, required) — The email address to check for breaches.
            # Example usage:
                - Input: "alice@example.com"
                - Output: A list of breach records (e.g., "Adobe — October 2013 — email addresses, passwords").
        """

    class ProfessionalEmailFinderEngine:
        """
        For running Email finders
        """

        find_emails_for_domain = """    	
			Fetches emails for a given domain using Hunter.io's Domain Search API.

			Args:
				domain_name: A domain name for which you want to get emails for (eg. owasp.org, stripe.com)

			Returns:
				str: A nicely formatted string containing all email entries with their details.
				Returns None if none found or request fails.

			Use this when you just have a domain name and you want to get leads.

    	"""

        find_emails_for_person = """
			Finds a person's professional email at a given domain using Hunter.io's Email Finder API.

			Args:
				domain_name (str): Company domain (e.g., "reddit.com")
				first_name (str): Person's first name
				last_name (str): Person's last name

			Returns:
				str: A formatted string with all details if found
				None: If no email is found or request fails

			Use this function when you have a target's name and a company which that target belongs to.

			This is the typical information that will be present in that string:

			{
				"data": {
					"first_name": "Alexis",
					"last_name": "Ohanian",
					"email": "alexis@reddit.com",
					"score": 97,
					"domain": "reddit.com",
					"accept_all": true,
					"position": "Designer",
					"twitter": null,
					"linkedin_url": null,
					"phone_number": null,
					"company": "Reddit",
					"sources": [],
					"verification": {
						"date": "2025-09-26",
						"status": "valid"
						}
					},
				"meta": {
					"params": {
						"first_name": "Alexis",
						"last_name": "Ohanian",
						"full_name": null,
						"domain": "reddit.com",
						"company": null,
						"max_duration": null
					}
				}
			}
    	"""

    class GetPagesEngine:
        """
        For fetching the about page for URLs
        """

        fetch_get_page = """
            Use this function whenever you need to perform a GET request on a single URL. 
            It will return both the HTTP status code and the response text (often JSON). 

            Typical uses:
            - Verifying if a specific URL exists and is reachable.
            - Checking whether a profile, API endpoint, or resource returns valid data.
            - Retrieving the raw JSON or text response from a known URL.

            IMPORTANT:
            - Always prefer this function over browser automation when you only need to 
              check if a URL works or obtain its raw contents.
        """

        fetch_get_pages_bulk = """
            Use this function whenever you need to check multiple URLs in one go. 
            It performs GET requests on all provided URLs concurrently (in parallel) 
            and returns a dictionary where each URL is mapped to:
              - its HTTP status code
              - the response text (often JSON).

            Typical uses:
            - Quickly validating a batch of URLs discovered after a username search.
            - Checking multiple API endpoints for existence and content.
            - Collecting results from multiple sources without slow sequential requests.

            IMPORTANT:
            - This function is designed for speed and accuracy. Use it instead of 
              browser automation whenever possible, as it directly tests whether 
              each URL is valid and what it contains.
        """

    class HyperlinkExtractEngine:
        """
        For extracting all hyperlinks from URLs
        """

        hyperlinks_for_single_url = """
        	This function extracts all hyperlinks from a single webpage.

	        You should use this function in the following cases:
	        1. You want to analyze one specific URL and quickly discover all its outbound or internal links.
	        2. You are looking for potentially relevant connections such as:
	           - Contact details embedded in links (e.g., "mailto:someone@example.com").
	           - Links to professional or social media platforms (LinkedIn, Twitter, GitHub, etc.).
	           - References to related resources or subpages.
	        3. You want a lightweight way to explore a page’s link structure before performing deeper automation.

	        The function ensures that:
	        - You receive a clean list of all links extracted from the page.
	        - Links are returned in their absolute form, ready for further validation or filtering.
	        - You can use the extracted hyperlinks for lead generation, discovery of related resources,
	          or as input for subsequent engines.

	        Prefer this function when your scope is limited to a single page and you don’t need to process 
	        multiple URLs in bulk.
        """

        hyperlinks_for_multiple_urls = """
	        This function extracts all hyperlinks from a list of webpages in one go.

	        You should use this function in the following cases:
	        1. You want to process multiple URLs efficiently and gather their link structures in parallel.
	        2. You are scanning multiple domains or pages to find:
	           - Contact links (emails, phone number pages, contact forms).
	           - Social handles (LinkedIn, Twitter, GitHub, etc.).
	           - Additional related references spread across different sources.
	        3. You need a structured mapping of URLs to their discovered links for downstream processing.

	        The function ensures that:
	        - You receive structured output: each input URL maps to a list of its extracted links.
	        - This allows you to compare, merge, or filter across multiple sources easily.
	        - It acts as a fast, programmatic way to discover related resources before launching
	          browser automation or other heavy operations.

	        Prefer this function when your goal is to map and analyze multiple webpages in bulk, 
	        saving time and resources.
        """

    class VerifyAIGeneratedImageEngine:
        """ """

        deepscan_fake_image_verification = """

		This engine is used to verify if the image is AI generated or not. It uses the DeepScan model to verify this ONLY
		for portraits. If the image is not a portrait, this won't work. 

		Additionally, this model is a little weak, as in, it can detect only the very obvious ones!

		Args:
			image_path: path to the image fiel
		Returns:
			List<Dict> containing:
			- is_real <boolean>
			- antispoof_score <Int> -> How real or fake
    	"""

        metadata_analysis = """
        	Extract the C2PA and exif data for an image to see if any AI generated traces are left behind. This is a very low hanging fruit and it
        	might or might now work!
        """

        isgsenAI = """
        	This is the best option. The API runs SOTA models in the background which are extremely good at giving out a probability score for
        	AI generated images (human vs AI).

        	Use this for the best analysis on whether the image is AI generated or has been modified in any way using AI
		"""

        combined_AI_image_verification = """

			This is the combined analysis which uses
			1. Metadata extraction
				Extract the C2PA and exif data for an image to see if any AI generated traces are left behind. This is a very low hanging fruit and it
				might or might now work!
			2. deepface models
				This engine is used to verify if the image is AI generated or not. It uses the DeepScan model to verify this ONLY
				for portraits. If the image is not a portrait, this won't work. 

				Additionally, this model is a little weak, as in, it can detect only the very obvious ones!

				Args:
					image_path: path to the image fiel
				Returns:
					List<Dict> containing:
					- is_real <boolean>
					- antispoof_score <Int> -> How real or fake
			3. IsgenAI
				This is the best option. The API runs SOTA models in the background which are extremely good at giving out a probability score for
				AI generated images (human vs AI).

			Note that if the results are contradictory between the two AI models, always prefer the IsgenAI one.
		"""
