"""Stage case variants of the Meridian entry route for static GitHub Pages."""
import base64
from hashlib import sha256
from itertools import product
from pathlib import Path
import sys

CANONICAL_DIRECTORY = 'Meridian'
CANONICAL_PATH = '/' + CANONICAL_DIRECTORY + '/'
REDIRECT = f'location.replace("{CANONICAL_PATH}" + location.search + location.hash);'
SCRIPT_HASH = base64.b64encode(sha256(REDIRECT.encode()).digest()).decode()
ALIAS_HTML = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-{SCRIPT_HASH}'; base-uri 'none'; form-action 'none'">
  <title>Meridian</title>
  <link rel="canonical" href="https://arbiterforge.com{CANONICAL_PATH}">
  <script>{REDIRECT}</script>
  <noscript><meta http-equiv="refresh" content="0;url={CANONICAL_PATH}"></noscript>
</head>
<body><p><a href="{CANONICAL_PATH}">Open Meridian</a></p></body>
</html>
'''.encode()


def stage_aliases(destination):
    spellings = product(*((letter.lower(), letter.upper()) for letter in CANONICAL_DIRECTORY))
    for letters in spellings:
        spelling = ''.join(letters)
        if spelling == CANONICAL_DIRECTORY:
            continue
        directory = destination / spelling
        directory.mkdir(parents=True)
        (directory / 'index.html').write_bytes(ALIAS_HTML)


if __name__ == '__main__':
    stage_aliases(Path(sys.argv[1]))
