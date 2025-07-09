"""
Import as:

import ck_marketing.linkedin.phantombuster_api as cmliphap
"""

import io
import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import requests

import helpers.hdbg as hdbg
import helpers.hio as hio

_LOG = logging.getLogger(__name__)


# #############################################################################
# Phantom
# #############################################################################


class Phantom:

    def __init__(self) -> None:
        """
        Initialize the Phantom class with the provided API key.

        This method sets up the necessary headers for making API
        requests to the PhantomBuster service using the provided API
        key.

        :param api_key: api key for accessing the PhantomBuster API.
        """
        self.api_key = os.getenv("Phantom_API_KEY")
        self.headers = {
            "X-Phantombuster-Key-1": self.api_key,
            "Content-Type": "application/json",
        }

    def create_sales_nav_phantom(
        self,
        agent_name: str,
        sales_nav_query: str,
        linkedin_session_cookie: str,
    ) -> Dict:
        """
        Create a Sales Navigator Phantom with the provided search query and
        LinkedIn session cookie.

        Phantom link: "https://phantombuster.com/automations/sales-navigator/6988/sales-navigator-search-export"
        - The phantom is used to scrape and export the results of a Sales Navigator search into a spreadsheet
        - eg: give sales navigation query and extract all profiles with available info into a sheet.

        :param sales_nav_query: sales Navigator search query URL.
        :param linkedin_session_cookie: linkedIn session cookie.
        :return: response from the PhantomBuster API.
        """
        url = "https://api.phantombuster.com/api/v2/agents/save"
        payload = {
            "argument": {
                "numberOfProfiles": 2500,
                "numberOfResultsPerSearch": 2500,
                "numberOfLinesPerLaunch": 10,
                "removeDuplicateProfiles": True,
                "searches": sales_nav_query,
                "sessionCookie": linkedin_session_cookie,
            },
            "org": "phantombuster",
            "script": "Sales Navigator Search Export.js",
            "branch": "master",
            "environment": "release",
            "name": agent_name,
            "fileMgmt": "delete",
            "launchType": "manually",
            "nbLaunches": 2,
            "lastEndType": "finished",
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def create_linkedIn_info_extractor_phantom(
        self, gsheet_url: str, agent_name: str, linkedin_session_cookie: str
    ):
        """
        Create and configure a LinkedIn Search Export Phantom to extract
        profile info (whatever is present on LinkedIn) from linkedin urls.

        phantom link = ""
        - This phantom is used to scrape all the available data from LinkedIn profiles, including emails.
        - eg: give profiles with linkedIn url and extract info available on linkedIn including mails.

        :param api_key: Phantombuster API key
        :param gsheet_url: URL of the Google Sheet containing LinkedIn
            search URLs
        :param phantom_name: Name of the Phantom to create
        :return: Details of the created Phantom
        """
        url = "https://api.phantombuster.com/api/v2/agents/save"
        payload = {
            "argument": {
                "spreadsheetUrl": gsheet_url,
                "sessionCookie": linkedin_session_cookie,
                "numberOfProfilesPerSearch": 10000,
            },
            "org": "phantombuster",
            "name": agent_name,
            "script": "LinkedIn Profile Scraper.js",
            "branch": "master",
            "environment": "release",
            "fileMgmt": "delete",
            "launchType": "manually",
            "nbLaunches": 2,
            "lastEndType": "finished",
        }
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            linkedin_resp = response.json()
        else:
            raise Exception(
                f"Error creating Phantom: {response.status_code} {response.text}"
            )
        return linkedin_resp

    def create_linkedIn_url_finder_phantom(
        self, agent_name: str, gsheet_url: str, linkedin_session_cookie: str
    ):
        """
        Create and configure a Phantom to find LinkedIn profile URLs based on a
        Google Sheet.

        phantom link = "https://phantombuster.com/automations/linkedin/4015/linkedin-profile-url-finder"
        - The phantom is used to find LinkedIn profiles from your prospect list. This tool inputs from Google Sheets and integrates with HubSpot.
        - eg: Give full names and het linkedIn urls back.

        :param agent_name: name of the Phantom to create
        :param gsheet_url: url of the Google Sheet containing names
            (must have a "fullName" column) and sheet should have open
            access
        :param linkedin_session_cookie: linkedIn session cookie (li_at)
            for authentication
        :return: details of the created Phantom
        """
        url = "https://api.phantombuster.com/api/v2/agents/save"
        payload = {
            "argument": {
                "spreadsheetUrl": gsheet_url,
                "nameColumn": "fullName",
                "sessionCookie": linkedin_session_cookie,
            },
            "org": "phantombuster",
            "name": agent_name,
            "script": "LinkedIn URL Finder.js",
            "branch": "master",
            "environment": "release",
            "fileMgmt": "delete",
            "launchType": "manually",
            "nbLaunches": 2,
            "lastEndType": "finished",
        }
        response = requests.post(url, json=payload, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f"Error creating Phantom: {response.status_code} {response.text}"
            )

    def delete_phantom(self, agent_id: str) -> None:
        """
        Delete a Phantom by its agent ID.

        PB dashboard link: "https://phantombuster.com/8472730339660855/phantoms"

        :param agent_id: phantom agent to be deleted.
        :return: response from the PhantomBuster API.
        """
        url = "https://api.phantombuster.com/api/v2/agents/delete"
        payload = {"id": agent_id}
        response = requests.post(url, json=payload, headers=self.headers)
        hdbg.dassert_eq(
            response.status_code,
            200,
            f"Deletion failed for Phantom ID {agent_id}. Response: {response.text}",
        )
        _LOG.info(
            "Successfully deleted phantom %s. Response: %s",
            agent_id,
            response.text,
        )

    def get_all_agents(self) -> List:
        """
        Fetch all agents from the PhantomBuster API.

        This method sends a GET request to the PhantomBuster API to
        retrieve a list of all agents associated with the account linked
        to the provided API key. It returns the list of agents or raises
        an exception if the request fails.

        :return: A list of dictionaries, each containing information
            about an agent.
        :raises Exception: If the API request fails or the response
            format is unexpected.
        """
        url = "https://api.phantombuster.com/api/v2/agents/fetch-all"
        response = requests.get(url, headers=self.headers)
        response_data = response.json()
        response_dataa = None
        if isinstance(response_data, list):
            response_dataa = response_data
            return response_dataa
        if "status" in response_data and response_data["status"] == "success":
            response_dataa = response_data["data"]
            return response_dataa
        raise RuntimeError(f"Failed to get agents:  {response_data}")

    def get_agent_name(self, agent_id: str) -> str:
        """
        Retrieve the name of a specific agent given its ID.

        This method iterates through the list of all agents to find the
        agent with the specified ID and returns its name. If the agent
        is not found, it raises an exception.

        :param agent_id: The ID of the agent whose name is to be
            retrieved.
        :return: The name of the agent with the specified ID.
        :raises Exception: If the agent with the given ID is not found.
        """
        agents = self.get_all_agents()
        for agent in agents:
            if agent["id"] == agent_id:
                return agent["name"]
        raise ValueError("Agent with ID %s not found" % agent_id)

    def launch_agent(self, agent_id: str) -> Dict:
        """
        Launch a specific agent by its ID.

        This method sends a POST request to the PhantomBuster API to
        launch the specified agent. It returns the response JSON
        containing details of the launched agent.

        :param agent_id: The ID of the agent to be launched.
        :return: A dictionary containing the response JSON with details
            of the launched agent.
        :raises Exception: If the launch request fails.
        """
        url = "https://api.phantombuster.com/api/v2/agents/launch"
        payload = {"id": agent_id}
        response = requests.post(url, headers=self.headers, json=payload)
        response_json = response.json()
        hdbg.dassert_in(
            "containerId",
            response_json,
            msg=f"Failed to launch agent: {response_json}",
        )
        return response_json

    def launch_and_get_df(self, agent_id: str) -> pd.DataFrame:
        ress = self.launch_agent(agent_id)
        _LOG.debug(ress)
        time.sleep(10)
        result_response_json = self.fetch_agent_results(agent_id)
        time.sleep(10)
        csv_url = self.get_csv_url(result_response_json.get("output", ""))
        df = self.download_csv(csv_url)
        df = df.replace([np.nan, np.inf, -np.inf], "", inplace=False)
        return df

    def fetch_agent_results(self, agent_id: str) -> Dict:
        """
        Fetch the results of a specific agent after it has been launched.

        This method continuously polls the PhantomBuster API to check if
        the agent has finished running. Once the agent is no longer
        running, it returns the output JSON.

        :param agent_id: iD of the agent whose results are to be
            fetched.
        :return: dictionary containing the results of the agent.
        :raises Exception: error fetching the agent's results.
        """
        url = "https://api.phantombuster.com/api/v2/agents/fetch-output"
        while True:
            response = requests.get(
                url, headers=self.headers, params={"id": agent_id}
            )
            response_json = response.json()
            if response_json.get("status") == "error":
                raise Exception("Error fetching the agent's results")
            if not response_json.get("isAgentRunning", True):
                print("Agent finished running")
                return response_json
            print("Agent still running, waiting for 30 seconds...")
            print("wait..")
            time.sleep(30)

    def get_csv_url(self, output_text: str) -> str:
        """
        Extract the CSV URL from the agent's output text.

        This method uses a regular expression to find the first
        occurrence of a URL ending with 'result.csv' in the provided
        output text. It returns the extracted URL or raises an exception
        if no URL is found.

        :param output_text: The text output from which to extract the
            CSV URL.
        :return: The extracted CSV URL.
        :raises Exception: If no CSV URL is found in the output text.
        """
        csv_url_match = re.search(r"https://[^\s]+/result\.csv", output_text)
        hdbg.dassert(
            csv_url_match is not None,
            msg="No CSV URL found in the output",
        )
        return csv_url_match.group(0)

    def download_csv(self, csv_url: str) -> pd.DataFrame:
        """
        Download a CSV file from a given URL and loads it into a pandas
        DataFrame.

        This method sends a GET request to the specified CSV URL,
        decodes the content, and reads it into a pandas DataFrame.

        :param csv_url: The URL of the CSV file to be downloaded.
        :return: A pandas DataFrame containing the data from the CSV
            file.
        :raises Exception: If the CSV download or parsing fails.
        """
        response = requests.get(csv_url)
        csv_content = response.content.decode("utf-8")
        return pd.read_csv(io.StringIO(csv_content))

    def get_all_phantoms(self) -> Optional[pd.DataFrame]:
        """
        Retrieve all the names and IDs of the Phantoms from Phantombuster.

        :return: a dataframe containing the all Phantoms information,
            or None if the request failed
        Example of the return dataframe:
        # pylint: disable=line-too-long
        ```
                      id            name scriptId ... lastEndStatus queuedContainers runningContainers
        2862499141527492   Search Export     6988           success                0                 0
        3593602419926765 Profile Scraper     3112           success                0                 0
        3933308360008191 Profile Scraper     3112           success                0                 0
        # pylint: enable=line-too-long
        ```
        """
        data = self._get_phantom_data()

        if data and "data" in data and "agents" in data["data"]:
            return pd.DataFrame(data["data"]["agents"])
        #
        _LOG.error("The data structure is invalid: Phantoms not found.")
        return None

    def download_result_csv_by_phantom_id(
        self, phantom_id: str, output_path: str
    ) -> None:
        """
        Download result CSV by phantom ID.

        :param phantom_id: The ID of the phantom for which to fetch the
            result CSV
        :param output_path: The path to save the result CSV
        """
        result_url = self._get_result_csv_by_phantom_id(phantom_id)
        if result_url:
            self._download_result_csv_to_local(result_url, output_path)

    # #########################################################################

    @staticmethod
    def _download_result_csv_to_local(
        result_csv_url: str, output_path: str
    ) -> None:
        """
        Download result CSV from Phantombuster server to local storage.

        :param result_csv_url: The URL of the result CSV
        :param output_path: The path to save the result CSV
        """
        hio.create_enclosing_dir(output_path, incremental=True)
        try:
            response = requests.get(result_csv_url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            _LOG.error("%s", e)
            return None
        response.encoding = "UTF-8"
        hio.to_file(output_path, response.text)
        _LOG.info("Result CSV saved to %s", output_path)
        return None

    @staticmethod
    def _extract_result_csv_url(response_text: str) -> str:
        """
        Extract the result CSV URL from the response text.

        :param response_text: The response text from Phantom API
            containers/fetch-output
        :return: a string containing the result CSV url, or None if
            there is no result CSV url
        """
        data = json.loads(response_text)
        output = data["output"]
        csv_url = re.search("CSV saved at (https://[^\\s]+)", output)
        if csv_url:
            csv_url = csv_url.group(1)
        else:
            raise ValueError(
                f"Unable to find the result CSV URL in the response: {output}"
            )
        return csv_url

    # #########################################################################
    # Private functions.
    # #########################################################################

    def _get_result_csv_by_phantom_id(self, phantom_id: str) -> str:
        """
        Get result CSV by Phantom id.

        :param phantom_id: The id of the phantom for which to fetch the
            result CSV
        :return: a string containing the result CSV url, or None if
            there is no result CSV url
        """
        containers_id = self._get_all_containers_id_by_phantom_id(phantom_id)
        hdbg.dassert_is(
            containers_id,
            None,
            "There is no container id available. Have you run the Phantom?",
            only_warning=False,
        )
        # Get the last container ID, which is from the first time Phantom ran.
        # Later runs might not provide the CSV link if there's no new data.
        # We use the first run to ensure we obtain the CSV link, which remains
        # consistent across all containers of a Phantom.
        container_to_process = containers_id[-1]
        #
        result_csv_url = self._get_result_csv_by_container_id(
            container_to_process
        )
        hdbg.dassert(result_csv_url is not None, "Failed to fetch result CSV.")
        #
        return result_csv_url

    def _get_all_containers_id_by_phantom_id(
        self, phantom_id: str
    ) -> Optional[List[str]]:
        """
        Get all container IDs by the Phantom ID.

        Containers represent the executions of a Phantom. Each time a
        Phantom runs, a new container is created. Thus, if you run a
        Phantom 10 times, you will have 10 containers. Every container
        has a unique container ID.

        :param phantom_id: The ID of the phantom for which to get
            containers
        :return: a list containing all containers id, or None if the
            request failed
        """
        url = f"https://api.phantombuster.com/api/v2/containers/fetch-all?agentId={phantom_id}"
        response = self._get_api_response(url)
        if response is None:
            return None
        #
        data = response.json().get("containers", [])
        containers_id = [container["id"] for container in data]
        #
        return containers_id

    def _get_result_csv_by_container_id(self, container_id: str) -> Optional[str]:
        """
        Get result CSV url by container id.

        :param container_id: The id of the container for which to fetch
            the result CSV
        :return: a string containing the result CSV url, or None if
            there is no result CSV url
        """
        url = f"https://api.phantombuster.com/api/v2/containers/fetch-output?id={container_id}"
        response = self._get_api_response(url)
        if response is None:
            return None
        # Extract the result CSV URL from the response text.
        result_csv_url = self._extract_result_csv_url(response.text)
        if result_csv_url:
            _LOG.info("Result CSV URL: %s", result_csv_url)
            return result_csv_url
        return None

    def _get_phantom_data(self) -> Optional[Dict[str, Any]]:
        """
        Get all Phantoms information from Phantombuster.

        :return: a dictionary containing all Phantoms information

        Example of the returned data:
        ```
        {'status': 'success',
         'data': {'email': 'saggese@gmail.com',
          'timeLeft': 72000,
          'emailsLeft': 100,
          'storageLeft': 993000000,
          'captchasLeft': 1000,
          'databaseLeft': 0,
          'agents': [{'id': 3593602419926765,
            'name': 'Yiyun LinkedIn Profile Scraper',
            'scriptId': 3112,
            'lastEndMessage': '',
            'lastEndStatus': 'success',
            'queuedContainers': 0,
            'runningContainers': 0},
           {'id': 4809903115550081,
            'name': 'Retired MBA DC UMD LinkedIn Search Export',
            'scriptId': 3149,
            'lastEndMessage': '',
            'lastEndStatus': 'success',
            'queuedContainers': 0,
            'runningContainers': 0}]}}
        ```
        """
        url = "https://api.phantombuster.com/api/v1/user"
        response = self._get_api_response(url)
        if response is None:
            return None
        return response.json()

    def _get_api_response(self, url: str) -> Optional[requests.Response]:
        """
        Get API response data.

        :param url: The url of the API request
        :return: a dictionary containing the API response data, or None
            if the request failed
        """
        headers = {
            "accept": "application/json",
            "X-Phantombuster-Key": self.api_key,
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response
