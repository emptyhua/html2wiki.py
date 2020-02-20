#!/usr/bin/env python3
import os
import sys
import re
import argparse
from urllib.parse import urlparse
from urllib.parse import urljoin
import html

import requests
from lxml import etree


class HTML2Wiki:

    re_trimspace = re.compile(r'\s+')
    re_htag = re.compile(r'^h([1-6])$')
    newlinetags  = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'pre', 'blockquote', 'section']
    keeptags = ['pre', 'q', 'u', 'del', 'code', 'blockquote']
    tableattrs = ['scope', 'colspan', 'rowspan']
    mimemap = {
            'image/bmp':'.bmp',
            'image/tiff':'.tiff',
            'image/x-icon':'.icon',
            'image/jpeg':'.jpg',
            'image/jpg':'.jpg',
            'image/png':'.png',
            'image/gif':'.gif',
            'image/webp':'.webp',
            'image/svg+xml':'.svg',
            }

    def __init__(self,
                url = '',
                useragent = None,
                removelinks = False,
                image_save_dir=None,
                image_name_template=None):

        self.url = url
        self.useragent = useragent
        self.removelinks = removelinks

        self.imageindex = 0
        self.image_save_dir = image_save_dir
        self.image_name_template = image_name_template

        self.liststack = []

    def parse_element(self, el):
        out = self.html_to_wiki(el)
        return out

    def download_image(self, url):
        self.imageindex += 1
        url = urljoin(self.url, url)

        path = urlparse(url).path
        basename = path[path.rfind('/')+1:]
        name, ext = os.path.splitext(basename)
        ext = ext.lower()

        headers = {}
        if self.useragent is not None:
            headers['User-Agent'] = self.useragent

        r = requests.get(url, headers=headers)
        if ext == '':
            mime = r.headers['content-type']
            ext = self.mimemap.get(mime) or ''

        filename = self.image_name_template.format(i=self.imageindex, name=name, ext=ext)
        filepath = os.path.join(self.image_save_dir, filename)

        if not os.path.isfile(filepath):
            with open(filepath, "wb") as fp:
                fp.write(r.content)

        return filename

    def html_to_wiki(self, el):
        out = ''
        end = ''

        if not isinstance(el.tag, str):
            return ''
        elif el.tag == 'a' and not self.removelinks and 'href' in el.attrib and el.find('img') is None:
            out += '[' + urljoin(self.url, el.attrib['href']) + ' '
            end = ']'
        elif el.tag == 'img':
            src = ''
            if 'data-src' in el.attrib:
                src = el.attrib['data-src']
            elif 'data-original-src' in el.attrib:
                src = el.attrib['data-original-src']
            elif 'src' in el.attrib:
                src = el.attrib['src']

            if src != '':
                if self.image_save_dir is not None:
                    name = self.download_image(src)
                    out += '[[File:' + name + ']]'
                else:
                    path = urlparse(src).path
                    basename = path[path.rfind('/')+1:]
                    out += '[[File:' + basename + ']]'
        elif el.tag == 'strong':
            out += "'''"
            end = "'''"
        elif el.tag == 'hr':
            out += '\n----\n'
        elif el.tag == 'ol':
            self.liststack.append('#')
        elif el.tag == 'ul':
            self.liststack.append('*')
        elif el.tag == 'li':
            out += ''.join(self.liststack) + ' '
        elif el.tag == 'table':
            out += '{|\n'
            end = '|}\n'
        elif el.tag == 'tr':
            n = el.getnext()
            while n is not None:
                if n.tag == 'tr':
                    out += '|-\n';
                    break
                n = n.getnext()
        elif el.tag == 'th' or el.tag == 'td':
            if el.tag == 'th':
                out += '!'
            elif el.tag == 'td':
                out += '|'

            attrs = ''
            for attr in self.tableattrs:
                if attr in el.attrib:
                    attrs += ' ' + attr + '="' + html.escape(el.attrib[attr]) + '"'

            if len(attrs):
                out += attrs
                out += '|'

            end = '\n'
        elif el.tag in self.keeptags:
            out += '<' + el.tag + '>'
            end = '</' + el.tag + '>'
        else:
            m = self.re_htag.match(el.tag)
            if m is not None:
                end = '=' * int(m.group(1))
                out += end

        if el.text is not None:
            if el.tag == 'pre':
                out += el.text
            else:
                text = self.re_trimspace.sub(' ', el.text)
                if text != ' ':
                    out += text

        if el.tag == 'li':
            out += "\n"

        for child in el.iterchildren():
            out += self.html_to_wiki(child)

        out += end

        if el.tag == 'ol' or el.tag == 'ul':
            self.liststack.pop()

        if el.tag in self.newlinetags:
            out += "\n\n"

        if el.tail is not None:
            text = self.re_trimspace.sub(' ', el.tail)
            if text != ' ':
                out += text

        return out

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
