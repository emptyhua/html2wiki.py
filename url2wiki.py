#!/usr/bin/env python3
import os
import sys
import re
import argparse
from urllib.parse import urlparse
from urllib.parse import urljoin
import requests
from lxml import etree
from html2wiki import HTML2Wiki


if __name__ == '__main__':

    imagenameformat = '''
image name template marks:
{i}\t index of the image
{ext}\t extension of the image: .jpg .png .gif ...
{name}\t image name without extension
    '''
    parser = argparse.ArgumentParser(epilog=imagenameformat, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('url', help='url or article')
    parser.add_argument('xpath', help='xpath of article')
    parser.add_argument('output', help='output name')
    parser.add_argument('-removelinks', action='store_true', help='remove links')
    parser.add_argument('-downimage', action='store_true', help='download images')
    parser.add_argument('-imagename', help='image name template')
    parser.add_argument('-useragent', help='useragent')

    parser.set_defaults(downimage=False,
            removelinks=False,
            imagename='{name}{ext}',
            useragent='Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/60'
            )
    args = parser.parse_args()

    imagedir = None
    if args.downimage:
        imagedir = os.path.dirname(args.output)
    h2w = HTML2Wiki(url=args.url,
                useragent=args.useragent,
                removelinks=args.removelinks,
                image_save_dir=imagedir,
                image_name_template=args.imagename)

    headers = {"User-Agent":args.useragent}
    r = requests.get(args.url, headers=headers)
    html_root = etree.HTML(r.text)

    els = html_root.xpath(args.xpath)
    out = ''
    for el in els:
        out += h2w.parse_element(el)
        out += "\n"
    out = re.sub(r'\n{3,}', '\n\n', out)

    with open(args.output, 'w') as fp:
        fp.write(out)
