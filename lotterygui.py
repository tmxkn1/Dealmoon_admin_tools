from lottery.lottery import DMLottery, PrizeType
from tkinter.font import Font
import tkinter as tk
from tkinter import StringVar, ttk, messagebox, filedialog, IntVar
from typing import List
import json

VERSION_MAJOR = 1
VERSION_MINOR = 1
VERSION_PATCH = 0
app_version = (f'v{VERSION_MAJOR}.{VERSION_MINOR:0>2}.{VERSION_PATCH}')

BG = 'white'
FG = '#4b6584'
FG_HL = '#FC5C65'
PADDING_X = 10
PADDING_Y = 10
PADDING_Y_COMPACT = 5
PADDING_X_CLOSE = 2.5
PADDING_SANDWICHED = (PADDING_X_CLOSE, PADDING_X_CLOSE)
PADDING_X_LABEL = (PADDING_X, PADDING_X_CLOSE)
PADDING_X_BACK_LABEL = (PADDING_X_CLOSE, PADDING_X)
PADDING_X_AFTER_LABEL = (PADDING_X_CLOSE, PADDING_X)
CN_FONT = ('PingFang SC', 10, 'normal')


def config_style():
    style = ttk.Style()
    style.configure('.', background=BG, foreground=FG)
    style.configure('TFrame', background=BG, borderwidth=2)
    style.configure('CN.TLabel', font=CN_FONT)
    style.configure('CN.TCombobox', font=CN_FONT)
    style.configure('Heading.TLabel', background=BG, foreground=FG_HL)


class DMLotteryGUI:
    PRIZE_TYPES = ('空奖', '礼卡', '实物', '金币')
    PROFILE_DIR = 'lottery/profiles'

    def __init__(self):
        self._dml = None
        self._root = tk.Tk()
        self._row = 0
        self._prize_type_vars = [StringVar(), StringVar(), StringVar(
        ), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        self._prize_quantity_vars = []  # type: list[StringVar]
        for _ in range(8):
            sv = IntVar()
            sv.trace('w', lambda name, index, mode, sv=sv:self._update_quantity())
            self._prize_quantity_vars.append(sv)
        self._gold_quantity_vars = [StringVar(), StringVar(), StringVar(
        ), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        self._total_prize_quantity = StringVar()
        self._gold_qty_combs = []  # type: list[ttk.Entry]
        self._build()
        self._root.mainloop()

    def _build(self):
        self._root.config(bg=BG)
        self._root.title(
            'Dealmoon Lottery Auto Configurator (%s)' % app_version)
        # self._root.grid(padx=PADDING_X, pady=PADDING_Y)
        config_style()
        self._root.config(menu=self._build_menu())
        for i in range(8):
            self._build_row(i)
            self._row += 1
        self._build_button_row()

    def _build_menu(self):
        menubar = tk.Menu(self._root)
        font = Font(family=CN_FONT[0], size=CN_FONT[1], weight=CN_FONT[2])
        self._profile_menu = tk.Menu(
            menubar, tearoff=False, background=BG, foreground=FG, font=font)
        self._profile_menu.add_command(label='加载', command=self.on_load)
        self._profile_menu.add_command(label='保存', command=self.on_save)
        menubar.add_cascade(label='Files', menu=self._profile_menu)
        return menubar

    def _build_row(self, id):
        ttk.Label(self._root, text=str(id+1), style='Heading.TLabel').grid(
            column=0, row=self._row, sticky=tk.E, pady=PADDING_Y, padx=PADDING_X_LABEL)
        ttk.Label(self._root, text='奖励类型', style='CN.TLabel').grid(
            column=1, row=self._row, sticky=tk.E, pady=PADDING_Y, padx=PADDING_X_LABEL)
        comb = ttk.Combobox(self._root, state='readonly', values=DMLotteryGUI.PRIZE_TYPES, style='CN.TCombobox',
                            textvariable=self._prize_type_vars[id], width=10, exportselection=False)
        comb.bind("<<ComboboxSelected>>", lambda obj=None,
                  a=id: self.on_prize_type_selected(obj, a))
        comb.grid(column=2, row=self._row, sticky=tk.W,
                  pady=PADDING_Y, padx=PADDING_X_AFTER_LABEL)
        comb.current(0)

        ttk.Label(self._root, text='奖励数量', style='CN.TLabel').grid(
            column=3, row=self._row, sticky=tk.E, pady=PADDING_Y, padx=PADDING_X_LABEL)
        ttk.Entry(self._root, textvariable=self._prize_quantity_vars[id], width=10).grid(
            column=4, row=self._row, sticky=tk.W, pady=PADDING_Y, padx=PADDING_X_AFTER_LABEL)

        ttk.Label(self._root, text='金币数', style='CN.TLabel').grid(
            column=5, row=self._row, sticky=tk.E, pady=PADDING_Y, padx=PADDING_X_LABEL)
        gold_comb = ttk.Entry(
            self._root, textvariable=self._gold_quantity_vars[id], width=10, state=tk.DISABLED)
        gold_comb.grid(column=6, row=self._row, sticky=tk.W,
                       pady=PADDING_Y, padx=PADDING_X_AFTER_LABEL)
        self._gold_qty_combs.append(gold_comb)

    def _build_button_row(self):
        self._panel = ttk.Frame(self._root)
        ttk.Label(self._panel, textvariable=self._total_prize_quantity).pack(
            side=tk.LEFT, anchor=tk.NW, padx=PADDING_X, pady=PADDING_Y)
        ttk.Button(self._panel, text='Run', command=self.on_run).pack(
            side=tk.RIGHT, anchor=tk.NE, padx=PADDING_X, pady=PADDING_Y)
        self._panel.grid(row=self._row, columnspan=7,
                         sticky=tk.E, padx=PADDING_X, pady=PADDING_Y)

    def _set_gold_entry_box_states(self):
        for i, v in enumerate(self._prize_type_vars):
            if v.get() == '金币':
                self._gold_qty_combs[i].config(state=tk.NORMAL)
            else:
                self._gold_qty_combs[i].config(state=tk.DISABLED)

    def _update_quantity(self):
        self._total_prize_quantity.set(f'总奖励数量：{sum([v.get() for v in self._prize_quantity_vars])}')

    def on_run(self):
        if self._dml is None:
            self._dml = DMLottery()
            self._dml.login()
        self._dml.initiate_lottery()
        for i in range(8):
            row = self._dml.select_row(i)
            prize_type = DMLotteryGUI.PRIZE_TYPES.index(
                self._prize_type_vars[i].get())
            gold_quantity = self._gold_quantity_vars[i].get(
            ) if prize_type == 3 else None
            row.config(PrizeType(prize_type),
                       self._prize_quantity_vars[i].get(),
                       gold_quantity)

    def on_prize_type_selected(self, evtobj: tk.Event, id):
        if evtobj.widget.current() == 3:
            self._gold_qty_combs[id].config(state=tk.NORMAL)
        else:
            self._gold_qty_combs[id].config(state=tk.DISABLED)

    def on_save(self):
        p = Profile()
        p.set_values_from_vars(Profile.KEY_PRIZE_TYPE, self._prize_type_vars)
        p.set_values_from_vars(Profile.KEY_PRIZE_QTY,
                               self._prize_quantity_vars)
        p.set_values_from_vars(Profile.KEY_GOLD_QTY, self._gold_quantity_vars)
        p.save(filedialog.asksaveasfilename(
            filetypes=[('json', '*.json')], initialdir=self.PROFILE_DIR))

    def on_load(self):
        p = Profile()
        p.load(filedialog.askopenfilename(
            filetypes=[('json', '*.json')], initialdir=self.PROFILE_DIR))
        p.set_vars(Profile.KEY_PRIZE_TYPE, self._prize_type_vars)
        p.set_vars(Profile.KEY_PRIZE_QTY, self._prize_quantity_vars)
        p.set_vars(Profile.KEY_GOLD_QTY, self._gold_quantity_vars)
        self._set_gold_entry_box_states()

    def on_config(self):
        pass


class Profile:
    KEY_PRIZE_TYPE = 'prize_type'
    KEY_PRIZE_QTY = 'prize_qty'
    KEY_GOLD_QTY = 'gold_qty'

    def __init__(self):
        self._profile = {}

    def load(self, filename):
        self._profile = json.load(open(filename, 'r', encoding='utf-8'))

    def save(self, filename):
        json.dump(self._profile, open(filename, 'w',
                                      encoding='utf-8'), indent=4, ensure_ascii=False)
        messagebox.showinfo("Save", f'保存完毕')

    def set_values_from_vars(self, key_: str, vars: List[StringVar]):
        t = [v.get() for v in vars]
        self._profile[key_] = t

    def set_vars(self, key_: str, vars: List[StringVar]):
        for i, val in enumerate(self._profile[key_]):
            vars[i].set(val)


if __name__ == "__main__":
    DMLotteryGUI()
