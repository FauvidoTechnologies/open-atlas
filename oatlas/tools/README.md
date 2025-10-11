# Available Engines and Functions

---

## EmailCheckEngine (`ecE`) — *email-verification*
Validates email addresses using multiple verification techniques.

### Functions
- **`verify_email_address`** — Verifies whether an email address is valid.

---

## StaticImageExtractionEngine (`siE`) — *image-metadata*
Analyzes image metadata and performs firmware extraction.

### Functions
- **`extract_metadata`** — Extracts all metadata from an image.  
- **`scan_firmware`** — Scans images/binaries for embedded firmware signatures using Binwalk.  
- **`extract_firmware`** — Extracts a firmware section from an image by byte offset.  
- **`extract_strings`** — Extracts readable ASCII and UTF-16LE strings from an image or binary.

---

## RedditKnownEngine (`rkE`) — *reddit-known-username*
Queries Reddit APIs for a known username.

### Functions
- **`fetch_comments`** — Fetches a Reddit user’s recent comments.  
- **`fetch_user_posts`** — Fetches a Reddit user’s recent submissions (posts).

---

## RedditUnknownEngine (`ruE`) — *reddit-unknown-username*
Searches Reddit posts without needing a known username.

### Functions
- **`search_reddit_posts`** — Searches Reddit posts by query and optional subreddit.  
- **`fetch_post_details`** — Retrieves details of a specific Reddit post.

---

## DeepScanEngine (`dsE`) — *dl-image-scans*
Performs deep learning–based analysis of images (facial attributes, deepfake detection, etc.).

### Functions
- **`OCR_analysis`** — Extracts text from images via OCR.  
- **`verify_similar_faces`** — Verifies if two faces belong to the same person.  
- **`face_attribute_analysis`** — Analyzes facial attributes (age, gender, emotion, race).

---

## InstagramEngine (`insE`) — *instagram-query*
Queries Instagram data using HTML parsing and browser automation.

### Functions
- **`fetch_account_information`** — Retrieves basic info of an Instagram username.  
- **`fetch_public_account_posts`** — Fetches public posts from an Instagram profile.

---

## ImageGeolocationEngine (`igE`) — *image-geolocation*
Predicts geolocation from images using Picarta and VertexAI.

### Functions
- **`geolocate_local_image`** — Geolocates a local image.  
- **`geolocate_online_image`** — Geolocates an image via URL.  
- **`geolocate_using_LLMs`** — Performs geolocation inference using LLM reasoning.  
- **`combined_llm_deeplearning_analysis`** — Combines both LLM and deep learning geolocation results.

---

## IPinfoEngine (`ipE`) — *ip-lookups*
Performs IP address lookups via free and paid IPinfo APIs.

### Functions
- **`basic_ip_lookup`** — Free-tier IP lookup.  
- **`core_api_lookups`** — Paid IPinfo Core API lookup.  
- **`core_api_lookups_asn`** — Core API lookup by ASN number.

---

## PerplexityEngine (`pplxE`) — *pplx-search*
Integrates Perplexity AI for intelligent search and summarization.

### Functions
- **`search_perplexity_text`** — Performs text-based search and summary retrieval.  
- **`search_perplexity_images`** — Searches and retrieves image URLs from Perplexity.

---

## UsernameCheckEngine (`ucE`) — *username-enumeration*
Checks for a given username across multiple platforms using the OSS WhatsMyName dataset.

### Functions
- **`check_usernames`** — Scans a given username across multiple sites and returns matches.

---

## GitHubEngine (`ghE`) — *github-search*
Fetches user and repository information from GitHub APIs.

### Functions
- **`fetch_about`** — Fetches GitHub profile details.  
- **`fetch_repos`** — Fetches repositories with metadata.  
- **`get_repo_secrets`** — Extracts possible secrets from a repo and commit history.

---

## NettackerEngine (`ntE`) — *nettacker-scan*
Performs network scanning and vulnerability enumeration using OWASP Nettacker.

### Functions
- **`nettacker_run`** — Runs Nettacker on given targets with optional modules, profiles, and threading.

---

## HaveIBeenPwnedEngine (`HIBP`) — *have-i-been-pwned*
Queries Have I Been Pwned for known data breaches.

### Functions
- **`check_email_against_breach_data`** — Checks if an email address appears in breach records.

---

## ProfessionalEmailFinderEngine (`PEF`) — *professional-email-finder*
Finds professional emails using Hunter.io APIs.

### Functions
- **`find_emails_for_domain`** — Finds professional emails for a given company domain.  
- **`find_emails_for_person`** — Finds a person-specific professional email for a company.

---

## GetPagesEngine (`GPE`) — *get-pages*
Performs HTTP GET requests to check URL validity and retrieve content.

### Functions
- **`fetch_get_page`** — Fetches content of a single URL.  
- **`fetch_get_pages_bulk`** — Fetches multiple URLs in parallel.

---

## HyperlinkExtractEngine (`HLE`) — *hyperlink-extract*
Extracts hyperlinks, emails, and references from webpages.

### Functions
- **`hyperlinks_for_single_url`** — Extracts hyperlinks from a single page.  
- **`hyperlinks_for_multiple_urls`** — Extracts hyperlinks from multiple pages in bulk.

---

## VerifyAIGeneratedImageEngine (`VAI`) — *verify-ai-generated-image*
Analyzes whether an image is AI-generated or authentic using metadata, deepfake detection, and external APIs.

### Functions
- **`metadata_analysis`**  
  - **desc:** Performs metadata-based inspection of an image (EXIF and C2PA extraction).  
  - **args:** `image_path` — absolute path to the image (e.g., `/home/user/images/test.jpg`).  
  - **returns:** dict — Extracted metadata including EXIF and C2PA data.

- **`deepscan_fake_image_verification`**  
  - **desc:** Detects generative model signatures using deepfake detection algorithms.  
  - **args:** `image_path` — absolute path to the image.  
  - **returns:** dict — Verification results with probability scores.

- **`isgenAI`**  
  - **desc:** Uses the external IsgenAI service to verify AI generation.  
  - **args:** `image_path` — absolute path to the image.  
  - **returns:** dict — `{ classification: 'AI-generated', confidence: 0.87 }`.

- **`combined_AI_image_verification`**  
  - **desc:** Aggregates metadata, deepfake, and IsgenAI analyses for a unified result.  
  - **args:** `image_path` — absolute path to the image.  
  - **returns:** dict — Aggregated verification results.

---

## OathNetSearchEngine (`OATH`) — *oathnet-search*
Client for OathNet search endpoints. Handles session initialization and queries for breach and stealer log data.

### Functions
- **`get_breached_data`**  
  - **desc:** Queries `/search-breach/` for breach results.  
  - **args:** `query` — search string (same as session query).  
  - **returns:** dict — JSON response with breach data and metadata.

- **`get_stealer_logs`**  
  - **desc:** Queries `/search-stealer/` for stealer log data.  
  - **args:** `query` — search string.  
  - **returns:** dict — JSON response with log samples and timestamps.

- **`combined_oathnet_search`**  
  - **desc:** Runs both breach and stealer searches and aggregates results.  
  - **args:**  
    - `query` — search string.  
    - `include_raw` — optional boolean to include raw responses.  
  - **returns:** dict — `{ search_id, breach, stealer, raw }`.

---