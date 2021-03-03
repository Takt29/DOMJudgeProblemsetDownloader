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

parser = argparse.ArgumentParser(
    description='Download Problemset from DOMJudge')

parser.add_argument('url', type=str, help='DOMJudge URL')
parser.add_argument('-o', '--output', type=str, default='.')


def downloadProblemText(domjudge_url, problemName, problemId):
    text_url = f'{domjudge_url}/public/problems/{problemId}/text'
    return BytesIO(requests.get(text_url).content)


def downloadProblemTexts(domjudge_url, problems, output_dir):
    pdf_merger = PyPDF2.PdfFileMerger()

    for problem in problems:
        pdf_obj = downloadProblemText(
            domjudge_url, problem['name'], problem['id'])

        filepath = os.path.join(output_dir, f'{problem["name"]}.pdf')

        with open(filepath, 'wb') as f:
            f.write(pdf_obj.read())

        pdf_merger.append(filepath)

        print(f'downloaded {filepath}')

        time.sleep(2)

    pdf_merger.write(os.path.join(output_dir, 'all.pdf'))
    pdf_merger.close()


def downloadProblemSample(domjudge_url, problemId, output_dir):
    zip_url = f'{domjudge_url}/public/{problemId}/samples.zip'

    fileSteram = BytesIO(requests.get(zip_url).content)

    zfile = zipfile.ZipFile(fileSteram)
    zfile.extractall(output_dir)


def downloadProblemSamples(domjudge_url, problems, output_dir):
    for problem in problems:
        dir_path = f'{output_dir}/{problem["name"]}'
        os.makedirs(dir_path, exist_ok=True)
        downloadProblemSample(domjudge_url, problem['id'], dir_path)

        print(f'downloaded samples for {problem["name"]}')

        time.sleep(2)


def getProblemList(domjudge_url):
    standings_url = f'{domjudge_url}/public'
    res = requests.get(standings_url)
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

    problems = getProblemList(args.url)

    print(f'problems: {len(problems)}')

    texts_dir = os.path.join(args.output, 'pdf')
    samples_dir = os.path.join(args.output, 'samples')

    os.makedirs(texts_dir, exist_ok=True)
    downloadProblemTexts(args.url, problems, texts_dir)

    os.makedirs(samples_dir, exist_ok=True)
    downloadProblemSamples(args.url, problems, samples_dir)