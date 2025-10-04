# This holds all the APIs and their descriptions and use cases
# If a new API is being used, it needs to be updated here
# Additionally this tells whether paid versions of that API are available or not

"""
General structure for an API listing

{
	"api_1": {
		"name": api_name",
		"description": "about the API and its usage",
		"current_version": "free|paid",
		"paid_versions_available": "is|is not",
		"available_paid_versions": None|["version|key_1", "version|key_2" ...]
	},
	"api_2": {
		"name": api_name",
		"description": "about the API and its usage",
		"current_version": "free|paid",
		"paid_versions_available": "is|is not",
		"available_paid_versions": None|["version|key_1", "version|key_2" ...]|NA
	},
	...
}
"""

service_dictionary = {
    "api_1": {
        "name": "vertexAI",
        "description": "API calls for image searches and more",
        "current_version": "doesn't exist",  # Was intially setup on MY billing account, so please use yours...
        "paid_versions_available": "is",
        "available_paid_versions": "NA",  # Not sure but this seems about right
    },
    "api_2": {
        "name": "perplexity",
        "description": "The perplexity API as a substitute for googling and intial information gathering",
        "current_version": "free (sonar)",
        "paid_versions_available": "is",
        "available_paid_versions": [
            "sonar-pro",
            "sonar-reasoning",
            "sonar-reasoning-pro",
            "sonar-deep-research",
        ],
    },
    "api_3": {
        "name": "picarta",  # The structure doesn't change only the key does so all versions are supported
        "description": "The picarta API is for image geolocation",
        "current_version": "Free",
        "paid_versions_available": "is",
        "available_paid_versions": ["wallet", "monthy-subscription", "enterprise"],
    },
    "api_4": {
        "name": "isgen",
        "description": "This is a `different` way of making the POST requests for AI image detection",
        "current_version": "Free",  # This is technically free
        "paid_versions_available": "is",
        "available_paid_versions": ["lots"],  # Update this
    },
}

# There are more APIs, need to sit and document
