from CSSParser import CSSParser, cascade_priority, style
from HTMLParser import Element, HTMLParser, Text
from DocumentLayout import DocumentLayout

WIDTH = 800
HEIGHT = 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()


def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list


class Tab:
    def __init__(self, tab_height):
        self.url = None
        self.scroll = 0
        self.tab_height = tab_height
        self.history = []

    def click(self, x, y):
        y += self.scroll
        objs = [
            obj
            for obj in tree_to_list(self.document, [])
            if obj.x <= x < obj.x + obj.width and obj.y <= y < obj.y + obj.height
        ]

        if not objs:
            return
        elt = objs[-1].node
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elt = elt.parent

    def draw(self, canvas, offset):
        for cmd in self.display_list:
            if cmd.rect.top > self.scroll + self.tab_height:
                continue
            if cmd.rect.bottom < self.scroll:
                continue
            cmd.execute(self.scroll - offset, canvas)

    def scrolldown(self):
        max_y = max(self.document.height + 2 * VSTEP - self.tab_height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    def scrollup(self):
        if self.scroll == 0:
            return
        self.scroll -= SCROLL_STEP

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)

    def load(self, url):
        body = url.request()
        self.url = url
        self.history.append(url)
        self.nodes = HTMLParser(body).parse()

        rules = DEFAULT_STYLE_SHEET.copy()

        links = [
            node.attributes["href"]
            for node in tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]

        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except:
                continue
            rules.extend(CSSParser(body).parse())

        style(self.nodes, sorted(rules, key=cascade_priority))

        self.document = DocumentLayout(self.nodes)
        self.document.layout()

        self.display_list = []
        paint_tree(self.document, self.display_list)
