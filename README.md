# Usage
```
usage: url2wiki.py [-h] [-removelinks] [-downimage] [-imagename IMAGENAME]
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
# Example
```bash
mkdir ./bluehua.org
python3 ./url2wiki.py "https://bluehua.org" "//div[contains(@class,'post')]" ./bluehua.org/index.txt -removelinks -downimage -imagename "bluehua-{i}{ext}"
```
