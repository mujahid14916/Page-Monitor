import requests
import os
from pyquery import PyQuery
from time import sleep, ctime
from threading import Thread
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk


def create_obj(win_root, win_url, selector, interval, text):
    ob = SearchWindow(win_root, win_url, selector, interval, text)
    ob.monitor_page()


def start(event=None):
    global root, input_url, input_minutes, input_text, input_tags, error_label
    url_value = input_url.get()
    tags_value = input_tags.get()
    text_value = input_text.get()
    error_label.config(text='')
    if url_value:
        try:
            min_value = float(input_minutes.get()) * 60.0 if input_minutes.get() != '' else 60
            t = Thread(target=create_obj, args=(root,
                                                url_value,
                                                tags_value,
                                                min_value,
                                                text_value)
                       )
            t.setDaemon(True)
            t.start()
        except ValueError:
            error_label.config(text='Update Interval can only be numbers')


class SearchWindow:
    def __init__(self, win_root, win_url, selector, interval, text):
        self.root = Toplevel(win_root)
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.iconbitmap(os.path.join(os.getcwd(), 'icon.ico'))
        self.url = win_url
        self.time = interval
        self.text = text
        self.selector = selector if selector != '' else 'body'
        self.content = ScrolledText(self.root, width=50, height=15)
        self.info = ttk.Label(self.root, justify=LEFT)
        self.label_msg = ttk.Label(self.root, justify=LEFT)
        self.retry_btn = ttk.Button(self.root, text='Retry', command=self.retry, padding=5)
        self.status = ttk.Label(self.root, anchor=CENTER, font="16", foreground="white", padding=5)
        self.repeat = True
        self._create_widget()
        if self.time < 30:
            self.time = 30
        if self.text == '':
            self.text = 'none'

    def _create_widget(self):
        if self.text:
            self.root.title(self.text.capitalize())
        else:
            self.root.title(self.url)
        self.info.config(text='URL: '
                         + self.url + '\n'
                         + 'Selector: '
                         + self.selector)
        self.content.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.status.pack(fill=X, side=BOTTOM)
        self.retry_btn.pack(fill=X, side=BOTTOM)
        self.label_msg.pack(fill=X, padx=10, pady=10, side=BOTTOM)
        self.info.pack(fill=X, padx=10, pady=10, side=BOTTOM)

    def quit(self):
        self.repeat = False
        self.root.destroy()

    def retry(self):
        t = Thread(target=self.monitor_page)
        t.setDaemon(True)
        t.start()

    def monitor_page(self):
        update_msg = ''
        found_msg = ''
        old_item_list = []
        headers = {"Accept-Language": "en-US, en; q=0.5"}
        self.retry_btn.state(['disabled'])
        self.status.config(text='Status: Running', background='green')
        while self.repeat:
            new_item_list = []
            items = ''
            msg = ''
            page_updated = False

            try:
                html = requests.get(self.url, headers=headers).text
                elements = PyQuery(html)
                selected_elements = elements(self.selector)

                title = elements('title').text()
                if self.text != 'none':
                    title += ' (' + self.text.capitalize() + ')'
                if title != '':
                    self.root.title(title)

                for item in selected_elements:
                    if item.text_content().strip() not in old_item_list:
                        new_item_list.append(item.text_content().strip())
                        page_updated = True

                old_item_list = new_item_list + old_item_list

                pad = len(str(len(old_item_list)))
                for i, name in enumerate(old_item_list):
                    items += '{0:0{1}d}. {2}\n'.format((i + 1),pad, name)

                self.content.config(state='normal')
                self.content.delete('1.0', END)
                self.content.insert(INSERT, items)

                msg += 'Search String: {}\n'.format(self.text.capitalize())

                if page_updated:
                    update_msg = 'Page Updated at {}'.format(ctime())
                    if items.lower().find(self.text) >= 0 and self.text != 'none':
                        found_msg = self.text.capitalize() + ' found'
                    self.root.deiconify()

                msg += update_msg + '\n'
                msg += found_msg + '\n'
                msg += "{}. Page is visited every {:0.2f} minutes.".format(ctime(), self.time / 60)
                self.label_msg.config(text=msg)
            except requests.RequestException as e:
                self.content.config(state='normal')
                self.content.delete('1.0', END)
                self.content.insert(INSERT, str(e))
                self.status.config(text='Status: Stopped', background='red')
                self.retry_btn.state(['!disabled'])
                self.root.deiconify()
                break
            finally:
                self.content.config(state='disable')
            sleep(self.time)


root = Tk()
root.title('Monitor Page')
root.iconbitmap(os.path.join(os.getcwd(), 'icon.ico'))

url = ttk.Label(root, text='URL to monitor:')
url.grid(row=0, column=0, padx=10, pady=10, sticky='we')

input_url = ttk.Entry(root, width=40)
input_url.focus()
input_url.grid(row=0, column=1, padx=10, pady=10)

tags = ttk.Label(root, text='CSS Selector')
tags.grid(row=1, column=0, padx=10, pady=10, sticky='we')

input_tags = ttk.Entry(root, width=40)
input_tags.grid(row=1, column=1, padx=10, pady=10)

minutes = ttk.Label(root, text='Update Interval (min):')
minutes.grid(row=2, column=0, padx=10, pady=10, sticky='we')

input_minutes = ttk.Entry(root, width=40)
input_minutes.grid(row=2, column=1, padx=10, pady=10)

search = ttk.Label(root, text='Search Text:')
search.grid(row=3, column=0, padx=10, pady=10, sticky='we')

input_text = ttk.Entry(root, width=40)
input_text.grid(row=3, column=1, padx=10, pady=10)

frame = ttk.Frame(root, height=100)
frame.grid(row=4, column=0, columnspan=2)
startBtn = ttk.Button(frame, command=start, text='Start')
startBtn.bind('<Return>', start)
startBtn.pack(padx=10, pady=10)

error_label = ttk.Label(root, foreground='red')
error_label.grid(row=5, column=0, columnspan=2)

if __name__ == '__main__':
    root.mainloop()
