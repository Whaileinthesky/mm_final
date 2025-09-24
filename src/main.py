import sys
from typing import List
import cv2 as cv
import numpy as np
#import yaml
from pathlib import Path
from PySide6.QtCore import QThread, Signal, Slot, QObject, QTimer
from PySide6.QtGui import QImage, QPixmap, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableView, QMessageBox
from ui_final import Ui_MainWindow
from api_client import DURClient
from predict_class import predict_func


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The main window of the application.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.my_medicine_list_model = QStandardItemModel(self)
        self.my_medicines_list_view.setModel(self.my_medicine_list_model)
        self.my_medicine_list_model.appendRow(QStandardItem("오피큐탄연질캡슐")) #내가 복용중인 약

        self.dur_table_model = QStandardItemModel(0, 3, self)
        self.dur_table_model.setHorizontalHeaderLabels(
            ["Ingredient", "Product Name", "Reason for Contraindication"]
        )
        self.dur_table_view.setModel(self.dur_table_model)
        self._configure_dur_table()

        #camera setting
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            self.statusbar.showMessage("카메라를 열 수 없습니다.", 3000)
        self._last_frame = None  # 최근 프레임 보관

        self.cam_timer = QTimer(self)
        self.cam_timer.timeout.connect(self._update_camera_preview)
        self.cam_timer.start(33)  # 약 30fps (33ms)

        #image 저장 위치
        base_dir = Path(__file__).resolve().parent          # projects/src
        self.image_dir = (base_dir.parent / "image")        # projects/image
        self.image_dir.mkdir(parents=True, exist_ok=True)

        #저장된 경로, 인식한 약 이름    c
        self.captured_image_path = None
        self.current_medicine_name = None

        #식약처 api키 불러오기
        self.api_key = "I4dBVv+Mef8KeUzJpsbXVyI2FzJRDvaaTrqjwDp3NSU1lZoosPsZFaxekYcWHETBTVLXBnjKr8gE5kiPoAS/XA=="
        if self.api_key:
            self.dur_client = DURClient(api_key=self.api_key)
        else:
            self.dur_client = None
            self.statusbar.showMessage("DUR Client could not be initialized.", 5000)

        #ui 버튼 연결
        self.add_medicine_button.clicked.connect(self.on_add_medicine_clicked)
        self.quit_button.clicked.connect(self.close)
        
    def _configure_dur_table(self):
        """
        Configures the appearance and behavior of the DUR table.
        """
        self.dur_table_view.setAlternatingRowColors(True)
        self.dur_table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.dur_table_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.dur_table_view.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.dur_table_view.horizontalHeader().setStretchLastSection(True)
        self.dur_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.dur_table_view.setSortingEnabled(False)

    """def _load_api_key(self) -> str:
    
        try:
            with open("config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            api_key = config.get("DECODING_KEY", "")
            if not api_key:
                self.statusbar.showMessage("API key is missing from config.yaml.", 5000)
            return api_key
        except FileNotFoundError:
            self.statusbar.showMessage("config.yaml not found.", 5000)
            return """

    #카메라 화면
    def _update_camera_preview(self):
        if not hasattr(self, "cap") or not self.cap.isOpened():
            return
        ok, frame = self.cap.read()
        if not ok:
            return

        self._last_frame = frame  # 최신 프레임 저장 (캡처 시 사용)

        # BGR -> RGB 변환 후 QLabel 표시
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        self.camera_view.setPixmap(QPixmap.fromImage(qimg))
        self.camera_view.setScaledContents(True)  # 라벨 크기에 맞춰 표시

    def on_add_medicine_clicked(self):
        if self._last_frame is None:
            self.statusbar.showMessage("아직 카메라 프레임이 없습니다.", 2000)
            return

        save_path = self.image_dir / f"medicine.jpg"
        #model 위치
        model_path = r"C:/Users/sd674/Documents/medicine_manager/mm_model/mm_model.h5"
        class_indices_path = r"C:/Users/sd674/Documents/medicine_manager/mm_model/mm_model_class_indices.json"

        ok = cv.imwrite(str(save_path), self._last_frame)
        if not ok:
            self.statusbar.showMessage("사진 저장 실패", 2000)
            return

        # 경로 보관
        self.captured_image_path = str(save_path)
        
        self.statusbar.showMessage(f"사진 저장: {self.captured_image_path}", 3000)

        pred = predict_func(model_path, class_indices_path)
        value = str(pred.predict(self.captured_image_path)).strip()
        
        self.current_medicine_name = value
        print(f"[DEBUG] 인식 결과 저장: {self.current_medicine_name}")

        self._append_to_my_medicine_list() 
        self._dur_check(self.current_medicine_name)
        #self._check_for_drug_interactions(self.current_medicine_name) dur 확인

    def _append_to_my_medicine_list(self):
        """self.current_medicine_name를 복용 목록에 중복 없이 추가"""
        name = (self.current_medicine_name or "").strip()
        if not name:
            self.statusbar.showMessage("인식된 약 이름이 없습니다.", 2000)
            return
        # 이미 있는지 확인
        for r in range(self.my_medicine_list_model.rowCount()):
            if self.my_medicine_list_model.item(r).text() == name:
                return
        self.my_medicine_list_model.appendRow(QStandardItem(name))

    def _append_dur_rows(self, items) -> int:
        print("append row ")
        def _get(d: dict, key: str, default=""):
            v = d.get(key)
            return (str(v).strip() if v is not None else default)

        # 현재 테이블 중복 키 수집 (ingredient, product, reason)
        existing = set()
        for r in range(self.dur_table_model.rowCount()):
            ing = self.dur_table_model.item(r, 0).text()
            prod = self.dur_table_model.item(r, 1).text()
            rsn = self.dur_table_model.item(r, 2).text()
            existing.add((ing, prod, rsn))

        # items 정규화
        if isinstance(items, dict):
            items = (items.get("items")
                    or items.get("body", {}).get("items")
                    or items.get("results")
                    or [])

        added = 0
        for it in (items or []):
            ingredient = _get(it, "MIXTURE_INGR_KOR_NAME")
            product    = _get(it, "MIXTURE_ITEM_NAME")
            reason     = _get(it, "PROHBT_CONTENT")

            # 셋 다 비면 스킵
            if not (ingredient or product or reason):
                continue

            key = (ingredient, product, reason)
            if key in existing:
                continue

            self.dur_table_model.appendRow([
                QStandardItem(ingredient),
                QStandardItem(product),
                QStandardItem(reason),
            ])
            existing.add(key)
            added += 1

        return added

    def _dur_check(self, new_medicine):
        """
        새로 추가된 약(new_medicine)과 내가 복용 중인 약들의 병용금기를 확인하고,
        테이블에 반영 + 경고창을 띄운다.

        DUR 응답의 '상대 약'은 MIXTURE_ITEM_NAME 로 간주한다.
        사유는 PROHBT_CONTENT 를 사용한다.
        """
        print("DUR check")
        name = (new_medicine or "").strip()
        if not name:
            self.statusbar.showMessage("DUR: 약 이름이 비어 있습니다.", 3000)
            return
        if not self.dur_client:
            self.statusbar.showMessage("DUR Client가 초기화되지 않았습니다.", 3000)
            return

        try:
            res = self.dur_client.query_drug_interaction(item_name=name, rows=50) or {}
        except Exception as e:
            self.statusbar.showMessage(f"DUR 조회 실패: {e}", 5000)
            return

        # 테이블 갱신
        added = self._append_dur_rows(res)
        print("table update")
        if added:
            self.statusbar.showMessage(f"DUR 결과 {added}건 추가", 3000)
        else:
            self.statusbar.showMessage("DUR: 추가할 신규 결과가 없습니다.", 3000)

        # 내 복용약 집합
        my_meds = { self.my_medicine_list_model.item(r).text().strip()
                    for r in range(self.my_medicine_list_model.rowCount()) }

        # 응답에서 병용 '상대 약'과 사유 추출
        def _items_from_res(res):
            if isinstance(res, list):
                return res
            if isinstance(res, dict):
                return (res.get("items")
                        or res.get("body", {}).get("items")
                        or res.get("results")
                        or [])
            return []

        items = _items_from_res(res)
        hits = []
        for it in items:
            other_prod = (it.get("MIXTURE_ITEM_NAME") or "").strip()
            reason     = (it.get("PROHBT_CONTENT") or "").strip()
            # 상대 제품명이 내 복용 목록에 있으면 히트
            if other_prod and other_prod in my_meds:
                hits.append((other_prod, reason))

        if hits:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("병용금기 주의")
            msg.setText(f"'{name}'과(와) 병용금기 가능성이 있습니다.")
            msg.setInformativeText("복용을 중단하고, 의사·약사와 상담하세요.")
            details = "\n".join([f"· {prod} — {rsn or '사유 정보 없음'}" for prod, rsn in hits])
            msg.setDetailedText(details)
            msg.exec()

        

    def closeEvent(self, event):
        try:
            if hasattr(self, "cam_timer"):
                self.cam_timer.stop()
            if getattr(self, "cap", None) is not None and self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Medicine Manager")
    window.show()
    sys.exit(app.exec())
