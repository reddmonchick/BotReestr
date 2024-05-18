from src.dto import FiltersParser


class Nopriz:


    def create_excel_file(self, filterdto: FiltersParser):
        pass


    def parse(self, filterdto: FiltersParser):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Origin': 'https://reestr.nopriz.ru',
            'Connection': 'keep-alive',
            'Referer': 'https://reestr.nopriz.ru/',
            # 'Cookie': 'BITRIX_SM_GUEST_ID=2592147; BITRIX_SM_LAST_VISIT=17.05.2024%2023%3A24%3A43; BITRIX_SM_LAST_ADV=5_Y; _ym_uid=170358633291607385; _ym_d=1712579416; _ym_isad=1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=1',
        }

        json_data = {
            'filters': {
                'state': [
                    'disabled',
                ],
                'registry_registration_date': [
                    '2024-05-18',
                ],
                'suspension_date': [
                    '2024-05-18',
                    '2024-05-31',
                ],
            },
            'page': 1,
            'pageCount': '100',
            'sortBy': {
                'registry_registration_date': 'DESC',
                'director': 'ASC',
            },
        }

        if filterdto.

        response = requests.post('https://reestr.nopriz.ru/api/sro/all/member/list', cookies=cookies, headers=headers,
                                 json=json_data)