# DOMJudge Problemset Downloader

Download problemset(texts and samples) from DOMJudge.

## Dependencies

```
pip install beautifulsoup4 requests PyPDF2
```

## Usage

```
usage: downloader.py [-h] [-o OUTPUT] url
```

### example

```
./downloader.py https://judge.example.com -o ./problemset
```