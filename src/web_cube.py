import base64
import hashlib
import logging
import re
from datetime import datetime
from typing import Optional, Dict

import lxml.etree as etree
import requests
from lxml import html
from lxml.builder import E

from config import config
from src.database import Reading

logger = logging.getLogger(__name__)


def catch_connection_exception(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError:
            raise WebCubeException.connection_exception()

    return wrap


class WebCubeException(Exception):
    @classmethod
    def connection_exception(cls):
        return cls('Error during http connection')

    @classmethod
    def missing_content_exception(cls):
        return cls('Response page does not contain Remaining data info')


class _WebCube:
    _username = config['web_cube_username']
    _password = config['web_cube_password']

    _remaining_base_url = 'http://internet.tre.it'
    _remaining_api_url = f'{_remaining_base_url}/calls/checkMSISDN.aspx'

    _connection_mode = {
        'auto': 0,
        'manual': 1
    }

    _gateway_base_url = 'http://192.168.1.1'
    _gateway_urls = {
        'api_login': f'{_gateway_base_url}/api/user/login',
        'html_connection': f'{_gateway_base_url}/html/mobileconnection.html',
        'api_connection': f'{_gateway_base_url}/api/dialup/connection'
    }

    def __init__(self):
        try:
            requests.get('https://www.google.com')
        except requests.exceptions.ConnectionError:
            self._connection_enabled = False
            logger.info('Network Unreachable, WebCube defaulted to connection disabled')
        else:
            self._connection_enabled = True
            logger.info('Network Reachable, WebCube defaulted to connection enabled')

    @property
    def connection_enabled(self):
        return self._connection_enabled

    @connection_enabled.setter
    def connection_enabled(self, enabled: bool):
        if enabled == self._connection_enabled:
            logger.info(f'Connection already set to {enabled}')
            return

        self._set_mobile_connection(enabled)
        self._connection_enabled = enabled
        logger.info(f'Connection set to {enabled}')

    def get_remaining_data(self) -> Reading:
        remaining_data = self._get_remaining_data()
        return Reading(remaining_data['remaining_gb'], remaining_data['total_gb'])

    @classmethod
    @catch_connection_exception
    def _get_remaining_data(cls) -> Optional[Dict[str, float]]:
        # get main page
        main_page = requests.get(cls._remaining_base_url).content
        main_html = html.fromstring(main_page)

        # get guid variable from script tag
        scripts: list = main_html.xpath('//script[@type="text/javascript"]')

        non_empty_contents = map(lambda s: s.text, filter(lambda s: s.text, scripts))

        guid_re = re.compile(r"var guid = '(\d+)'")
        results = list(filter(lambda x: x, map(guid_re.search, non_empty_contents)))

        if len(results) <= 0:
            raise WebCubeException.missing_content_exception()

        guid = results[0].group(1)

        # get variables from iframe
        iframe = main_html.xpath('//iframe[@id="ifrEnrichment"]')[0]
        iframe_page = requests.get(iframe.attrib['src']).content
        iframe_html = html.fromstring(iframe_page)

        iframe_script = iframe_html.xpath('//script[@type="text/javascript"]')[0]
        match = re.search(r"parent.push\('', '(\d+)', '(.+)'\)", iframe_script.text)

        current_mc = match.group(1)
        encoded_h = match.group(2)
        campaign_id = 0

        now = datetime.utcnow()
        timestamp = str(int(datetime.timestamp(now)))

        # get info request
        check_response = requests.get(
            cls._remaining_api_url,
            params={
                'g': guid,
                'h': encoded_h,
                'mc': current_mc,
                'acid': campaign_id,
                '_': timestamp
            },
            headers={'Referer': cls._remaining_base_url})
        data = check_response.json()['RemaningData']

        if not data['remaning'] or not data['total']:
            raise WebCubeException.missing_content_exception()

        return {
            'remaining_gb': float(data['remaning']) / 1000,
            'total_gb': float(data['total']) / 1000
        }

    @classmethod
    @catch_connection_exception
    def _get_login_session(cls) -> requests.Session:
        s = requests.Session()
        home_html = s.get(cls._gateway_base_url).content
        token = _WebCube._get_token_from_html(home_html)

        def b64_sha256(value: str) -> str:
            sha256 = hashlib.sha256(value.encode())
            return base64.b64encode(sha256.hexdigest().encode()).decode()

        encoded_password = b64_sha256(cls._username + b64_sha256(cls._password) + token)

        req_data = etree.tostring(
            E.request(
                E.Username(cls._username),
                E.Password(encoded_password),
                E.password_type(str(4))
            ),
            xml_declaration=True, encoding='UTF-8')

        s.post(
            cls._gateway_urls['api_login'],
            headers={
                '__RequestVerificationToken': token,
                'Referer': f'{cls._gateway_base_url}/html/home.html'
            },
            data=req_data)

        return s

    @classmethod
    @catch_connection_exception
    def _set_mobile_connection(cls, enabled: bool):
        session = cls._get_login_session()

        mobile_conn_html = session.get(cls._gateway_urls['html_connection']).content
        token = cls._get_token_from_html(mobile_conn_html)

        connection_mode = cls._connection_mode['auto' if enabled else 'manual']
        connection_mode_req = E.request(
            E.RoamAutoConnectEnable(str(0)),
            E.MaxIdelTime(str(600)),
            E.ConnectMode(str(connection_mode)),
            E.MTU(str(1440)),
            E.auto_dial_switch(str(1)),
            E.pdp_always_on(str(0))
        )

        req_data = etree.tostring(
            connection_mode_req, xml_declaration=True, encoding='UTF-8')
        res = session.post(
            cls._gateway_urls['api_connection'], data=req_data,
            headers={
                '__RequestVerificationToken': token,
                'Referer': cls._gateway_urls['html_connection']
            })
        if not res:
            raise WebCubeException.connection_exception()

    @staticmethod
    def _get_token_from_html(content: str):
        parsed_content = html.fromstring(content)
        csrf_tokens = list(map(lambda e: e.attrib['content'],
                               parsed_content.xpath('//meta[@name="csrf_token"]')))
        return csrf_tokens[-1]


web_cube = _WebCube()
