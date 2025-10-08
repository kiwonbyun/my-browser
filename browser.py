import tkinter
from HTMLParser import HTMLParser, print_tree
from url import URL
from DocumentLayout import DocumentLayout

WIDTH = 800
HEIGHT = 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())
        
    for child in layout_object.children:
        paint_tree(child, display_list)

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
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
        print(self.nodes)
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
    
