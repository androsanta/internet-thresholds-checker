import json
import logging

import lxml.etree as etree
import requests
from lxml import html
from lxml.builder import E

from internet_checker.database import Reading
from .config import config

logger = logging.getLogger(__name__)

_gateway_base_url = 'http://192.168.1.1'
_gateway_urls = {
    'api_login': f'{_gateway_base_url}/api/user/login',
    'html_connection': f'{_gateway_base_url}/html/mobileconnection.html',
    'api_connection': f'{_gateway_base_url}/api/dialup/connection',
    'html_reboot': f'{_gateway_base_url}/html/reboot.html',
    'api_reboot': f'{_gateway_base_url}/api/device/control'
}
_connection_mode = {
    'auto': 0,  # enabled
    'manual': 1  # disabled
}


def get_reading() -> Reading:
    _api = 'https://apigw.windtre.it'
    _api_login = f'{_api}/api/v1/login/credentials'
    _api_threshold = f'{_api}/piksel/api/offerService/getThreshold'

    with requests.session() as s:
        credentials = {
            'username': config['USERNAME'],
            'password': config['PASSWORD']
        }
        headers = {
            'Content-Type': 'application/json',
            'X-Brand': 'ONEBRAND',
            'X-Wind-Client': 'Web',
        }
        login_response = s.post(_api_login, json.dumps(credentials), headers=headers)

        if not login_response or login_response.json()['status'] == 'FAIL':
            raise Exception(f'Login error, status code {login_response.status_code}')

        auth_token = login_response.headers['X-W3-Token']
        data = {'msisdn': config['MOBILE_NUMBER']}
        headers = {
            'Content-Type': 'application/json',
            'X-Wind-Client': 'Web',
            'Authorization': f'Bearer {auth_token}'
        }
        threshold_response = s.post(_api_threshold, json.dumps(data), headers=headers)

        if not threshold_response:
            raise Exception(f'Error getting threshold, status code {threshold_response.status_code}')

        threshold_res_data = threshold_response.json()
        if not threshold_res_data['success']:
            raise Exception('Internal portal error getting threshold')

        offer = threshold_res_data['response']['threshold'][0]['detailList']['offer'][0]
        initial_amount_mb = float(offer['initialAmount'])
        used_amount_mb = float(offer['usedAmount'])

        total_gb = initial_amount_mb / 1000
        remaining_gb = (initial_amount_mb - used_amount_mb) / 1000
        return Reading(total_gb, remaining_gb)


def _get_token_from_html(content: str):
    parsed_content = html.fromstring(content)
    csrf_tokens = list(map(lambda e: e.attrib['content'],
                           parsed_content.xpath('//meta[@name="csrf_token"]')))
    return csrf_tokens[-1]


def set_mobile_connection(enabled: bool):
    with requests.session() as s:
        mobile_conn_html = s.get(
            _gateway_urls['html_connection']).content
        token = _get_token_from_html(mobile_conn_html)

        connection_mode = _connection_mode['auto' if enabled else 'manual']
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
        res = s.post(
            _gateway_urls['api_connection'], data=req_data,
            headers={
                '__RequestVerificationToken': token,
                'Referer': _gateway_urls['html_connection']
            })

        # todo check also error field inside response
        if not res:
            raise Exception('Connection error')


def get_mobile_connection():
    with requests.session() as s:
        s.get(_gateway_base_url)
        res = s.get(_gateway_urls['api_connection'])
        if not res:
            raise Exception('Connection error')

        res_tree = etree.fromstring(res.content)
        matches = res_tree.xpath('/response/ConnectMode')
        if len(matches) < 1:
            raise Exception('Missing content')

        conn_mode = int(matches[0].text)
        return conn_mode == 0


def reboot():
    with requests.session() as s:
        reboot_html = s.get(_gateway_urls['html_reboot']).content
        token = _get_token_from_html(reboot_html)

        req_data_xml = E.request(E.Control(str(1)))
        req_data = etree.tostring(req_data_xml, xml_declaration=True, encoding='UTF-8')

        res = s.post(
            _gateway_urls['api_reboot'], data=req_data,
            headers={
                '__RequestVerificationToken': token,
                'Referer': _gateway_urls['html_reboot']
            })
        if not res:
            raise Exception('Connection exception')
