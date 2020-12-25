# -*- coding: utf-8 -*-
import sys
import csv
import cv2
import pytesseract
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import SnippingTool

language = 'eng'


class DetectWord:
    def __init__(self, languae, image, pathFileResult):
        self.languae = languae
        self.image = image
        self.pathFileResult = pathFileResult

    def pre_processing(self):
        """
        This function take one argument as
        input. this function will convert
        input image to binary image
        :param image: image
        :return: thresholded image
        """
        imgUMat = cv2.imread(self.image)
        gray_image = cv2.cvtColor(imgUMat, cv2.COLOR_BGR2GRAY)
        # converting it to binary image
        threshold_img = cv2.threshold(
            gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # saving image to view threshold image
        cv2.imwrite('thresholded.png', threshold_img)
        cv2.imshow('threshold image', threshold_img)
        # Maintain output window until
        # user presses a key
        # cv2.waitKey(0)
        # Destroying present windows on screen
        cv2.destroyAllWindows()

        return threshold_img

    def parse_text(self, threshold_img):
        """
        This function take one argument as
        input. this function will feed input
        image to tesseract to predict text.
        :param threshold_img: image
        return: meta-data dictionary
        """
        # configuring parameters for tesseract
        tesseract_config = r'--oem 3 --psm 6'
        # now feeding image to tesseract
        # your path may be different
        pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
        details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT,
                                            config=tesseract_config, lang=self.languae)
        # vie
        return details

    def draw_boxes(self, thresholds_image, details, threshold_point):
        """
        This function takes three argument as
        input. it draw boxes on text area detected
        by Tesseract. it also writes resulted image to
        your local disk so that you can view it.
        :param image: image
        :param details: dictionary
        :param threshold_point: integer
        :return: None
        """
        total_boxes = len(details['text'])
        for sequence_number in range(total_boxes):
            if int(details['conf'][sequence_number]) > threshold_point:
                (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number],
                                details['width'][sequence_number], details['height'][sequence_number])
                thresholds_image = cv2.rectangle(
                    thresholds_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # saving image to local
        cv2.imwrite('captured_text_area.png', thresholds_image)
        # display image
        cv2.imshow('captured text', thresholds_image)
        # Maintain output window until user presses a key
        # cv2.waitKey(0)
        # Destroying present windows on screen
        cv2.destroyAllWindows()

    def format_text(self, details):
        """
        This function take one argument as
        input.This function will arrange
        resulted text into proper format.
        :param details: dictionary
        :return: list
        """
        parse_text = []
        word_list = []
        last_word = ''
        for word in details['text']:
            if word != '':
                word_list.append(word)
                last_word = word
            if (last_word != '' and word == '') or (word == details['text'][-1]):
                parse_text.append(word_list)
                word_list = []
        return parse_text

    def write_text(self, formatted_text):
        """
        This function take one argument.
        it will write arranged text into
        a file.
        :param formatted_text: list
        :return: None
        """
        print(formatted_text)
        with open(self.pathFileResult, 'w', newline="", encoding="utf-8") as file:
            csv.writer(file, delimiter=" ").writerows(formatted_text)

    def excute(self):
        # calling pre_processing function to perform pre-processing on input image.
        thresholds_image = self.pre_processing()
        # calling parse_text function to get text from image by Tesseract.
        parsed_data = self.parse_text(thresholds_image)
        # defining threshold for draw box
        accuracy_threshold = 30
        # calling draw_boxes function which will draw dox around text area.
        self.draw_boxes(thresholds_image, parsed_data, accuracy_threshold)
        # calling format_text function which will format text according to input image
        arranged_text = self.format_text(parsed_data)
        # calling write_text function which will write arranged text into file
        self.write_text(arranged_text)
        f = open(self.pathFileResult, mode="r", encoding="utf-8")
        return f.read()


class MainWindow(QMainWindow):

    def __init__(self, image=''):
        super().__init__()

        self.setObjectName("MainWindow")

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setStyleSheet("background-color: #F0F2F5;")

        self.labelImg = QLabel(self.centralwidget)
        self.labelImg.setGeometry(QRect(50, 20, 260, 260))
        self.labelImg.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.labelImg.setObjectName("labelImg")
        self.labelImg.setStyleSheet(
            "background-color: gray;border: 1px solid black;")

        self.btnChooseImage = QPushButton(self.centralwidget)
        self.btnChooseImage.setGeometry(QRect(70, 290, 110, 23))
        self.btnChooseImage.setObjectName("btnChooseImage")
        self.btnChooseImage.clicked.connect(self.openFileNameDialog)

        self.btnSreenShot = QPushButton(self.centralwidget)
        self.btnSreenShot.setGeometry(QRect(200, 290, 110, 23))
        self.btnSreenShot.setObjectName("btnSreenShot")
        self.btnSreenShot.clicked.connect(self.screenShot)

        self.lbChooseLanguage = QLabel(self.centralwidget)
        self.lbChooseLanguage.setGeometry(QRect(70, 320, 110, 23))
        self.lbChooseLanguage.setObjectName("lbChooseLanguage")

        self.cbChooseLanguage = QCheckBox(self.centralwidget)
        self.cbChooseLanguage.setGeometry(QRect(135, 320, 110, 23))
        self.cbChooseLanguage.setObjectName("cbChooseLanguage")
        self.cbChooseLanguage.stateChanged.connect(self.clickBox)
        global language
        if language == 'vie':
            self.cbChooseLanguage.setChecked(True)

        self.btnStart = QPushButton(self.centralwidget)
        self.btnStart.setGeometry(QRect(300, 340, 111, 23))
        self.btnStart.setObjectName("btnStart")
        self.btnStart.clicked.connect(self.startProcess)

        self.txtResult = QTextEdit(self.centralwidget)
        self.txtResult.setGeometry(QRect(400, 20, 260, 260))
        self.txtResult.setObjectName("txtResult")

        self.labelResult = QLabel(self.centralwidget)
        self.labelResult.setGeometry(QRect(340, 120, 47, 13))
        self.labelResult.setObjectName("labelResult")

        if image != '':
            self.labelImg.setPixmap(QPixmap(image).scaled(
                self.labelImg.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image = image
        self.snippingTool = SnippingTool.SnippingWidget()
        self.resize(710, 380)
        self.setWindowTitle("Chương trình đọc chữ từ hình ảnh")
        self.setCentralWidget(self.centralwidget)
        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)
        self.show()

        # cv2.waitKey(0)

    def clickBox(self, state):
        global language
        if state == Qt.Checked:
            language = 'vie'
        else:
            language = 'eng'

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        # self.setWindowTitle(_translate(
        #     "MainWindow", "Chương trình đọc chữ từ hình ảnh"))
        self.labelImg.setText(_translate("MainWindow", ""))
        self.btnChooseImage.setText(_translate(
            "MainWindow", "Chọn ảnh từ bộ nhớ"))
        self.txtResult.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                          "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                          "p, li { white-space: pre-wrap; }\n"
                                          "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\" bgcolor=\"#b0e0e6\">\n"
                                          "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.labelResult.setText(_translate("MainWindow", "Kết quả"))
        self.btnStart.setText(_translate("MainWindow", "Bắt đầu quá trình"))
        self.cbChooseLanguage.setText(_translate("MainWindow", "Tiếng việt"))
        self.lbChooseLanguage.setText(_translate("MainWindow", "Ngôn ngữ:"))
        self.btnSreenShot.setText(_translate(
            "MainWindow", "Chụp ảnh màn hình"))

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self, "", r"<Default dir>", "Image files (*.jpg *.jpeg *.gif *.png)", options=options)
        if fileName:
            self.labelImg.setPixmap(QPixmap(fileName).scaled(
                self.labelImg.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image = fileName

    # TODO exit application when we exit all windows
    def closeEvent(self, event):
        sys.exit()

    def startProcess(self):
        if self.image != None:
            global language
            detectWord = DetectWord(language, self.image, "result.txt")
            self.txtResult.setText(detectWord.excute())

    def screenShot(self):
        # mở sniipng tool nek mà mở xong nó ko mỏ lại
        self.hide()
        self.snippingTool.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
