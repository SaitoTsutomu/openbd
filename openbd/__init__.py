import sys
from collections import namedtuple

import requests

# see pyproject.toml
__version__ = "0.0.3"
__author__ = "Saito Tsutomu <tsutomu7@hotmail.co.jp>"


def get(dc, path):
    keys = path.split("/")
    try:
        for key in keys:
            if key.startswith("#"):
                dc = dc[int(key[1:])]
            else:
                dc = dc[key]
    except:
        return None
    return dc


def drop_none(iterable, func=None, *args, **kwargs):
    if not func:
        func = lambda x: x
    return [func(i, *args, **kwargs) for i in iterable if i]


def get_person(data, key2, key3):
    name = get(data, key2)
    roles = get(data, key3)
    if not name or not roles:
        return
    role = "・".join(drop_none(map(_dcp.get, roles)))
    return f"{name}／{role}"


def get_authors(data, key1, key2, key3):
    lst = get(data, key1)
    if not lst:
        return None
    return "、".join(drop_none(lst, get_person, key2, key3))


def get_publish(data, key1, key2, dup):
    p1 = get(data, key1)
    p2 = get(data, key2)
    return "／".join(drop_none([p1, "" if not dup and p2 == p1 else p2]))


def get_date(s):
    return f"{s[:4]}/{s[4:6]}/{s[6:8]}" if s else None


def get_price(data, key1, key2, key3):
    dc = get(data, key1) or {}
    crncy = dc.get(key3, "")
    return dc.get(key2, "") + ("円" if crncy == "JPY" else crncy)


def book_info(isbn, has_data=False, dup=False):
    _req = requests.get("https://api.openbd.jp/v1/get?isbn=" + isbn)
    if _req.status_code != 200:
        return None
    data = _req.json()
    onix = get(data, "#0/onix")
    isbn_ = get(onix, "RecordReference")
    _desc = get(onix, "DescriptiveDetail")
    title = get(_desc, "TitleDetail/TitleElement/TitleText/content")
    subtitle = get(_desc, "TitleDetail/TitleElement/Subtitle/content")
    series = get(_desc, "Collection/TitleDetail/TitleElement/#0/TitleText/content")
    authors = get_authors(
        onix, "DescriptiveDetail/Contributor", "PersonName/content", "ContributorRole"
    )
    _pub = get(onix, "PublishingDetail")
    publish = get_publish(_pub, "Imprint/ImprintName", "Publisher/PublisherName", dup)
    date = get_date(get(_pub, "PublishingDate/#0/Date"))
    price = get_price(
        onix, "ProductSupply/SupplyDetail/Price/#0", "PriceAmount", "CurrencyCode"
    )
    page = get(_desc, "Extent/#0/ExtentValue")
    size = _dcs.get(get(_desc, "ProductFormDetail"))
    _det = get(onix, "CollateralDetail")
    content = get(_det, "TextContent/#0/Text")
    image = get(_det, "SupportingResource/#0/ResourceVersion/#0/ResourceLink")
    return BookInfo(
        isbn_,
        title,
        subtitle,
        series,
        authors,
        publish,
        date,
        price,
        page,
        size,
        content,
        image,
        data if has_data else None,
    )


_dcp = {
    "A01": "著",
    "B01": "編集",
    "B20": "監修",
    "B06": "翻訳",
    "A12": "イラスト",
    "A38": "原著",
    "A10": "企画原案",
    "A08": "写真",
    "A21": "解説",
    "E07": "朗読",
}
_dcs = {
    "B108": "A5判",
    "B109": "B5判",
    "B110": "B6判",
    "B111": "文庫",
    "B112": "新書",
    "B119": "四六判",
    "B120": "四六変形",
    "B121": "A4判",
    "B122": "A4変形",
    "B123": "A5変形",
    "B124": "B5変形",
    "B125": "B6変形",
    "B126": "AB判",
    "B127": "B7判",
    "B128": "菊判",
    "B129": "菊変形",
    "B130": "B4判",
}
_names = (
    "isbn title subtitle series authors publish date price page size content image data"
)
BookInfo = namedtuple("BookInfo", _names.split())


def main():
    if len(sys.argv) > 1:
        print(book_info(sys.argv[1]))
    else:
        print("usage: openbd isbn")
