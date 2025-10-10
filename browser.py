import tkinter
from CSSParser import CSSParser, cascade_priority, style
from HTMLParser import Element, HTMLParser
from url import URL
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
class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            bg="white"
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)

    def scrolldown(self, e):
        max_y = max(self.document.height + 2 * VSTEP - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def scrollup(self, e):
        if self.scroll == 0:
            return
        self.scroll -= SCROLL_STEP
        self.draw()

    def load(self, url):
        body = url.request()
        self.nodes = HTMLParser(body).parse()

        rules = DEFAULT_STYLE_SHEET.copy()
        
        links = [node.attributes['href'] 
                for node in tree_to_list(self.nodes, [])
                if isinstance(node, Element)
                and node.tag == "link"
                and node.attributes.get("rel") == "stylesheet"
                and "href" in node.attributes]

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
        self.draw()


if __name__ == "__main__":
    import sys

    browser = Browser()
    browser.load(URL(sys.argv[1]))
    browser.window.mainloop()
    
