#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2025/1/16 20:56
# @Site    : 
# @File    : apis.py

import os
import re

import requests

from decorators import *
from encrypt import get_md5, get_sha1, get_base64, get_xencode
from apis import LoginLogger

os.environ['no_proxy'] = 'https://net.szu.edu.cn/'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36'
}


class LoginManager:
    def __init__(self,
                 url_login_page="https://net.szu.edu.cn/srun_portal_pc?theme=proyx",
                 url_get_challenge_api="https://net.szu.edu.cn/cgi-bin/get_challenge",
                 url_login_api="https://net.szu.edu.cn/cgi-bin/srun_portal",
                 n="200",
                 vtype="1",
                 acid="12",
                 enc="srun_bx1"
                 ):
        # urls
        self.url_login_page = url_login_page
        self.url_get_challenge_api = url_get_challenge_api
        self.url_login_api = url_login_api

        # other static parameters
        self.n = n
        self.vtype = vtype
        self.acid = acid
        self.enc = enc

        self.logger = LoginLogger()

    def login(self, username, password):
        self.username = username
        self.password = password

        self.get_ip()
        self.get_token()
        self.get_login_responce()

    def get_ip(self):
        self.logger.info("Step1: Get local ip returned from srun server.")
        self._get_login_page()
        self._resolve_ip_from_login_page()
        self.logger.info("Current IP: " + self.ip)
        self.logger.info("----------------")

    def get_token(self):
        self.logger.info("Step2: Get token by resolving challenge result.")
        self._get_challenge()
        self._resolve_token_from_challenge_response()
        self.logger.info("Current token: " + self.token)
        self.logger.info("----------------")

    def get_login_responce(self):
        self.logger.info("Step3: Loggin and resolve response.")
        self._generate_encrypted_login_info()
        self._send_login_info()
        self._resolve_login_responce()
        self.logger.info("The loggin result is: " + self._login_result)
        self.logger.info("----------------")

    def _is_defined(self, varname):
        """
        Check whether variable is defined in the object
        """
        allvars = vars(self)
        return varname in allvars

    @infomanage(
        callinfo="Getting login page",
        successinfo="Successfully get login page",
        errorinfo="Failed to get login page, maybe the login page url is not correct"
    )
    def _get_login_page(self):
        # Step1: Get login page
        self._page_response = requests.get(self.url_login_page, headers=header)

    @checkvars(
        varlist="_page_response",
        errorinfo="Lack of login page html. Need to run '_get_login_page' in advance to get it"
    )
    @infomanage(
        callinfo="Resolving IP from login page html",
        successinfo="Successfully resolve IP",
        errorinfo="Failed to resolve IP"
    )
    def _resolve_ip_from_login_page(self):
        self.ip = re.search(r'ip\s*:\s*"([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})"',
                            self._page_response.text).group(1)

    @checkip
    @infomanage(
        callinfo="Begin getting challenge",
        successinfo="Challenge response successfully received",
        errorinfo="Failed to get challenge response, maybe the url_get_challenge_api is not correct." \
                  "Else check params_get_challenge"
    )
    def _get_challenge(self):
        """
        The 'get_challenge' request aims to ask the server to generate a token
        """
        params_get_challenge = {
            "callback": "jsonp1583251661367",  # This value can be any string, but cannot be absent
            "username": self.username,
            "ip": self.ip
        }

        self._challenge_response = requests.get(self.url_get_challenge_api, params=params_get_challenge, headers=header)

    @checkvars(
        varlist="_challenge_response",
        errorinfo="Lack of challenge response. Need to run '_get_challenge' in advance"
    )
    @infomanage(
        callinfo="Resolving token from challenge response",
        successinfo="Successfully resolve token",
        errorinfo="Failed to resolve token"
    )
    def _resolve_token_from_challenge_response(self):
        self.token = re.search('"challenge":"(.*?)"', self._challenge_response.text).group(1)

    @checkip
    def _generate_info(self):
        info_params = {
            "username": self.username,
            "password": self.password,
            "ip": self.ip,
            "acid": self.acid,
            "enc_ver": self.enc
        }
        info = re.sub("'", '"', str(info_params))
        self.info = re.sub(" ", '', info)

    @checkinfo
    @checktoken
    def _encrypt_info(self):
        self.encrypted_info = "{SRBX1}" + get_base64(get_xencode(self.info, self.token))

    @checktoken
    def _generate_md5(self):
        self.md5 = get_md5("", self.token)

    @checkmd5
    def _encrypt_md5(self):
        self.encrypted_md5 = "{MD5}" + self.md5

    @checktoken
    @checkip
    @checkencryptedinfo
    def _generate_chksum(self):
        self.chkstr = self.token + self.username
        self.chkstr += self.token + self.md5
        self.chkstr += self.token + self.acid
        self.chkstr += self.token + self.ip
        self.chkstr += self.token + self.n
        self.chkstr += self.token + self.vtype
        self.chkstr += self.token + self.encrypted_info

    @checkchkstr
    def _encrypt_chksum(self):
        self.encrypted_chkstr = get_sha1(self.chkstr)

    def _generate_encrypted_login_info(self):
        self._generate_info()
        self._encrypt_info()
        self._generate_md5()
        self._encrypt_md5()

        self._generate_chksum()
        self._encrypt_chksum()

    @checkip
    @checkencryptedmd5
    @checkencryptedinfo
    @checkencryptedchkstr
    @infomanage(
        callinfo="Begin to send login info",
        successinfo="Login info send successfully",
        errorinfo="Failed to send login info"
    )
    def _send_login_info(self):
        login_info_params = {
            'callback': 'jsonp1583251661368',  # This value can be any string, but cannot be absent
            'action': 'login',
            'username': self.username,
            'password': self.encrypted_md5,
            'ac_id': self.acid,
            'ip': self.ip,
            'info': self.encrypted_info,
            'chksum': self.encrypted_chkstr,
            'n': self.n,
            'type': self.vtype
        }
        self._login_responce = requests.get(self.url_login_api, params=login_info_params, headers=header)

    @checkvars(
        varlist="_login_responce",
        errorinfo="Need _login_responce. Run _send_login_info in advance"
    )
    @infomanage(
        callinfo="Resolving login result",
        successinfo="Login result successfully resolved",
        errorinfo="Cannot resolve login result. Maybe the srun response format is changed"
    )
    def _resolve_login_responce(self):
        self._login_result = re.search('"suc_msg":"(.*?)"', self._login_responce.text).group(1)


if __name__ == '__main__':
    lm = LoginManager()
    lm.get_ip()
    lm.get_token()
