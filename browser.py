import tkinter

from tab import Tab
from url import URL


WIDTH = 800
HEIGHT = 600

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT,
            bg="white",
        )
        self.canvas.pack()
        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<Up>", self.handle_up)
        self.window.bind("<Button-1>", self.handle_click)
        self.tabs = []
        self.active_tab = None
    
    def handle_down(self, e):
        self.active_tab.scrolldown()
        self.draw()

    def handle_up(self, e):
        self.active_tab.scrollup()
        self.draw()

    def handle_click(self, e):
        self.active_tab.click(e.x, e.y)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas)

    def new_tab(self, url):
        new_tab = Tab()
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

if __name__ == "__main__":
    import sys
    Browser().new_tab(URL(sys.argv[1]))
    tkinter.mainloop()