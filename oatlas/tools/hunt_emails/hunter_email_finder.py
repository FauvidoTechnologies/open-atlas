import os
from typing import Union

import requests

from oatlas.config import Hunter
from oatlas.logger import get_logger

log = get_logger()


class ProfessionalEmailFinderEngine:
    """
    Professional email finding using Hunter
    """

    @staticmethod
    def find_emails_for_domain(domain_name: str) -> Union[str, None]:
        """
                Fetches emails for a given domain using Hunter.io's Domain Search API.

                Returns:
                        str: A nicely formatted string containing all email entries with their details.
                        Returns None if none found or request fails.

                Example data:

                {
                        "data": {
                        "domain": "stripe.com",
                        "disposable": false,
                        "webmail": false,
                        "accept_all": true,
                        "pattern": "{first}{l}",
                        "organization": "Stripe",
                        "description": "Stripe is a fintech company that specializes in online payment processing services.",
                        "industry": "Technology, Information and Internet",
                        "twitter": "https://twitter.com/stripe",
                        "facebook": "https://facebook.com/175383762511776",
                        "linkedin": "https://linkedin.com/company/stripe",
                        "instagram": null,
                        "youtube": "https://youtube.com/stripe",
                        "technologies": [
                        "algolia",
                        "amazon-s3",
                        "amazon-web-services",
                        "angular-js",
                        "typescript",
                        "vue-js",
                        "windows",
                        "zip"
                        ],
                        "country": "US",
                        "state": "CA",
                        "city": "South San Francisco",
                        "postal_code": null,
                        "street": null,
                        "headcount": "5001-10000",
                        "company_type": "privately held",
                        "linked_domains": [],
                        "emails": [
                                {
                                        "value": "valerie@stripe.com",
                                        "type": "personal",
                                        "confidence": 94,
                                        "sources": [
                                                {
                                                        "domain": "linkedin.com",
                                                        "uri": "https://www.google.com/search?q=site:linkedin.com%20valerie%20wagoner%20stripe",
                                                        "extracted_on": "2025-08-19",
                                                        "last_seen_on": "2025-09-01",
                                                        "still_on_page": true
                                                }
                                        ],
                                        "first_name": "Valerie",
                                        "last_name": "Wagoner",
                                        "position": "Head of Product APAC",
                                        "position_raw": "Global Product, Head of APAC",
                                        "seniority": "executive",
                                        "department": "management",
                                        "linkedin": "https://www.linkedin.com/in/valwagoner",
                                        "twitter": null,
                                        "phone_number": null,
                                        "verification": {
                                        "date": "2025-09-25",
                                        "status": "valid"
                                                }
                                        },
                                ]
                        },
                        "meta": {
                                "results": 854,
                                "limit": 10,
                                "offset": 0,
                                "params": {
                                "domain": "stripe.com",
                                "company": null,
                                "type": null,
                                "seniority": null,
                                "department": null
                                }
                }
        }

        Returns:
                str: A nicely formatted string containing all email entries with their details.
                        Returns None if none found or request fails.
        """

        hunter_api_key = os.getenv("hunter_api_key")

        if not hunter_api_key:
            log.error("Missing Hunter API key in environment variable 'hunter_api_key'.")
            return None

        url = Hunter.domain.format(domain_name=domain_name, hunter_api_key=hunter_api_key)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            emails = data.get("data", {}).get("emails", [])
            if not emails:
                return "No emails found."

            email_strings = []
            for email in emails:
                parts = [
                    f"Email: {email.get('value')}",
                    f"Type: {email.get('type')}",
                    f"Confidence: {email.get('confidence')}",
                    f"First Name: {email.get('first_name')}",
                    f"Last Name: {email.get('last_name')}",
                    f"Position: {email.get('position')}",
                    f"Seniority: {email.get('seniority')}",
                    f"Department: {email.get('department')}",
                    f"LinkedIn: {email.get('linkedin')}",
                    f"Twitter: {email.get('twitter')}",
                    f"Phone: {email.get('phone_number')}",
                ]

                # Handle verification info if present
                verification = email.get("verification")
                if verification:
                    parts.append(
                        f"Verification Status: {verification.get('status')} (Date: {verification.get('date')})"
                    )

                # Handle sources if present
                sources = email.get("sources", [])
                if sources:
                    source_strs = [
                        f"{src.get('domain')} ({src.get('uri')}) last seen {src.get('last_seen_on')}"
                        for src in sources
                    ]
                    parts.append("Sources: " + "; ".join(source_strs))

                email_strings.append("\n".join(parts))

            return "\n---\n".join(email_strings)

        except requests.exceptions.RequestException as e:
            log.error(f"Request failed: {e}")
            return None
        except ValueError as e:
            log.error(f"Error parsing response: {e}")
            return None

    @staticmethod
    def find_emails_for_person(
        domain_name: str, first_name: str, last_name: str
    ) -> Union[str, None]:
        """
        Finds a person's professional email at a given domain using Hunter.io's Email Finder API.

        Args:
                domain_name (str): Company domain (e.g., "reddit.com")
                first_name (str): Person's first name
                last_name (str): Person's last name

        This is how the example response looks like

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

        Returns:
                str: A formatted string with all details if found
                None: If no email is found or request fails

        """
        hunter_api_key = os.getenv("hunter_api_key")

        if not hunter_api_key:
            log.error("Missing Hunter API key in environment variable 'hunter_api_key'.")
            return None

        url = Hunter.person_domain_email.format(
            domain_name=domain_name,
            person_first_name=first_name,
            person_last_name=last_name,
            hunter_api_key=hunter_api_key,
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            person = data.get("data")
            if not person:  # This is bad news, means we found nothing on him
                return None

            parts = [
                f"First Name: {person.get('first_name')}",
                f"Last Name: {person.get('last_name')}",
                f"Email: {person.get('email')}",
                f"Score: {person.get('score')}",
                f"Domain: {person.get('domain')}",
                f"Company: {person.get('company')}",
                f"Position: {person.get('position')}",
                f"Twitter: {person.get('twitter')}",
                f"LinkedIn: {person.get('linkedin_url')}",
                f"Phone: {person.get('phone_number')}",
            ]

            verification = person.get("verification")
            if verification:
                parts.append(
                    f"Verification Status: {verification.get('status')} (Date: {verification.get('date')})"
                )

            sources = person.get("sources", [])
            if sources:
                source_strs = [
                    f"{src.get('domain')} ({src.get('uri')}) last seen {src.get('last_seen_on')}"
                    for src in sources
                ]
                parts.append("Sources: " + "; ".join(source_strs))

            return "\n".join(parts)

        except requests.exceptions.RequestException as e:
            log.error(f"Request failed: {e}")
            return None
        except ValueError as e:
            log.error(f"Error parsing response: {e}")
            return None
