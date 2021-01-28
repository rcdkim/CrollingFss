# -*- coding: utf-8 -*-

"""
Web Crolling Code
ksh, 2021.01.27
rcdkim@yonsei.ac.kr

site : http://www.fss.or.kr/kr/mw/dpc/IFRAME_dpc_l.jsp

※ 해당 사이트에 대하여 특화되서 코드가 제작된 부분이 있음. 해당 부분은 별도로 표시함
※ 코드를 실행하기 전에 크롬의 버전을 확인 한 후 해당 버전의 크롬드라이버를 사전에 다운받아서 코드가 있는 폴더에 넣어야 함
  크롬 드라이버 링크 : https://sites.google.com/a/chromium.org/chromedriver/downloads
"""

import os
import re
from urllib import request
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from selenium import webdriver
import time


class Crolling:
    """
    방향성
    1. 게시판 페이지 번호를 누르고
    2. 해당 페이지의 게시물을 클릭하여
    3. 게시물의 링크주소를 알아내어 txt 파일로 저장하고
    4. 저장된 파일 링크를 기반으로 폴더를 생성하여 파일을 저장한다
    """

    def __init__(self):
        """
        주요 변수 초기화 선언
        """
        self.overlap = []
        self.pageUrl = []
        self.downUrl = []
        self.boardUrl = 'http://www.fss.or.kr/kr/mw/dpc/IFRAME_dpc_l.jsp#1'  # 게시판 링크
        self.site = 'http://www.fss.or.kr/'  # 베이스 링크 (이 뒤로 반복링크가 붙으므로)
        self.rec = "/kr/bbs/iframe/view.jsp?bbsid=1208250172922&idx="  # 페이지를 클릭했을 때 반복되는 부분을 찾기 위한 검색어
        self.dl = "/download.bbs?bbsid"  # 페이지 내 첨부파일 주소가 반복되는 부분 찾기 위한 검색어

        ## ***************************************
        # 중요!!!!!  첨부파일을 저장할 곳 설정
        self.basefolder = "C:\\croll\\"
        ## ***************************************

        # 크롬드라이버를 로드
        self.driver = webdriver.Chrome('chromedriver', options=self.set_crome_option())

        ## 게시물의 링크를 알아낼 때 쓰는 함수 주석 제거 후 사용
        # self.open_board()

        # 게시물링크로 들어가 첨부파일 주소를 알아내고 다운로드 받는 함수
        self.get_down_link()

        self.close()


    def close(self):
        """
        크롬 드라이버 종료함수
        """
        self.driver.quit()

    def set_crome_option(self):
        """
        크롬 드라이버가 화면에 안보이도록 설정
        """
        _options = webdriver.ChromeOptions()
        _options.add_argument('headless')
        # _options.add_argument('window-size=1920x1080')
        return _options

    def open_board(self):
        """
        게시판 페이지를 탐색하여 범위를 인지하고
        각 페이지별로 게시물의 링크를 알아내어
        pagelink.txt 파일에 링크를 저장함
        """
        # 링크를 파일로 저장하기 위하여 txt 파일 생성
        self.fp = open('pagelink.txt', 'w')

        # 초기화 부분에 저장된 self.boardUrl에 저장된 페이지를 최초로 염
        self.driver.get(self.boardUrl)

        # Next를 몇번 누를지 결정
        # 맨마지막 게시물 번호이용하여 다음페이지(예를 들어 10 이상 11페이지로 갈려면 next 버튼을 눌러야 하는데 next 몇번 누를지 결정)
        _iterationTimes = (int(self.driver.find_element_by_xpath('//*[@id="dpcListPrint"]/div[2]/table/tbody/tr[1]/td[1]').text) // 100)

        # 게시물이 10개씩 있는데, 맨 마지막 페이지의 경우 몇개가 있는지 모르니까 마지막 페이지에서 페이지 번호를 몇번 누를지 결정
        # 맨마지막 페이지 모음에 도달하면 게시물 갯수를 이용하여 횟수 결정, 그 외는 페이지 모음당 10개씩 있으니까 10으로 설정
        # TODO 게시물이 1000개 이상이 되면 문제가 생길 것임
        for _i in range(_iterationTimes + 1):
            if _i == _iterationTimes:
                _pageNumber = ((int(self.driver.find_element_by_xpath(
                    '//*[@id="dpcListPrint"]/div[2]/table/tbody/tr[1]/td[1]').text) % 100) // 10) + 1
                self.get_page_link(_pageNumber)
            else:
                _pageNumber = 10
                self.get_page_link(_pageNumber)
                self.driver.find_element_by_xpath('//*[@id="dpcListPrint"]/div[3]/div/a[13]').click()
        self.fp.close()

    def get_page_link(self, n):
        """
        :param n: 페이지모음에서 페이지 번호가 몇개인지
        각 페이지에서 각 게시물을 클릭하여
        소스코드를 열어 href 로 씌여진 링크 주소를 검색하여
        self.rec에 저장된 url 주소가 있는 부분을 색인하여
        메모장에 해당 주소를 저장
        """
        for _i in range(n):
            _page = f'//*[@id="dpcListPrint"]/div[3]/div/a[{_i + 3}]'
            self.driver.find_element_by_xpath(_page).click()

            _source = self.driver.page_source
            _soup = BeautifulSoup(_source, "html.parser")
            _getA = _soup.find_all("a")

            for subpage_link in _getA:
                _data = subpage_link.get('href')
                if self.rec in subpage_link.get("href"):
                    print(self.site + subpage_link.get("href"), file=self.fp)


    def get_down_link(self):
        """
        각 게시물에서 첨부파일 링크를 알아내어
        폴더를 생성하고
        첨부파일을 저장하는 함수
        """

        # 첨부파일 링크를 txt파일로 저장하기 위해
        self.fd = open('downlink.txt', 'w')

        # get_page_link() 함수를 통해 저장한 각 게시물 링크를 기반으로 시작하므로 해당 링크를 열자
        _pagelink = self.file_open('pagelink.txt')

        # pagelink.txt 파일안에 있는 주소 동안에 반복문 실행
        for linkname in _pagelink:
            self.driver.get(linkname)

            # 아래는 게시물의 정보를 파악하기 위해서 변수에 정보를 담는 과정
            _dummy = linkname.find('m=')
            _number = linkname[_dummy + 2:].rstrip()
            _date = (self.driver.find_element_by_xpath('//*[@id="wrapMWfaq"]/div[1]/table/tbody/tr[5]/td[1]').text)[:10]
            _title = self.driver.find_element_by_xpath('//*[@id="wrapMWfaq"]/div[1]/table/tbody/tr[1]/th[2]').text
            _office = self.driver.find_element_by_xpath('//*[@id="wrapMWfaq"]/div[1]/table/tbody/tr[4]/td[1]').text
            _team = self.driver.find_element_by_xpath('//*[@id="wrapMWfaq"]/div[1]/table/tbody/tr[4]/td[2]').text

            _source = self.driver.page_source
            _soup = BeautifulSoup(_source, "html.parser")
            _getA = _soup.find_all("a")

            _paths = self.basefolder + f'{_number} {_date} {_title}'

            # 첨부파일을 저장할 베이스 폴더에 각 게시물 번호 날짜 이름으로 폴더 생성 (없는 경우 생성 있으면 넘어감)
            if not os.path.exists(_paths):
                os.makedirs(_paths)

            print(f'\n{_number}\t{linkname.rstrip().lstrip()}', file=self.fd)

            # 게시물에 들어갔을 때 첨부파일의 주소를 알아내고 해당 파일을 저장
            for getFile in _getA:
                if self.dl in getFile.get('href'):
                    _fileUrl = self.site + getFile.get('href')
                    # 첨부파일 이름을 동일하게 하기 위한 처리
                    _fileOriginalNM = re.sub('<.+?>', '', str(getFile), 0).strip().replace('_', '')
                    print(f'\t\t{_fileUrl}', file=self.fd)

                    # 만약 저장 폴더에 파일이 있는 경우 다시 다운로드 안하기 위해서
                    if os.path.isfile(f'{_paths}\\{_fileOriginalNM}'):
                        print(f"{_number} {_fileOriginalNM} : already exist")
                    else:
                        try:
                            os.chdir(_paths)
                            request.urlretrieve(_fileUrl, _fileOriginalNM)
                            print(f'{_number} {_fileOriginalNM} : download completed\n')
                        except HTTPError as e:
                            print(f'{_number} link error')
        self.fd.close()

    def file_open(self, filename):
        """
        다운로드 링크를 저장한 txt 파일을 읽고 변수화 시킴
        """
        with open(filename) as data:
            lines = data.readlines()
        return lines


if __name__ == "__main__":
    # 위에는 클래스를 만들어 둔거고 클래스를 실행해라

    APPLICATION = Crolling()
