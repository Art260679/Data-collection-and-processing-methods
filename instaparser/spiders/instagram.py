# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstagramItem


def fetch_csrf_token(text):
    matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
    return matched.split(':').pop().replace(r'"', '')


def fetch_user_id(text, username):
    matched = re.search(
        '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
    ).group()
    return json.loads(matched).get('id')


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = "artemmaiun"
    insta_pass = "#PWD_INSTAGRAM_BROWSER:10:1591722117:AUBQADIcrhyTHgb0+N/xydK3nvVQRQ4AY1m5x2bW44r1NCZjBPMiaISNA3VnmJkZYQcB1eURLEFG9lchtB60F3qEQ+NpAQDxceZ5ugkqkPouwVS3M5tB2qiZXvwwPrcyvDSS7J74r8S5EoYaua0="
    inst_login_link = 'https://instagram.com/accounts/login/ajax/'

    hash_followers = '7c8a1055f69ff97dc201e752cf6f0093'
    hash_following = 'd04b0a864b4b54837c0d870b0e77e076'
    graphql_link = 'https://www.instagram.com/graphql/query/?'

    def __init__(self, parser_user):
        self.parser_user = parser_user

    def parse(self, response):
        csrf_token = fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.authenticated_user,
            formdata={
                'username': self.insta_login,
                'enc_password': self.insta_pass
            },
            headers={'X-CSRFToken': csrf_token}
        )

    def authenticated_user(self, response):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parser_user:
                yield response.follow(
                    f'/{user}',
                    callback=self.data_user,
                    cb_kwargs={'user': user}
                )

    def data_user(self, response: HtmlResponse, user):
        user_id = fetch_user_id(response.text, user)
        variables = {"id": user_id,
                     "first": 50
                     }
        url_followers = f'{self.graphql_link}query_hash={self.hash_followers}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.followers_parse,
            cb_kwargs={'user_id': user_id,
                       'variables': deepcopy(variables)
                       }
        )

        url_following = f'{self.graphql_link}query_hash={self.hash_following}&{urlencode(variables)}'
        yield response.follow(
            url_following,
            callback=self.following_parse,
            cb_kwargs={'user_id': user_id,
                       'variables': deepcopy(variables)
                       }

        )

    def followers_parse(self, response, user_id, variables):
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_followers = f'{self.graphql_link}query_hash={self.hash_followers}&{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        followers = j_body.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            item = InstagramItem(
                followers_of=user_id,
                name=self.parser_user,
                id=follower['node']['id'],
                username=follower['node']['username'],
                fullname=follower['node']['full_name'],
                pic_url=follower['node']['profile_pic_url'],
                status='followers'
            )

            yield item

    def following_parse(self, response, user_id, variables):
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_follow').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_following = f'{self.graphql_link}query_hash={self.hash_following}&{urlencode(variables)}'

            yield response.follow(
                url_following,
                callback=self.following_parse,
                cb_kwargs={'user_id': user_id,
                           'variables': deepcopy(variables)}
            )

        followers = j_body.get('data').get('user').get('edge_follow').get('edges')
        for follower in followers:
            item = InstagramItem(
                followed_by=user_id,
                name=self.parser_user,
                id=follower['node']['id'],
                username=follower['node']['username'],
                fullname=follower['node']['full_name'],
                pic_url=follower['node']['profile_pic_url'],
                status='followed_by'
            )

            yield item
