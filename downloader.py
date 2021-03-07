#! /usr/bin/env python3

import os
import re
import requests
import PyPDF2
import time
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup
import argparse
import mimetypes

parser = argparse.ArgumentParser(
    description='Download problemset from DOMJudge')

parser.add_argument('url', type=str, help='DOMJudge URL')
parser.add_argument('-o', '--output', type=str,
                    default='.', metavar='OUTPUT_DIR')
parser.add_argument('-u', '--username', type=str, help='username for DOMJudge')
parser.add_argument('-p', '--password', type=str, help='password for DOMJudge')


class DOMJudgeConnector:
    session = None
    loggedin = False
    host = None

    def __init__(self, host, username=None, password=None):
        self.host = host
        self.session = requests.Session()

        if username and password:
            r = self.login(username, password)

            if r.status_code != requests.codes.ok:
                print('Login failed')
                exit(1)

            print('Successfully logged in')
            self.loggedin = True

    def login(self, username, password):
        url = f'{self.host}/login'

        r = self.session.get(url)

        soup = BeautifulSoup(r.content, 'html.parser')

        csrf = soup.find('input', attrs={'name': '_csrf_token'})['value']

        return self.session.post(f'{self.host}/login', data={
            "_csrf_token": csrf,
            "_username": username,
            "_password": password,
        }, headers=dict(Referer=url))

    def getProblemText(self, problemId):
        if self.loggedin:
            url = f'{self.host}/team/problems/{problemId}/text'
        else:
            url = f'{self.host}/public/problems/{problemId}/text'

        return self.session.get(url)

    def getProblemList(self):
        if self.loggedin:
            url = f'{self.host}/team/scoreboard'
        else:
            url = f'{self.host}/public'

        return self.session.get(url)

    def getProblemSample(self, problemId):
        if self.loggedin:
            url = f'{self.host}/team/{problemId}/samples.zip'
        else:
            url = f'{self.host}/public/{problemId}/samples.zip'

        return self.session.get(url)


def downloadProblemText(conn, problemName, problemId, file_dir):
    r = conn.getProblemText(problemId)

    ext = mimetypes.guess_extension(r.headers['content-type'].split(';')[0])

    file_path = os.path.join(file_dir, f'{problemName}{ext}')

    with open(file_path, 'wb') as f:
        f.write(r.content)

    return file_path


def downloadProblemTexts(conn, problems, output_dir):
    text_paths = []

    for problem in problems:
        file_path = downloadProblemText(
            conn, problem['name'], problem['id'], output_dir)

        text_paths.append(file_path)

        print(f'downloaded {file_path}')

        time.sleep(2)

    try:
        pdf_merger = PyPDF2.PdfFileMerger()
        for path in text_paths:
            pdf_merger.append(path, import_bookmarks=False)

        pdf_merger.write(os.path.join(output_dir, 'all.pdf'))
        pdf_merger.close()
    except:
        print('failed to merge texts')


def downloadProblemSample(conn, problemId, output_dir):
    fileSteram = BytesIO(conn.getProblemSample(problemId).content)

    zfile = zipfile.ZipFile(fileSteram)
    zfile.extractall(output_dir)


def downloadProblemSamples(conn, problems, output_dir):
    for problem in problems:
        dir_path = f'{output_dir}/{problem["name"]}'
        os.makedirs(dir_path, exist_ok=True)
        downloadProblemSample(conn, problem['id'], dir_path)

        print(f'downloaded samples for {problem["name"]}')

        time.sleep(2)


def getProblemList(conn):
    res = conn.getProblemList()

    soup = BeautifulSoup(res.content, 'html.parser')

    header = soup.find(class_='scoreheader')

    problems = []

    for elem in header.find_all('th'):
        title = elem['title']

        if title and re.match(r'^problem', title):
            a_elem = elem.find('a')
            href = a_elem['href']
            problemId = re.search(r'/([0-9]+)/', href).group(1)
            problemName = a_elem.text.strip()
            problems.append({
                'name': problemName,
                'id': problemId,
            })

    return problems


if __name__ == '__main__':
    args = parser.parse_args()

    conn = DOMJudgeConnector(args.url, args.username, args.password)

    problems = getProblemList(conn)

    print(f'problems: {len(problems)}')

    texts_dir = os.path.join(args.output, 'pdf')
    samples_dir = os.path.join(args.output, 'samples')

    os.makedirs(texts_dir, exist_ok=True)
    downloadProblemTexts(conn, problems, texts_dir)

    os.makedirs(samples_dir, exist_ok=True)
    downloadProblemSamples(conn, problems, samples_dir)
