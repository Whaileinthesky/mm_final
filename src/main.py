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
from pathlib import Path

try:
    from picamera2 import Picamera2
    PICAM_AVAILABLE = True
except Exception:
    PICAM_AVAILABLE = False


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The main window of the application.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        #debug
        print("Medicine Manager")

        self.my_medicine_list_model = QStandardItemModel(self)
        self.my_medicines_list_view.setModel(self.my_medicine_list_model)
        self.my_medicine_list_model.appendRow(QStandardItem("오피큐탄연질캡슐")) #내가 복용중인 약

        self.dur_table_model = QStandardItemModel(0, 3, self)
        self.dur_table_model.setHorizontalHeaderLabels(
            ["Ingredient", "Product Name", "Reason for Contraindication"]
        )
        self.dur_table_view.setModel(self.dur_table_model)
        self._configure_dur_table()

        self._last_frame_rgb = None
        self.picam2 = None

        if not PICAM_AVAILABLE:
            self.statusbar.showMessage("Picamera2 미설치: sudo apt install python3-picamera2", 8000)
        else:
            try:
                self.picam2 = Picamera2()
                cfg = self.picam2.create_preview_configuration(
                    main={"size": (640, 480), "format": "RGB888"}  # 호환성/속도 좋은 기본값
                )
                self.picam2.configure(cfg)
                self.picam2.start()
            except Exception as e:
                self.statusbar.showMessage(f"카메라 초기화 실패: {e}", 8000)
                self.picam2 = None

        # 미리보기 타이머(워밍업 0.5s 후 시작)
        self.cam_timer = QTimer(self)
        self.cam_timer.timeout.connect(self._update_camera_preview)
        QTimer.singleShot(500, lambda: self.cam_timer.start(33)) 
        print("Timer Started")

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
    
    def _update_camera_preview(self):
        """Picamera2에서 프레임을 받아 QLabel(camera_view)에 표시하고
        최신 프레임을 self._last_frame_rgb 로 보관한다."""
        if self.picam2 is None:
            return
        try:
            frame_rgb = self.picam2.capture_array("main")  # RGB888 numpy(H,W,3)
        except Exception as e:
            print("[CAPTURE ERR]", repr(e))
            self.statusbar.showMessage(f"CAPTURE ERR: {e}", 2000)
            return
        if frame_rgb is None:
            return

        self._last_frame_rgb = frame_rgb  # 저장/예측에 동일 프레임 사용

        h, w, ch = frame_rgb.shape  # ch=3
        qimg = QImage(frame_rgb.data, w, h, 3*w, QImage.Format.Format_RGB888).copy()
        self.camera_view.setPixmap(QPixmap.fromImage(qimg))
        self.camera_view.setScaledContents(True)
        
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

    def on_add_medicine_clicked(self):
        if self._last_frame_rgb is None:
            self.statusbar.showMessage("아직 카메라 프레임이 없습니다.", 2000)
            return

        # 저장 위치 
        
        base_dir = Path(__file__).resolve().parent
        image_dir = (base_dir.parent / "image")
        image_dir.mkdir(parents=True, exist_ok=True)
        save_path = image_dir / "medicine.jpg"

        # 저장(RGB -> BGR 변환 후 imwrite)
        import cv2 as cv
        #bgr = cv.cvtColor(self._last_frame_rgb, cv.COLOR_RGB2BGR)
        if not cv.imwrite(str(save_path), self._last_frame_rgb):
            self.statusbar.showMessage("사진 저장 실패", 2000)
            return

        self.captured_image_path = str(save_path)
        self.statusbar.showMessage(f"사진 저장: {self.captured_image_path}", 3000)

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
