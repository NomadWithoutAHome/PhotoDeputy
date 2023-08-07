import os
import sys
import io
from PyQt5.QtCore import Qt, pyqtSlot, QDir
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QListWidget, QListWidgetItem,
    QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QWidget, QFrame, QDesktopWidget,
)


class PhotoDeputy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path = ''
        self.file_list = []

        QApplication.setStyle('WindowsVista')

        self.setFixedSize(891, 480)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images/Hat.ico')
        self.setWindowIcon(QIcon(icon_path))

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        folder_action = file_menu.addAction('Select Folder')
        folder_action.triggered.connect(self.browse_files)

        convert_action = file_menu.addAction('Convert Folder')
        convert_action.triggered.connect(self.convert_folder)

        self.setMenuBar(menu_bar)

        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        self.file_list_box = QListWidget(self)
        self.file_list_box.currentRowChanged.connect(self.display_image)
        default_item = QListWidgetItem('Files shown here')
        default_item.setFlags(default_item.flags() & ~Qt.ItemIsSelectable)
        self.file_list_box.addItem(default_item)
        main_layout.addWidget(self.file_list_box)

        preview_frame = QFrame(self)
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_frame.setFrameShadow(QFrame.Raised)
        main_layout.addWidget(preview_frame)

        preview_layout = QVBoxLayout(preview_frame)

        self.preview_label = QLabel(preview_frame)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(653, 397)
        placeholder_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'Images/LogoSmoking.png')
        placeholder_image = QPixmap(placeholder_image_path)
        self.preview_label.setPixmap(placeholder_image)
        preview_layout.addWidget(self.preview_label)

        button_layout = QHBoxLayout(preview_frame)

        full_size_button = QPushButton('Full Size', preview_frame)
        full_size_button.clicked.connect(self.open_full_size_window)
        button_layout.addWidget(full_size_button)

        save_button = QPushButton('Save', preview_frame)
        save_button.clicked.connect(self.save_image)
        button_layout.addWidget(save_button)

        preview_layout.addLayout(button_layout)

        help_menu = menu_bar.addMenu('?')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about_dialog)

        self.setCentralWidget(main_widget)
        self.setWindowTitle('Photo Deputy')

        self.show()

    def show_about_dialog(self):
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About")
        about_dialog.setText(
            f"<p>Photo Deputy v1.0.0</p>"
            f"<p>Made by NomadWithoutAHome</p>"
            f"<p><a href='https://bit.ly/PhotoDeputy'>https://bit.ly/PhotoDeputy</a></p>"
        )
        about_dialog.show()

    def browse_files(self):
        self.folder_path = str(QFileDialog.getExistingDirectory(self, 'Select a folder'))
        if not self.folder_path:
            return
        self.file_list_box.clear()
        self.file_list = self.find_files(self.folder_path)
        if not self.file_list:
            QMessageBox.information(self, "No PRDR files found", "No PRDR files found in the selected folder.")
        for file_path in self.file_list:
            filename = os.path.basename(file_path)
            self.file_list_box.addItem(filename)
        self.file_list_box.takeItem(0)
        if self.file_list_box.count() == 0:
            default_item = QListWidgetItem('Files show here')
            default_item.setFlags(default_item.flags() & ~Qt.ItemIsSelectable)
            self.file_list_box.addItem(default_item)
        self.file_list_box.setCurrentRow(0)

    def find_files(self, root_folder):
        file_list = []
        dir = QDir(root_folder)
        for file in dir.entryList(["PRDR*"], QDir.Files):
            file_list.append(os.path.join(root_folder, file))
        return file_list

    def read_image_file(self, filepath):
        with open(filepath, 'rb') as fl:
            buffer = fl.read()

        startBytes = 300
        buffer2 = buffer[startBytes:]

        bytesToFind = bytearray([0xFF, 0xD9])

        lo = 0
        hi = len(buffer2)
        while lo < hi:
            mid = (lo + hi) // 2
            if buffer2[mid:mid + 2] >= bytesToFind:
                hi = mid
            else:
                lo = mid + 1

        endIndex = lo + 2

        img_buffer = io.BytesIO(buffer2[:endIndex])
        img = QImage.fromData(img_buffer.getvalue())

        return img

    @pyqtSlot(int)
    def display_image(self, index):
        if not self.file_list:
            self.preview_label.setPixmap(
                QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images/LogoSmoking.png')))
        elif 0 <= index < len(self.file_list):
            filepath = self.file_list[index]
            img = self.read_image_file(filepath)
            img = img.scaled(653, 397, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(QPixmap.fromImage(img))
        else:
            self.preview_label.setPixmap(
                QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images/LogoSmoking.png')))

    def open_full_size_window(self, _=None):
        index = self.file_list_box.currentRow()
        if not self.file_list or index == -1:
            return
        filepath = self.file_list[index]
        img = self.read_image_file(filepath)
        full_size_dialog = QLabel(self, Qt.Window)
        full_size_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        full_size_dialog.setPixmap(QPixmap.fromImage(img))
        full_size_dialog.setWindowTitle("Photo Deputy - Full Size")
        icon = QIcon(QPixmap.fromImage(img))
        full_size_dialog.setWindowIcon(icon)
        desktop = QDesktopWidget().screenGeometry()
        dialog_rect = full_size_dialog.geometry()
        center_point = desktop.center()
        top_left = center_point - dialog_rect.center()
        full_size_dialog.move(top_left)
        full_size_dialog.show()
        full_size_dialog.raise_()

    def save_image(self):
        index = self.file_list_box.currentRow()
        if not self.file_list or index == -1 or index == self.file_list_box.count() - 1:
            return
        filepath = self.file_list[index]
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "JPEG images (*.jpg);;PNG images (*.png);;All files (*.*)")
        if not save_path:
            return
        file_format = save_path.split(".")[-1].lower()
        if file_format not in ["jpg", "jpeg", "png"]:
            save_path += ".jpg"
        img = self.read_image_file(filepath)
        img.save(save_path)
        QMessageBox.information(self, "Success", "Image saved successfully.")

    def convert_folder(self):
        if not self.file_list:
            QMessageBox.warning(self, 'Error', 'No PRDR files found. Please select a folder first')
            return
        save_format, _ = QFileDialog.getSaveFileName(self, "Select Output Format and Directory", "",
                                                     "JPEG images (*.jpg);;PNG images (*.png);;All files (*.*)")
        if not save_format:
            return
        save_dir = os.path.join(os.path.dirname(sys.executable), "Output")
        os.makedirs(save_dir, exist_ok=True)
        for file_path in self.file_list:
            img = self.read_image_file(file_path)
            filename, _ = os.path.splitext(os.path.basename(file_path))
            filename = f"{filename}.{save_format.split('.')[-1]}"
            save_path = os.path.join(save_dir, filename)
            img.save(save_path)
        QMessageBox.information(self, "Success", f"All images converted and saved in {save_dir}")


if __name__ == '__main__':
    app = QApplication([])
    photo_deputy = PhotoDeputy()
    app.exec_()
