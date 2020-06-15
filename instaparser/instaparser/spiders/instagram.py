# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem
from scrapy.loader import ItemLoader


def fetch_csrf_token(text):
    matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
    return matched.split(':').pop().replace(r'"', '')


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = "artemmaiun"
    insta_pass = "#PWD_INSTAGRAM_BROWSER:10:1591722117:AUBQADIcrhyTHgb0+N/xydK3nvVQRQ4AY1m5x2bW44r1NCZjBPMiaISNA3VnmJkZYQcB1eURLEFG9lchtB60F3qEQ+NpAQDxceZ5ugkqkPouwVS3M5tB2qiZXvwwPrcyvDSS7J74r8S5EoYaua0="
    inst_login_link = 'https://instagram.com/accounts/login/ajax/'

    hash_followers = 'c76146de99bb02f6415203be841dd25a'
    hash_following = 'd04b0a864b4b54837c0d870b0e77e076'
    graphql_link = 'https://www.instagram.com/graphql/query/?'

    collection = None  # for the name of the collection

    def __init__(self, users):
        self.users_list = users

    def parse(self, response):
        csrf_token = fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.parse_user,
            formdata={'username': self.insta_login,
                      'enc_password': self.insta_pass},
            headers={'X-CSRFToken': csrf_token}
        )

    def parse_user(self, response):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.users_list:
                self.collection = user
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse
                )

    def user_data_parse(self, response: HtmlResponse):
        user_parser = response.xpath("//script[contains(text(), 'csrf_token')]").extract_first()[52:-10]
        user_parser = json.loads(user_parser)['entry_data']['ProfilePage'][0]['graphql']['user']

        variables = {"id": user_parser['id'],
                     "first": 50
                     }

        url_followers = f'{self.graphql_link}query_hash={self.hash_followers}&{urlencode(variables)}'

        yield response.follow(
            url_followers,
            callback=self.subscribers_parse,
            cb_kwargs={'variables': deepcopy(variables)}
        )


    def subscribers_parse(self, response, variables):
        j_body = json.loads(response.text)
        next_page_subscribers = j_body['data']['user']['edge_followed_by']['page_info']
        followers = j_body['data']['user']['edge_followed_by']['edges']
        for follower in followers:
            loader = ItemLoader(item=InstaparserItem())
            loader.add_value('_id', follower['node']['id'])
            loader.add_value('username', follower['node']['username'])
            loader.add_value('full_name', follower['node']['full_name'])
            loader.add_value('is_private', follower['node']['is_private'])
            loader.add_value('profile_pic_url', follower['node']['profile_pic_url'])
            loader.add_value('type_user', 'subscribers')
            yield loader.load_item()

            if next_page_subscribers.get('has_next_page'):
                variables['after'] = next_page_subscribers['end_cursor']

                url_posts = f'{self.graphql_link}query_hash={self.hash_followers}&{urlencode(variables)}'
                yield response.follow(
                    url_posts,
                    callback=self.subscribers_parse,
                    cb_kwargs={'variables': deepcopy(variables)}
                )
            else:
                url_posts = f'{self.graphql_link}query_hash={self.hash_following}&{urlencode(variables)}'
                yield response.follow(
                    url_posts,
                    callback=self.subscriptions_parse,
                    cb_kwargs={'variables': deepcopy(variables)}
                )

    def subscriptions_parse(self, response, variables):
        j_body = json.loads(response.text)
        next_page = j_body['data']['user']['edge_follow']['page_info']
        followings = j_body['data']['user']['edge_follow']['edges']
        for following in followings:
            loader = ItemLoader(item=InstaparserItem())
            loader.add_value('_id', following['node']['id'])
            loader.add_value('username', following['node']['username'])
            loader.add_value('full_name', following['node']['full_name'])
            loader.add_value('is_private', following['node']['is_private'])
            loader.add_value('profile_pic_url', following['node']['profile_pic_url'])
            loader.add_value('type_user', 'subscriptions')
            yield loader.load_item()

            if next_page.get('has_next_page'):
                variables['after'] = next_page['end_cursor']

                url_posts = f'{self.graphql_link}query_hash={self.hash_following}&{urlencode(variables)}'
                yield response.follow(
                    url_posts,
                    callback=self.subscribers_parse,
                    cb_kwargs={'variables': deepcopy(variables)}
                )
