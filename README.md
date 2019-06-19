# html2wiki.py
convert html to mediawiki format
```
usage: html2wiki.py [-h] [-removelinks] [-downimage] [-imagename IMAGENAME]
                    [-useragent USERAGENT]
                    url xpath output

positional arguments:
  url                   url or article
  xpath                 xpath of article
  output                output name

optional arguments:
  -h, --help            show this help message and exit
  -removelinks          remove links
  -downimage            download images
  -imagename IMAGENAME  image name template
  -useragent USERAGENT  useragent

image name template marks:
{i}	 index of the image
{ext}	 extension of the image: .jpg .png .gif ...
{name}	 image name without extension
```
