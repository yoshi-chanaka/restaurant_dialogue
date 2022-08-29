# -*- coding: utf-8 -*-

import time
import requests
import json
import re
import MeCab

HOTPEPPER_API_KEY = "xxxxxxxxxx"


class HotpepperApi:

    api = "http://webservice.recruit.co.jp/hotpepper/gourmet/v1/?key={key}&lat={lat}&lng={lng}&range=2&order=1&format=json"

    def __init__(self, api_key):
        self.api_key = api_key

    def collect_shop_list(self, lat, lng, num_return=100, range=3):

        url = self.api.format(key=self.api_key, lat=lat, lng=lng)
        shop_list, num_shop_available = [], 0

        while len(shop_list) < num_return:

            query = {
                'key': self.api_key,
                'start': len(shop_list) + 1,
                'count': 100,
                'format': 'json',
                'range': range
            }

            response = requests.get(url, query)
            time.sleep(2)

            results = json.loads(response.text)['results']
            num_shop_available = results['results_available']
            num_return = min(num_shop_available, num_return)

            shop_list += results['shop']

        return shop_list


def extract_morph_info(line):
    """
    形態素解析の結果を辞書型の変数に整理して返す
    """
    morph_info_dict = {}
    morph_info_dict['surface'], info = line.split('\t', 1)
    info_splitted = info.split(',')
    morph_info_dict['pos'] = info_splitted[0]
    morph_info_dict['pos1'] = info_splitted[1]
    morph_info_dict['base'] = info_splitted[6]

    return morph_info_dict


def process_catch_text(input_text):
    """
    catchの前処理. 名詞のみ残す
    """
    input_text = re.sub(r'\s', '', input_text)
    tagger = MeCab.Tagger()
    wakati_res = tagger.parse(input_text)

    catch = []
    for line in wakati_res.split('\n'):

        line = line.strip()
        if line and line != 'EOS':

            morph_info_dict = extract_morph_info(line)
            pos     = morph_info_dict['pos']
            pos1    = morph_info_dict['pos1']
            base    = morph_info_dict['base']
            if (pos == '名詞') and (pos1 in ['一般', '固有名詞']) and (base != '*'):
                catch.append(base)

    return catch


if __name__ == "__main__":

    positions = {
        '電気通信大学': ('35.656068', '139.5440491'),
        '調布駅': ('35.6518205', '139.5446124'),
        'つつじヶ丘駅': ('35.6580629', '139.5752686'),
        '国領駅': ('35.6502086', '139.5584334'),
        '府中駅': ('35.6701251', '139.4937559'),
        '新宿駅': ('35.690921', '139.70025799999996'),
        '八王子駅': ('35.6554856', '139.3391012'),
        '長野駅': ('36.6444757', '138.1886261'),
        '北海道駅': ('43.068564', '141.3507138'),
        '京都駅': ('34.7024', '135.4959'),
        '金沢駅': ('36.5780818', '136.6478206'),
        '名古屋駅': ('35.1706431', '136.8816945')
    }

    hotpepper_api = HotpepperApi(HOTPEPPER_API_KEY)
    remove_genres = ['カラオケ・パーティ', 'カフェ・スイーツ', 'バー・カクテル', '居酒屋']

    save_path = '../data/restaurants.tsv'
    f = open(save_path, 'w')
    f.write('name\tgenre\tcatch\tcatch_processed\tplace\turl\n')
    for place, (lat, lon) in positions.items():

        print(place, lat, lon)
        shop_list = hotpepper_api.collect_shop_list(lat, lon, num_return=2000)

        for i, shop in enumerate(shop_list):
            catch = shop['catch'] + ' ' + shop['genre']['catch']
            catch_processed = process_catch_text(catch.replace('料理', ''))
            remove_words_list = [
                '居酒屋', '個室', '宴会', '店', 'メニュー', 'おすすめ', 'コース',
                'コロナ', '対策', '東口', '西口', '南口', '北口', '全席'
            ]
            for rm_word in remove_words_list:
                while rm_word in catch_processed:
                    catch_processed.remove(rm_word)
            genre = shop['genre']['name']
            name = shop['name']
            url = shop['urls']['pc']

            # print([name, genre, catch, ' '.join(catch_processed), place, url])
            if (len(catch_processed) >= 3) and (genre not in remove_genres):
                f.write('\t'.join([name, genre, catch, ' '.join(catch_processed), place, url]) + '\n')

    f.close()
