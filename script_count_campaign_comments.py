from lib.autobrowser import *
import traceback

with open('data/campaign_url.txt', 'r') as r:
    review_urls = r.readlines()

excluded_names = ['小不列颠晒晒君', 'Freyacxr']

class DMCommentsCounter:

    def __init__(self, writer):
        self.writer = writer
        self._browser = browser_setup(headless_mode=True)
        self.pointer = -1
        self.prev_url = ''
        
    def go_to_next_url(self):
        self.pointer += 1
        url = review_urls[self.pointer].strip()
        print(url+' -> ')
        if not url:
            self.writer.write('0\n')
            self.go_to_next_url()
            return
        if url == self.prev_url:
            return
        self._browser.get(url)
        if not wait_until_visible(self._browser, By.CLASS_NAME, 'dm-cmt-group-title',time_to_wait=5):
            self.writer.write('wrong url\n')
            self.go_to_next_url()
            return
        self.prev_url = url

    def get_comment_count(self):
        ele = self._browser.find_elements_by_class_name('dm-cmt-user')
        names = []
        if not ele:
            self.writer.write('no result\n')
            print('no result.')
            return
        for e in ele:
            text = e.text #type: str
            if text.startswith('@'):
                text = text[1:]
            if text in excluded_names or text in names:
                continue
            names.append(text)
        c = len(names)
        print(c)
        self.writer.write(str(c) + '\n')

w = open('dmcc_result.txt', 'w')
dmcc = DMCommentsCounter(w)
try:
    while dmcc.pointer < len(review_urls):
        dmcc.go_to_next_url()
        dmcc.get_comment_count()
except:
    pass
finally:
    traceback.print_exc()
    w.close()