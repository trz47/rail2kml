import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from shapefile import ShapefileException

import make_dict
import rail2kml

SECTION_NUM = 20  # 区間の入力欄数


class Application(ttk.Frame):
    """
    アプリケーション本体
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(column=0, row=0)
        self.create_widgets()
        self.add_to_cmmbx_is_act = False
        self.recent_shp_dir = os.path.abspath(os.path.expanduser("~"))
        self.recent_kml_dir = os.path.abspath(os.path.expanduser("~"))

    def create_widgets(self):
        """
        ウィジット作成
        """
        # 路線shapefileパス
        rail_spf_path_lbl = ttk.Label(self, text="路線shapefile")
        self.disp_rail_spf_path = tk.StringVar()
        rail_spf_path_etr = ttk.Entry(
            self, textvariable=self.disp_rail_spf_path
        )
        self.rail_spf_path_ref = ttk.Button(self, text="参照")
        self.rail_spf_path_ref.bind("<Button-1>", self.ref_shp_path)

        # 駅shapefileパス
        station_spf_path_lbl = ttk.Label(self, text="駅shapefile")
        self.disp_station_spf_path = tk.StringVar()
        station_spf_path_etr = ttk.Entry(
            self, textvariable=self.disp_station_spf_path
        )
        self.station_spf_path_ref = ttk.Button(self, text="参照")
        self.station_spf_path_ref.bind("<Button-1>", self.ref_shp_path)

        # shapefile読み込み
        read_spf_btn = ttk.Button(self, text="shapefile読込")
        read_spf_btn.bind("<Button-1>", self.read_spf)

        # 区間の選択
        section_cmbbx_lbls = list()
        for typ in ["会社", "路線", "始点駅", "終点駅"]:
            section_cmbbx_lbls.append(ttk.Label(self, text=typ))
        self.section_cmbbxs_lst = list()
        self.section_cmbbxs_typs = list(["company", "line", "start", "goal"])
        for i in range(SECTION_NUM):
            section_cmbbxs = dict()
            for cmbbx_typ in self.section_cmbbxs_typs:
                val = tk.StringVar()
                cmbbx = ttk.Combobox(self, textvariable=val, state=tk.DISABLED)
                section_cmbbx = dict({"widget": cmbbx, "value": val})
                section_cmbbxs.update({cmbbx_typ: section_cmbbx})
            self.section_cmbbxs_lst.append(section_cmbbxs)

        # 中間駅を含めるか設定
        self.is_inc_mdls = tk.BooleanVar()
        is_inc_mdls_chk = ttk.Checkbutton(
            self, variable=self.is_inc_mdls, text="中間駅を含める"
        )

        # kml保存先
        kml_path_lbl = ttk.Label(self, text="kml保存先")
        self.disp_kml_path = tk.StringVar()
        kml_path_etr = ttk.Entry(self, textvariable=self.disp_kml_path)
        self.kml_path_ref = ttk.Button(self, text="参照")
        self.kml_path_ref.bind("<Button-1>", self.ref_kml_path)

        # kml 作成ボタン
        self.mk_kml_btn = ttk.Button(self, text="kml作成", state=tk.DISABLED)

        # 終了ボタン
        quit_btn = ttk.Button(self, text="終了", command=self.master.destroy)

        # 状態表示
        self.status = tk.StringVar()
        status_disp = ttk.Label(self, textvariable=self.status)

        # 配置設定
        clm = 0
        row = 0
        rail_spf_path_lbl.grid(column=clm, row=row)
        clm += 1
        rail_spf_path_etr.grid(column=clm, row=row)
        clm += 1
        self.rail_spf_path_ref.grid(column=clm, row=row)

        clm = 0
        row += 1
        station_spf_path_lbl.grid(column=clm, row=row)
        clm += 1
        station_spf_path_etr.grid(column=clm, row=row)
        clm += 1
        self.station_spf_path_ref.grid(column=clm, row=row)

        clm = 3
        row += 1
        read_spf_btn.grid(column=clm, row=row)

        clm = -1
        row += 1
        for lbl in section_cmbbx_lbls:
            clm += 1
            lbl.grid(column=clm, row=row)

        for i in range(SECTION_NUM):
            clm = -1
            row += 1
            for j, cmbbx_typ in enumerate(self.section_cmbbxs_typs):
                clm += 1
                self.section_cmbbxs_lst[i][cmbbx_typ]["widget"].grid(
                    column=clm, row=row
                )

        clm = 3
        row += 1
        is_inc_mdls_chk.grid(column=clm, row=row)

        clm = 0
        row += 1
        kml_path_lbl.grid(column=clm, row=row)
        clm += 1
        kml_path_etr.grid(column=clm, row=row)
        clm += 1
        self.kml_path_ref.grid(column=clm, row=row)

        clm = 3
        row += 1
        self.mk_kml_btn.grid(column=clm, row=row)

        clm = 3
        row += 1
        quit_btn.grid(column=clm, row=row)

        clm = 0
        row += 1
        status_disp.grid(column=clm, row=row)

    def ref_shp_path(self, event):
        """
        shapefile 参照
        """
        filepath = filedialog.askopenfilename(
            filetypes=[("Shapefile", ".shp")], initialdir=self.recent_shp_dir
        )
        self.recent_shp_dir = os.path.dirname(filepath)

        # 呼び出しもとで条件分岐
        if event.widget is self.rail_spf_path_ref:
            self.disp_rail_spf_path.set(filepath)
        elif event.widget is self.station_spf_path_ref:
            self.disp_station_spf_path.set(filepath)
        else:
            pass

        return "break"

    def ref_kml_path(self, event):
        """
        kml 保存先参照
        """
        filepath = filedialog.asksaveasfilename(
            initialfile="rail.kml",
            filetypes=[("KMLファイル", ".kml")],
            initialdir=self.recent_kml_dir,
        )
        self.recent_kml_dir = os.path.dirname(filepath)
        self.disp_kml_path.set(filepath)
        return "break"

    def read_spf(self, event):
        """
        shapefile 読込
        """
        self.status.set("shapefile読込中")

        shapefile_path = dict(
            {
                "rail": self.disp_rail_spf_path.get(),
                "station": self.disp_station_spf_path.get(),
            }
        )

        try:
            self.shape_recs = rail2kml.read_shapefile(shapefile_path, True)
            shape_recs_station = self.shape_recs["station"]
            self.stations_dict = make_dict.make_stations_dict(
                shape_recs_station
            )
            for i in range(SECTION_NUM):
                for cmbbx_typ in self.section_cmbbxs_typs:
                    cmmbbx = self.section_cmbbxs_lst[i][cmbbx_typ]
                    if cmbbx_typ == "company":
                        cmmbbx["widget"]["values"] = list(
                            sorted(self.stations_dict.keys())
                        )
                        self.act_cmbbx(cmmbbx)
                    else:
                        self.diact_cmbbx(cmmbbx)
            self.mk_kml_btn.bind("<Button-1>", self.mk_kml)
            self.mk_kml_btn["state"] = tk.NORMAL
            self.status.set("shapefile読込完了")
        except (ShapefileException, IndexError):
            for i in range(SECTION_NUM):
                for cmbbx_typ in self.section_cmbbxs_typs:
                    cmmbbx = self.section_cmbbxs_lst[i][cmbbx_typ]
                    self.diact_cmbbx(cmmbbx)
            self.mk_kml_btn.unbind("<Button-1>")
            self.mk_kml_btn["state"] = tk.DISABLED
            self.status.set("")
            messagebox.showwarning("shapefile読込エラー", "shapefileのパスを確認してください。")

        return "break"

    def add_to_cmmbx(self, event):
        """
        combobox に選択項目追加
        """
        if self.add_to_cmmbx_is_act is False:
            self.add_to_cmmbx_is_act = True
            for i in range(SECTION_NUM):
                for cmbbx_typ in self.section_cmbbxs_typs:
                    if (
                        event.widget
                        is self.section_cmbbxs_lst[i][cmbbx_typ]["widget"]
                    ):
                        company = self.section_cmbbxs_lst[i]["company"][
                            "value"
                        ].get()
                        line = self.section_cmbbxs_lst[i]["line"][
                            "value"
                        ].get()
                        start = self.section_cmbbxs_lst[i]["start"][
                            "value"
                        ].get()
                        goal = self.section_cmbbxs_lst[i]["goal"][
                            "value"
                        ].get()
                        line_cmbbx = self.section_cmbbxs_lst[i]["line"]
                        start_cmbbx = self.section_cmbbxs_lst[i]["start"]
                        goal_cmbbx = self.section_cmbbxs_lst[i]["goal"]
                        if cmbbx_typ == "company":
                            if company in self.stations_dict.keys():
                                line_cmbbx["widget"]["values"] = list(
                                    sorted(self.stations_dict[company].keys())
                                )
                                self.act_cmbbx(line_cmbbx)
                                self.diact_cmbbx(start_cmbbx)
                                self.diact_cmbbx(goal_cmbbx)
                            elif company != "":
                                messagebox.showwarning(
                                    "会社入力エラー", "入力された会社は登録されていません。"
                                )
                                self.section_cmbbxs_lst[i]["company"][
                                    "value"
                                ].set("")
                                self.diact_cmbbx(line_cmbbx)
                                self.diact_cmbbx(start_cmbbx)
                                self.diact_cmbbx(goal_cmbbx)
                            else:
                                pass
                        elif cmbbx_typ == "line":
                            if line in self.stations_dict[company].keys():
                                start_cmbbx["widget"]["values"] = list(
                                    sorted(self.stations_dict[company][line])
                                )
                                goal_cmbbx["widget"]["values"] = list(
                                    sorted(self.stations_dict[company][line])
                                )
                                self.act_cmbbx(start_cmbbx)
                                self.act_cmbbx(goal_cmbbx)
                            elif line != "":
                                messagebox.showwarning(
                                    "路線入力エラー", "入力された路線は登録されていません。"
                                )
                                self.section_cmbbxs_lst[i]["line"][
                                    "value"
                                ].set("")
                                self.diact_cmbbx(start_cmbbx)
                                self.diact_cmbbx(goal_cmbbx)
                            else:
                                pass
                        elif cmbbx_typ == "start":
                            if (
                                start != ""
                                and start
                                not in self.stations_dict[company][line]
                            ):
                                messagebox.showwarning(
                                    "始点駅入力エラー", "入力された駅は登録されていません。"
                                )
                                self.section_cmbbxs_lst[i]["start"][
                                    "value"
                                ].set("")
                            elif start != "" and goal != "" and start == goal:
                                messagebox.showwarning(
                                    "始点駅入力エラー", "始点駅と終点駅は同じにできません。"
                                )
                                self.section_cmbbxs_lst[i]["start"][
                                    "value"
                                ].set("")
                            else:
                                pass
                        elif cmbbx_typ == "goal":
                            if (
                                goal != ""
                                and goal
                                not in self.stations_dict[company][line]
                            ):
                                messagebox.showwarning(
                                    "終点駅入力エラー", "入力された駅は登録されていません。"
                                )
                                self.section_cmbbxs_lst[i]["goal"][
                                    "value"
                                ].set("")
                            elif start != "" and goal != "" and start == goal:
                                messagebox.showwarning(
                                    "終点駅入力エラー", "始点駅と終点駅は同じにできません。"
                                )
                                self.section_cmbbxs_lst[i]["goal"][
                                    "value"
                                ].set("")
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
            self.add_to_cmmbx_is_act = False
        else:
            pass

    def mk_kml(self, event):
        """
        kmlファイル作成
        """
        PATCH_PATH = "patch/patch.json"
        patch = rail2kml.read_patch(PATCH_PATH)
        self.status.set("経路探索中")
        self.get_section_list()
        try:
            (
                section_edges_list,
                stations_edges_list,
            ) = rail2kml.get_section_edges_list(
                self.section_list, self.shape_recs, patch
            )
        except rail2kml.PathSearchError as pse:
            self.status.set("")
            messagebox.showwarning("経路探索エラー", "経路探索に失敗しました。" + "\n" + str(pse))
            return "break"

        self.status.set("kml保存中")
        try:
            rail2kml.output_kml(
                section_edges_list,
                stations_edges_list,
                self.section_list,
                self.is_inc_mdls.get(),
                self.disp_kml_path.get(),
                True,
            )
            self.status.set("")
            messagebox.showinfo("kml保存完了", "kmlファイルを保存しました。")
        except FileNotFoundError:
            self.status.set("")
            messagebox.showwarning("kml保存エラー", "kmlの保存先を確認してください。")
            return "break"

        return "break"

    def get_section_list(self):
        """
        section list 読込
        """
        self.section_list = list()
        for i in range(SECTION_NUM):
            section = dict()
            for cmbbx_typ in self.section_cmbbxs_typs:
                is_adding = True
                value = self.section_cmbbxs_lst[i][cmbbx_typ]["value"].get()
                if value != "":
                    section.update({cmbbx_typ: value})
                else:
                    is_adding = False
                    break
            if is_adding is True:
                self.section_list.append(section)
            else:
                pass

    def act_cmbbx(self, cmbbx):
        """
        comboboxの有効化
        """
        cmbbx["value"].set("")
        cmbbx["widget"].bind("<<ComboboxSelected>>", self.add_to_cmmbx)
        cmbbx["widget"].bind("<Return>", self.add_to_cmmbx)
        cmbbx["widget"].bind("<FocusOut>", self.add_to_cmmbx)
        cmbbx["widget"]["state"] = tk.NORMAL

    def diact_cmbbx(self, cmbbx):
        """
        comboboxの無効化
        """
        cmbbx["value"].set("")
        cmbbx["widget"].unbind("<<ComboboxSelected>>")
        cmbbx["widget"].unbind("<Return>")
        cmbbx["widget"].unbind("<FocusOut>")
        cmbbx["widget"]["value"] = list()
        cmbbx["widget"]["state"] = tk.DISABLED


def main():
    """
    メイン関数
    """
    root = tk.Tk()
    root.title("rail2kml")
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
