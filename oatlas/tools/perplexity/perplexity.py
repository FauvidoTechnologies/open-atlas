import json
import os
from typing import Dict

import requests

from oatlas.config import API, Config
from oatlas.core.arg_parser import ArgParser
from oatlas.core.module import Module
from oatlas.logger import get_logger
from oatlas.utils.common import read_file, download_image_from_url

log = get_logger()

IMAGE_FILE_LIST = []
IMG_BASE_DIR = Config.path.results_path / "scraped"


def format_perplexity_image_search_json(pplx_img_search_result_json: Dict) -> str:
    """
    This is the sample input:
        {
          'id': 'c1e31961-aca9-4a81-872b-f095d1ea4b19',
          'model': 'sonar',
          'created': 1758440277,
          'usage': {
            ....                # This is the usage tokens which aren't really needed
            'cost': {
                ....            # Request token costs
            }
          },
          'citations': [
                ....            # Some citations which are irrelevant to us
          ],
          'search_results': [
            {
              'title': 'fsdiahfuaeifanfa',
              'url': 'https://www.fsdiafawefa.com/afsd/fdsaj-sd-2fas-i-6089',
              'date': '2024-10-04',
              'last_updated': '2024-10-06',
              'snippet': 'Some xyz thing'
            },
            ....
          ],
          'images': [
            {
              'image_url': 'https://ismgfdas-fsdacdn.nyc3.cweden.didsafgitalocfeanspaces.com/au12t1h22o1rs/kurtfds-affdbsaker-fflfargeppIfawmaasge-5d-a-60189.png',
              'origin_url': 'https://wwefwaw.bppadsaafnkcicncfocsecucccritdfdsayp.ccfdpcoam/gfafguth2orsd/ksuargspfts-ddbsa2ke1rfdsaa-i-6089',
              'height': 500,
              'width': 400,
              'title': 'xyz'
            },
            .....
          ],
          'object': 'chat.completion',
          'choices': [
            ...
          ]
        }

    The output needs to contain where the images were downloaded to and some preliminary analysis on the same. The analysis is done using
    the `analyse_image_dir()` function inside Module.

    Returns:
        response: Dict -> All this is added to the reponse dictionary and dumped
    """

    response = {"scraped_images_base_dir": str(IMG_BASE_DIR)}

    images = pplx_img_search_result_json.get("images")

    if not isinstance(images, list):
        log.error("Perplexity couldn't find any images on this target!")
        return {
            "images_found": None,
        }  # For consistency
    for idx, image in enumerate(images):
        image_url = image.get("image_url")
        filename = f"scraped_{idx+1}"
        IMAGE_FILE_LIST.append(str(IMG_BASE_DIR / filename))

        if download_image_from_url(image_url, filename):
            response[f"scraped_image_{idx+1}"] = filename
        else:
            log.verbose_info("Image download failed!")

    # Setting update_intel to False returns a dictonary
    analyis_output = Module(brain_id=None).analyse_image_dir(
        image_files=IMAGE_FILE_LIST, update_intel=False
    )
    response["scraped_dir_analysis_output"] = analyis_output

    return json.dumps(response)


class PerplexityEngine(ArgParser):
    """
    Perplexity is being used as a substitute for googling and first line of research.
    Free and paid keys are handled for using the `.env.private` bypass
    """

    @staticmethod
    def search_perplexity_text(search_request):
        """
        Perform a perplexity API search. The endpoint URL remains the same regardless of the model used.

        Args:
            search_request: This is the query that needs to be passed through to perplexity

        Returns:
            None -> If anything fails ||
            data -> Direct response with no images or anything

        This is specifically to get text based inputs from perplexity
        """

        # The model name should be chosen based on what the user wants actually
        model_name = API.perplexity.default_perplexity_model
        endpoint_url = API.perplexity.endpoint_url
        api_key = os.getenv("perplexity_default_key")

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": API.perplexity.system_instruction},
                {"role": "user", "content": search_request},
            ],
            # hardcoding these values for now
            "max_completion_tokens": 4096,
            "temperature": 0.7,
            "return_images": False,
            "return_related_questions": False,
            "top_k": 50,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
            "response_format": None,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.request("POST", endpoint_url, json=payload, headers=headers)

        """
        This is an example of the raw response:

        {
            'id': 'b42deca7-8bf4-45e9-9990-cfcf6889572c', 
            'model': 'sonar', 
            'created': 1757068050, 
            'usage': {
                'prompt_tokens': 145, 
                'completion_tokens': 147, 
                'total_tokens': 292, 
                'search_context_size': 'low', 
                'cost': {
                    'input_tokens_cost': 0.0, 
                    'output_tokens_cost': 0.0, 
                    'request_cost': 0.005, 
                    'total_cost': 0.005
                    }
                }, 
            'citations': [
                'https://sessionize.com/achintya-jai/', 
                'https://cupd2024.calicotab.com/cupd2024/participants/adjudicator/632551/', 
                'https://nasi.org.in/wp-content/uploads/2024/05/ZONE-2024.pdf', 
                'https://nest.owasp.org/members/pUrGe12', 
                'https://github.com/pUrGe12'
                ],
            'search_results': [
                    {
                        'title': "Achintya Jai's Speaker Profile - Sessionize", 
                        'url': 'https://sessionize.com/achintya-jai/', 
                        'date': None, 
                        'last_updated': '2025-09-03', 
                        'snippet': 'Jai is a B.Tech student at IIT Madras and a Google Summer of Code contributor to OWASP Nettacker, where he has been actively developing new features and ...'
                    },
                    {
                        'title': 'CUPD 2024 |',
                        'url': 'https://cupd2024.calicotab.com/cupd2024/participants/adjudicator/632551/', 
                        'date': '2024-01-01', 
                        'last_updated': '2025-04-17', 
                        'snippet': "Achintya Jai is not adjudicating this round. About Achintya Jai. Institution: IIT Madras. Feedback Returns. Achintya Jai doesn't have any feedback to submit."
                    }, 
                    {
                        'title': '[PDF] Zone-wise List of Fellows & Honorary Fellows (2024)',
                        'url': 'https://nasi.org.in/wp-content/uploads/2024/05/ZONE-2024.pdf', 
                        'date': None, 
                        'last_updated': '2025-08-29', 
                        'snippet': 'GOVINDASAMY, Sekar, Professor, Department of Chemistry, IIT Madras, Chennai - 600036;. GOWDA, G.D. Veerappa, Former Professor, TIFR Centre for Application ...'
                    }, 
                    {
                        'title': 'Achintya Jai – OWASP Nest', 
                        'url': 'https://nest.owasp.org/members/pUrGe12', 
                        'date': '2025-08-12', 'last_updated': '2025-09-03', 
                        'snippet': "Summary. Achintya Jai. @pUrGe12. GSoC 25' @OWASP. Contribution Heatmap. Contribution Heatmap. User Details. Joined: Dec 8, 2023. Email: N/A. Company: IIT Madras."
                    }, 
                    {
                        'title': 'Achintya Jai pUrGe12 - GitHub', 
                        'url': 'https://github.com/pUrGe12', 
                        'date': '2024-08-25', 
                        'last_updated': '2025-08-29', 
                        'snippet': 'IIT Madras. Chennai; 22:43 - 5h behind; https://purge12.github.io · in/achintya-jai-887658212 · Achievements · Achievement: Pull Shark x2 · Achievements.'
                    }
                ], 
            'object': 'chat.completion', 
            'choices': [
                    {
                        'index': 0, 
                        'finish_reason': 'stop', 
                        'message': {
                            'role': 'assistant', 
                            'content': 'Achintya Jai is a B.Tech student at IIT Madras who has contributed to OWASP Nettacker as a Google Summer of Code participant, actively developing new features under mentorship. He has experience presenting on AI architectures and debating internationally[1][4]. He is also active on GitHub under the username pUrGe12, affiliated with IIT Madras[5].\n\nAdditional details:\n- Presented at UC Berkeley’s summit on multi-model AI architectures and tools he developed[1].\n- Has debating experience with good communication skills and stage presence[1].\n- Registered as an adjudicator/participant linked to IIT Madras in debating contexts like CUPD 2024 but no feedback submitted[2].'
                            }, 
                        'delta': {
                            'role': 'assistant', 
                            'content': ''
                        }
                    }
                ]
        }

        So out of these we will extract only citations and the overall summary from choices inside message.content
        """

        if response.status_code != 200:
            log.error(f"Error fetching data from Perplexity: {response.text}")
            return None

        data = response.json()

        citations = [str(i).strip() for i in data.get("citations")]
        summary = data.get("choices")[0].get("message").get("content")

        return read_file(Config.path.perplexity_text_output).format(
            citations=citations, summary=summary
        )

    @staticmethod
    def search_perplexity_images(search_request):
        """
        Perform a perplexity API search. The endpoint URL remains the same regardless of the model used.

        Args:
            search_request: This is the query that needs to be passed through to perplexity

        Returns:
            None -> If anything fails ||
            data -> Direct response with no images or anything

        This is specially for getting images from perpelxity. It will return some URLs which can parse and use
        """

        # The model name should be chosen based on what the user wants actually
        model_name = API.perplexity.default_perplexity_model
        endpoint_url = API.perplexity.endpoint_url
        api_key = os.getenv("perplexity_default_key")

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": API.perplexity.system_instruction},
                {"role": "user", "content": search_request},
            ],
            # hardcoding these values for now
            "max_completion_tokens": 4096,
            "temperature": 0.7,
            "return_images": True,
            "return_related_questions": False,
            "top_k": 50,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 1,
            "response_format": None,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.request("POST", endpoint_url, json=payload, headers=headers)

        if response.status_code != 200:
            log.error(f"Error fetching data from Perplexity: {response.text}")
            return None

        data = response.json()

        formatted_data = format_perplexity_image_search_json(data)

        # The formatted data includes which images were downloaded, what they were named and stored in which directory for the model's context
        return formatted_data

    @classmethod
    def get_abbr():
        return "pplxE"
