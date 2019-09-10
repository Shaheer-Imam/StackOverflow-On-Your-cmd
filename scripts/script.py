import urwid
import re
import sys
import os
from bs4 import BeautifulSoup
import requests
from queue import Queue
from subprocess import PIPE, Popen
from threading import Thread
import webbrowser
import time
from urwid.widget import (BOX, FLOW, FIXED)
import random

SO_URL="https://stackoverflow.com"

# Color codes
GREEN = '\033[92m'
GRAY = '\033[90m'
CYAN = '\033[36m'
RED = '\033[31m'
YELLOW = '\033[33m'
END = '\033[0m'
UNDERLINE = '\033[4m'
BOLD = '\033[1m'

# Scroll actions
SCROLL_LINE_UP = "line up"
SCROLL_LINE_DOWN = "line down"
SCROLL_PAGE_UP = "page up"
SCROLL_PAGE_DOWN = "page down"
SCROLL_TO_TOP = "to top"
SCROLL_TO_END = "to end"

# Scrollbar positions
SCROLLBAR_LEFT = "left"
SCROLLBAR_RIGHT = "right"

USER_AGENTS = [
    "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Firefox/59",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36 OPR/62.0.3331.116'
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
]

def get_lang(file_path):
    if file_path.endswith(".py"):
        return "python3"
    elif file_path.endswith(".class"):
        return "java";
    else:
        return ""

def get_error_msg(error,lang):
    if error=='':
        return None
    elif lang=="python3":
        if any(e in error for in in ["KeyboardInterrupt","SystemExit","GeneratorExit"]):
            return None
        else:
            return error.split('\n')[-2].strip()
    else:
        for line in error.split('\n'):
            m=re.search(r'.*(Exception|Error):(.*)', line)
            if m and m.group(2):
                return m.group(2)
            m=re.search(r'Exception in thread ".*" (.*)', line)
            if m and m.group(1):
                return m.group(1)

        return None

def read(pipe,func):
    for line in iter(pipe.readline,b''):
        for fun in func:
            fun(line.decode("utf-8"))
    pipe.close()

def write(get):
    for line in iter(get,None):
        print(line)

# Main

def execute(command):
    process = Popen(
        command,
        cwd=None,
        shell=False,
        close_fds=True,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=1
    )
    output=[]
    errors=[]
    pipe_queue=Queue()

    stdout_thread=Thread(target=read,args=(process.stdout, [pipe_queue.put, output.append]))
    stderr_thread=Thread(target=read,args=(process.stderr, [pipe_queue.put, errors.append]))

    writer_thread=Thread(target=write,args=(pipe_queue.get,))

    for thread in(stdout_thread, stderr_thread, writer_thread):
        thread.daemon=True
        thread.start()

    process.wait()

    for thread in (stdout_thread,stderr_thread):
        thread.join()

    pipe_queue.put(None)

    output=' '.join(output)
    errors=' '.join(errors)

    if "java"!=command[0] and not os.path.isfile(command[1]):
        return (None,None)
    else:
        return (output,errors)

# Scrapping Part

def style_code(soup):
    style_text=[]
    code_blocks=[block.get_text() for block in soup.find_all("code")]
    blockquotes=[block.get_text() for block in soup.find_all("blockquote")]
    newline=False

    for child in soup.recursiveChildGenerator():
        name=getattr(child,"name",None)
        if name is None:
            if child in code_blocks:
                if newline:
                    style_text.append(("code",u"\n%s" % str(child)))
                    newline=False
                else:
                    style_text.append(("code",u"%s" % str(child)))
            else:
                newline=child.emdswith('\n')
                style_text.append(u"%s" % str(child))
    if type(style_text[-2])==tuple:
        if style_text[-2][1].endswith('\n'):
            style_text[-2]=("code",style_text[-2][1][:-1])
    return urwid.Text(stylized_text)

def get_results(soup):
    search=[]
    for result in soup.find_all("div",class_="question-summary search result"):
        title=result.find_all("div",class_="result-link")[0].find_all("a")[0]
        if result.find_all("div",class_="status answered")!=[]:
            answer_count=int(result.find_all("div",class_="status answered")[0].find_all("strong")[0].text)
        elif result.find_all("div",class_="status answered-accepted")!=[]:
            answer_count=int(result.find_all("div",class_="status answered-accepted")[0].find_all("strong")[0].text)
        else:
            answer_count=0

        search_results.append({
            "Title": title["title"],
            "Answers":answer_count,
            "URL":SO_URL + title["href"]
            })

    return search
                
def souper(url):
    try:
        html=requests.get(url,headers={"User-Agent":random.choice(USER_AGENTS)})
    except requests.exceptions.RequestsException:
        sys.stdout.write("\n%s%s%s" % (RED, "Unable to fetch result from Stack Overflow."
                                            "Make sure your device is connected to internet.\n",END))
        sys.exit(1)

    if re.search("\.com/nocaptcha",html.url):
        return None
    else:
        return BeautifulSoup(html.text,"html.parser")

# Main

def search_stackoverflow(query):
    soup=souper(SO_URL+"/search?pagesize=50&q=%s" % query.replace(' ','+'))
    if soup==None:
        return(None,True)
    else:
        return (get_results(soup),False)

def get_ques_and_ans(url):
    soup=souper(url)
    if soup==None:
        return "Sorry, Stack Overflow blocked our requests. Try agaian"
    else:
        question_title=soup.find_all('a',class_="question-hyperlink")[0].get_text()
        question_stats=soup.find("div",class_="js-vote-count").get_text()
        try:
            question_stats=question_stats+"Votes|"+'|'.join((((soup.find_all("div", class_="module question-stats")[0].get_text())
                                                              .replace('\n',' ')).replace("     "," | ")).split('|')[:2])
        except IndexError:
            question_stats="Could not load Statistics."

        question_desc=style_code(soup.find_all("div", class_="post-text")[0])
        question_stats=' '.join(question_stats.split())

        answers=[style_code(answer) for answer in soup.find_all("div", class_="post-text")][1:]
        if len(answers)==0:
            answers.append(urwid.Text(("no answers", u"\nNo answers for this question.")))

        return question_title,question_desc,question_stats,answers

class Scrollable(urwid.WidgetDecoration):
    def sizing(self):
        return frozenset([BOX,])    
    
    def selectable(self):
        return True

    def __init__(self,widget):
        self._trim_top=0
        self._scroll_action=None
        self._forward_keypress=None
        self._old_cursor_coords=None
        self._rows_max_cached=0
        self._rows_max_displayable=0
        self.__super.__init__(widget)

    def render(seld,size,focus=False):
        maxcol, maxrow=size

        ow=self._original_widget
        ow_size=self._get_original_widget_size(size)
        canv=urwid.CompositeCanvas(ow.render(ow_size,focus))
        canv_cols=canv.cols()
        canv_rows=canv.rows()

        if canv_cols<=maxcol:
            pad_width=maxcol-canv_cols
            if pad_width>0:
                canv.pad_trim_left_right(0,pad_width)

        if canv_rows<=maxrow:
            fill_height=maxrow-canv_rows
            if fill_height>0:
                canv.pad_trim_top_bottom(0,fill_height)
        self._rows_max_displayable=maxrow
        if canv_cols<=maxcol and cav_rows<=maxrow:
            return canv

        self._adjust_trim_top(canv,size)

        trim_top=self._trim_top
        trim_end=canv_rows-maxrow-trip_top
        trim_right=canv_cols-maxcol
        if trim_top>0:
            canv.trim(trim_top)
        if trim_end>0:
            canv.trim_end(trim_end)
        if trim_right>0:
            canv.pad_trim_left_right(0.-trim_right)

        if canv.cursor is not None:
            curscol, cursrow=canv.cursor
            if cursrow>=maxrow or cursrow<0:
                canv.cursor=None

        self._forward_keypress=bool(canv.cursor)

        return canv
    
    def keypress(self,size,key):
        if self._forward_keypress:
            ow=self._original_widget
            ow_size=self._get_original_widget_size(size)

            if hasattr(ow,"get_cursor_coords"):
                self._old_cursor_coords=ow.get_cursor_coords(ow_size)

            key=ow.keypress(ow_size,key)
            if key is None:
                return None

        command_map=self._command_map
        if command_map[key]==urwid.CURSOR_UP:
            self._scroll_action=SCROLL_LINE_UP
        elif command_map[key]==urwid.CURSOR_DOWN:
            self._scroll_action=SCROLL_LINE_DOWN
        elif command_map[key]==urwid.CURSOR_PAGE_UP:
            self._scroll_action=SCROLL_PAGE_UP
        elif command_map[key]==urwid.CURSOR_PAGE_DOWN:
            self._scroll_action=SCROLL_PAGE_DOWN
        elif command_map[key]==urwid.CURSOR_MAX_LEFT:
            self._scroll_action=SCROLL_TO_TOP
        elif command_map[key]==urwid.CURSOR_MAX_RIGHT:
            self._scroll_action=SCROLL_TO_END
        else:
            return key

        self._invalidate()

    def mouse_event(self,size,event,button,col,row,focus):
        ow=self._original_widget
        if hasattr(ow,"mouse_event"):
            ow_size=self._get_original_widget_size(size)
            row+=self._trim_top
            return ow.mouse_event(ow_size,event,button,col,row,focus)
        else:
            return False
        
    def _adjust_trim_top(self,canv,size):
        action=self._scroll_action
        self._scroll_action=None
        maxcol,maxrow=size
        trim_top=self._trim_top
        canv_rows=canv.rows()

        if trim_top<0:
            trim_top=canv_rows-maxrow+trim_top+1

        if canv_rows<=maxrow:
            self._trim_top=0
            return

    def ensure_bounds(new_trip_top):
        return max(0, min(canv_rows-maxrow,new_trim_top)) 
