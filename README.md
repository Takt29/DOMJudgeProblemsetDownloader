# DOMJudge Problemset Downloader

Download problemset(texts and samples) from DOMJudge.

## Dependencies

```
pip install beautifulsoup4 requests PyPDF2
```

## Usage

```
usage: downloader.py [-h] [-o OUTPUT_DIR] [-u USERNAME] [-p PASSWORD] url
```

### example

```
./downloader.py https://judge.example.com -o ./problemset
./downloader.py https://judge.example.com -u team1 -p p4ssw0rd -o ./problemset
```