import os
import io
import json
import datetime
from PyQt5.QtCore import Qt, pyqtSlot, QDir, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidget, QListWidgetItem, QLabel, QPushButton, \
    QVBoxLayout, QHBoxLayout, QMessageBox, QWidget, QFrame, QDesktopWidget, QProgressDialog, QMenu, QAction, QDialog


class PhotoDeputy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path = ''
        self.file_list = []

        # Apply WindowsVista style
        QApplication.setStyle('WindowsVista')

        # Set fixed size of the main window
        self.setFixedSize(891, 480)

        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images/Hat.ico')
        self.setWindowIcon(QIcon(icon_path))

        # Create and set menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        folder_action = file_menu.addAction('Select Folder')
        folder_action.triggered.connect(self.browse_files)
        convert_action = file_menu.addAction('Convert Folder')
        convert_action.triggered.connect(self.convert_folder)
        self.setMenuBar(menu_bar)

        # Create main widget and layout
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        # Create list widget for files
        self.file_list_box = QListWidget(self)
        self.file_list_box.currentRowChanged.connect(self.display_image)

        # Create default list box item
        default_item = QListWidgetItem('Files shown here')
        default_item.setFlags(default_item.flags() & ~Qt.ItemIsSelectable)
        self.file_list_box.addItem(default_item)

        main_layout.addWidget(self.file_list_box)

        # Create frame for image preview
        preview_frame = QFrame(self)
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_frame.setFrameShadow(QFrame.Raised)
        main_layout.addWidget(preview_frame)

        # Create layout for preview frame
        preview_layout = QVBoxLayout(preview_frame)

        # Create label image preview
        self.preview_label = QLabel(preview_frame)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(653, 397)
        placeholder_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              'Images/LogoSmoking.png')  # path to placeholder image
        placeholder_image = QPixmap(placeholder_image_path)
        self.preview_label.setPixmap(placeholder_image)
        preview_layout.addWidget(self.preview_label)

        # Create layout for buttons
        button_layout = QHBoxLayout(preview_frame)

        # Create "Full Size" button
        full_size_button = QPushButton('Full Size', preview_frame)
        full_size_button.clicked.connect(self.open_full_size_window)
        button_layout.addWidget(full_size_button)

        # Create "Save" button
        save_button = QPushButton('Save', preview_frame)
        save_button.clicked.connect(self.save_single_image)
        button_layout.addWidget(save_button)

        preview_layout.addLayout(button_layout)

        # Create and set Help menu
        help_menu = menu_bar.addMenu('?')
        help_menu.addAction('About')
        help_menu.triggered.connect(self.show_about_dialog)

        # Create right-click context menu
        self.context_menu = QMenu(self)
        self.show_meta_action = QAction("Show Metadata", self)
        self.show_meta_action.triggered.connect(self.show_metadata)
        self.context_menu.addAction(self.show_meta_action)

        # Connect the right-click context menu to the list widget
        self.file_list_box.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list_box.customContextMenuRequested.connect(self.show_context_menu)

        self.setCentralWidget(main_widget)
        self.setWindowTitle('Photo Deputy')



        self.show()

    def show_context_menu(self, pos):
        selected_item = self.file_list_box.itemAt(pos)
        if selected_item:
            self.context_menu.exec_(self.file_list_box.mapToGlobal(pos))

    def show_metadata(self):
        index = self.file_list_box.currentRow()
        if not self.file_list or index < 0 or index >= len(self.file_list):
            return

        filepath = self.file_list[index]
        suggested_title = self.extract_title(filepath)
        meta_info = self.extract_meta(filepath)

        if suggested_title is None or meta_info is None:
            QMessageBox.warning(self, "Metadata Error", "Metadata information is not available for this image.")
            return

        metadata_dialog = QDialog(self)
        metadata_dialog.setWindowTitle("Metadata Information")

        metadata_layout = QVBoxLayout(metadata_dialog)

        title_label = QLabel(f"Title: {suggested_title}")
        metadata_layout.addWidget(title_label)

        for key, value in meta_info.items():
            meta_label = QLabel(f"{key.capitalize()}: {value}")
            metadata_layout.addWidget(meta_label)

        metadata_dialog.setLayout(metadata_layout)
        metadata_dialog.exec_()

    def show_about_dialog(self):
        """function to show the about dialog"""
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About")
        about_dialog.setText(f"<p>Photo Deputy v1.0.0</p>"
                             f"<p>Made by NomadWithoutAHome</p>"
                             f"<p><a href='https://bit.ly/PhotoDeputy'>https://bit.ly/PhotoDeputy</a></p>")
        about_dialog.show()

    def select_format(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Select Output Format")
        dialog.setText("Select the output format for converted files:")
        dialog.setIcon(QMessageBox.Question)

        jpeg_button = dialog.addButton("JPEG", QMessageBox.YesRole)
        png_button = dialog.addButton("PNG", QMessageBox.YesRole)

        dialog.exec_()

        if dialog.clickedButton() == jpeg_button:
            return "jpg"
        elif dialog.clickedButton() == png_button:
            return "png"
        else:
            return None

    # def browse_files(self):
    #     """function to browse for folder and find images"""
    #     self.folder_path = str(QFileDialog.getExistingDirectory(self, 'Select a folder'))
    #     if not self.folder_path:
    #         return
    #     self.file_list_box.clear()
    #     self.file_list = self.find_files(self.folder_path)
    #     if not self.file_list:
    #         QMessageBox.information(self, "No PRDR files found", "No PRDR files found in the selected folder.")
    #
    #     # Print the entire self.file_list
    #     print("Populated File List:")
    #     for file_path in self.file_list:
    #         print(file_path)
    #
    #     for file_path in self.file_list:
    #         suggested_title = self.extract_title(file_path)
    #         suggested_timestamp = self.extract_meta(file_path).get("creat", None)
    #
    #         if suggested_title is not None and suggested_timestamp is not None:
    #             formatted_title = suggested_title.replace(" ", "_")
    #             formatted_timestamp = self.dolerean(suggested_timestamp)
    #             suggested_filename = f"{formatted_title}"
    #         else:
    #             suggested_filename = os.path.basename(file_path)  # If metadata is not available
    #
    #         # Create a list widget item and set the text
    #         list_item = QListWidgetItem(suggested_filename)
    #         self.file_list_box.addItem(list_item)
    #
    #         # Set the size hint for the item to fit the longer text
    #         list_item.setSizeHint(QSize(list_item.sizeHint().width(), 50))  # Adjust the height as needed
    #
    #     self.file_list_box.takeItem(0)  # remove default item
    #     if self.file_list_box.count() == 0:
    #         # add default item if no files are found
    #         default_item = QListWidgetItem('Files show here')
    #         default_item.setFlags(default_item.flags() & ~Qt.ItemIsSelectable)
    #         self.file_list_box.addItem(default_item)
    #     self.file_list_box.setCurrentRow(0)  # set current row to first item

    def browse_files(self):
        """function to browse for folder and find images"""
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
        self.file_list_box.takeItem(0)  # remove default item
        if self.file_list_box.count() == 0:
            # add default item if no files are found
            default_item = QListWidgetItem('Files show here')
            default_item.setFlags(default_item.flags() & ~Qt.ItemIsSelectable)
            self.file_list_box.addItem(default_item)
        self.file_list_box.setCurrentRow(0)  # set current row to first item

    def find_files(self, root_folder):
        """function to search for files starting with 'PRDR'"""
        file_list = []
        dir = QDir(root_folder)
        for file in dir.entryList(["PRDR*"], QDir.Files | QDir.NoDotAndDotDot):
            file_path = os.path.join(root_folder, file)
            if not os.path.splitext(file_path)[1]:
                file_list.append(file_path)
        return file_list

    def find_files(self, root_folder):
        """function to search for files starting with 'PRDR'"""
        file_list = []
        dir = QDir(root_folder)
        for file in dir.entryList(["PRDR*"], QDir.Files | QDir.NoDotAndDotDot):
            file_path = os.path.join(root_folder, file)
            if not os.path.splitext(file_path)[1]:
                file_list.append(file_path)
        return file_list

    def read_image_file(self, filepath):
        """function to read image file and extract image buffer"""
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

    def extract_title(self, file_path):
        search_sequence = bytes.fromhex('54 49 54 4C 00 01 00 00')  # Hexadecimal bytes for search

        # Open the binary file for reading in binary mode
        with open(file_path, 'rb') as file:
            byte_data = file.read()  # Read the binary data from the file

        start_index = 0  # Initialize the starting index for searching

        # Iterate through the binary data to find the title
        while start_index < len(byte_data):
            title_pos = byte_data.find(search_sequence, start_index)  # Find position of search sequence

            if title_pos == -1:
                return None  # Return None if search sequence is not found

            title_string_start = title_pos + len(search_sequence)  # Start of title string
            title_string_end = byte_data.find(b'\0', title_string_start)  # End of title string

            if title_string_end == -1:
                return None  # Return None if end of string is not found

            title_bytes = byte_data[title_string_start:title_string_end]  # Extract title bytes
            title = title_bytes.decode('utf-8', errors='ignore')  # Decode title bytes to UTF-8 string

            return title  # Return the extracted title

        return None  # Return None if no title is found

    def extract_meta(self, file_path):
        # Open the binary file for reading in binary mode
        with open(file_path, 'rb') as file:
            byte_data = file.read()  # Read the binary data from the file

        start_sequence = b'{"loc":{"x":'
        end_sequence = b'}}'

        start_index = 0
        found_sequence = False  # Flag to track whether a sequence was found

        # Iterate through the binary data to find and extract JSON sequences
        while start_index < len(byte_data):
            start_pos = byte_data.find(start_sequence, start_index)

            # If start sequence not found, move to the next iteration
            if start_pos == -1:
                start_index = len(byte_data)
                continue

            end_pos = byte_data.find(end_sequence, start_pos + len(start_sequence))

            # If end sequence not found, move to the next iteration
            if end_pos == -1:
                start_index = len(byte_data)
                continue

            found_sequence = True  # A sequence was found

            # Extract the JSON bytes and attempt to parse
            json_bytes = byte_data[start_pos:end_pos + len(end_sequence)]
            try:
                json_data = json.loads(json_bytes)
                return json_data  # Return the extracted JSON data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)

            # Move the index to continue searching
            start_index = end_pos + len(end_sequence)

        if not found_sequence:
            print("No sequence found in the binary data")
            return None  # Return None if no sequence is found

    def dolerean(self, timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        formatted_datetime = dt_object.strftime("%Y-%m-%d-%I-%M-%S")
        return formatted_datetime

    @pyqtSlot(int)
    def display_image(self, index):
        """function to display selected image"""
        if not self.file_list or index < 0 or index >= len(self.file_list):
            self.preview_label.setPixmap(
                QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images/LogoSmoking.png')))
        else:
            filepath = self.file_list[index]
            img = self.read_image_file(filepath)
            img = img.scaled(653, 397, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(QPixmap.fromImage(img))

    def open_full_size_window(self, _=None):
        """function to open full size image in new window"""
        index = self.file_list_box.currentRow()
        if not self.file_list or index == -1:  # don't open full size image if default or empty
            return
        filepath = self.file_list[index]
        img = self.read_image_file(filepath)
        full_size_dialog = QLabel(self, Qt.Window)
        full_size_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        full_size_dialog.setPixmap(QPixmap.fromImage(img))
        full_size_dialog.setWindowTitle("Photo Deputy - Full Size")
        # Set icon to the selected image
        icon = QIcon(QPixmap.fromImage(img))
        full_size_dialog.setWindowIcon(icon)

        # Get the dimensions of the desktop and full size dialog
        desktop = QDesktopWidget().screenGeometry()
        dialog_rect = full_size_dialog.geometry()
        # Calculate the center point of the screen
        center_point = desktop.center()
        # Calculate the top-left corner of the dialog to center it
        top_left = center_point - dialog_rect.center()

        full_size_dialog.move(top_left)
        full_size_dialog.show()
        full_size_dialog.raise_()

    def save_single_image(self):
        index = self.file_list_box.currentRow()
        if not self.file_list or index < 0 or index >= len(self.file_list):
            return

        filepath = self.file_list[index]
        suggested_title = self.extract_title(filepath)
        suggested_timestamp = self.extract_meta(filepath).get("creat", None)
        if suggested_title is not None and suggested_timestamp is not None:
            formatted_title = suggested_title.replace(" ", "_")
            formatted_timestamp = self.dolerean(suggested_timestamp)
            suggested_filename = f"{formatted_title}_{formatted_timestamp}.jpg"
        else:
            suggested_filename = os.path.basename(filepath)  # If metadata is not available

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", suggested_filename,
                                                   "JPEG images (*.jpg);;PNG images (*.png);;All files (*.*)")

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

        output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if not output_dir:
            return

        save_format = self.select_format()
        if not save_format:
            return

        total_files = len(self.file_list)
        progress_dialog = QProgressDialog("Converting Files...", "Cancel", 0, total_files, self)
        progress_dialog.setWindowTitle("Conversion Progress")
        progress_dialog.setWindowModality(Qt.WindowModal)

        converted_count = 0
        for index, file_path in enumerate(self.file_list):
            if progress_dialog.wasCanceled():
                break

            title = self.extract_title(file_path)
            json_data = self.extract_meta(file_path)
            if title is None or json_data is None:
                continue

            timestamp = json_data.get("creat", None)
            formatted_title = title.replace(" ", "_")
            formatted_timestamp = self.dolerean(timestamp)  # Convert timestamp to formatted datetime
            filename = f"{formatted_title}_{formatted_timestamp}.{save_format}"

            img = self.read_image_file(file_path)
            save_path = os.path.join(output_dir, filename)
            img.save(save_path)

            converted_count += 1
            progress_dialog.setValue(converted_count)
            progress_dialog.setLabelText(f"Converting {converted_count} / {total_files} files...")
            QApplication.processEvents()

        progress_dialog.close()

        QMessageBox.information(self, "Success", f"All images converted and saved in {output_dir}")


if __name__ == '__main__':
    app = QApplication([])
    photo_deputy = PhotoDeputy()
    app.exec_()