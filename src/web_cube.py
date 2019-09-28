import re
from datetime import datetime
from functools import partial

import requests
from lxml import html

_base_url = 'http://internet.tre.it'
_get_info_url = f'{_base_url}/calls/checkMSISDN.aspx'


def get_remaining_data() -> dict:
    # get main page
    main_page = requests.get(_base_url).content
    main_html = html.fromstring(main_page)

    # get guid variable from script tag
    scripts: list = main_html.xpath('//script[@type="text/javascript"]')

    non_empty_contents = list(map(lambda s: s.text, filter(lambda s: s.text, scripts)))
    guid_search = partial(re.search, r"var guid = '(\d+)'")
    results = list(filter(lambda x: x, map(guid_search, non_empty_contents)))

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
    params = {
        'g': guid,
        'h': encoded_h,
        'mc': current_mc,
        'acid': campaign_id,
        '_': timestamp
    }
    headers = {'Referer': _base_url}

    check_response = requests.get(_get_info_url, params=params, headers=headers)
    data = check_response.json()['RemaningData']

    return {
        'remaining': data['remaning'],
        'total': data['total']
    }
