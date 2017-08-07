
from index import Ui_IndexWindow
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QApplication, QAction, QFileDialog, QTextEdit,QMessageBox
from upload import Upload
import os
import _thread

class mywindow(QtWidgets.QMainWindow,Ui_IndexWindow):
    upload = 0
    fileSignal = QtCore.pyqtSignal(str)
    progressSignal = QtCore.pyqtSignal(int,int)

    def __init__(self):
        super(mywindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("七牛上传辅助工具V1.0")
        self.putFileBtn.clicked.connect(self.submit)
        self.openFileBtn.clicked.connect(self.showFileSelector)
        self.bucketSpinner.addItem("kingmahjong-test")
        self.bucketSpinner.addItem("kingmahjong")
        self.originPathEdit.setPlaceholderText('如C://aaa/abc/或C://aaa/abc.jpg')
        self.destPathEdit.setPlaceholderText('如res/image/或res/image/abc.jpg')
        self.destPathEdit.textChanged.connect(self.resetUrl)
        self.originPathEdit.textChanged.connect(self.resetUrl)
        self.fileSignal.connect(self.printMsg)
        self.progressSignal.connect(self.updateProgress)
        self.upload = Upload()

    # 显示文件选择器
    def showFileSelector(self):
        # 如果打开文件夹
        if self.dirRadio.isChecked():
            filename = QFileDialog.getExistingDirectory(self, "请选择要上传的文件夹", './')
            self.originPathEdit.setText(filename)
        else:
            filename,_ = QFileDialog.getOpenFileName(self,'请选择要上传的文件','./')
            self.originPathEdit.setText(filename)

    def resetUrl(self):
        originPath = self.originPathEdit.text()
        destPath = self.destPathEdit.text()
        pos = originPath.rfind("/")
        url = 'http://xxx.cn/'+destPath+originPath[pos+1:]
        self.urlEdit.setText(url)

    # 打印上传数据
    def printMsg(self,str):
        self.msgTextEdit.appendPlainText(str)

    def updateProgress(self,progress,totalNum):
        radio = int((progress/totalNum)*100)
        if progress > 0: self.progressLabel.setText('当前进度:'+str(radio)+"%("+str(progress)+"/"+str(totalNum)+")")
        else: self.progressLabel.setText('当前进度:'+str(radio)+"%")
        if radio == 100:
            self.putFileBtn.setEnabled(True)

    # 上传单个文件
    def putFile(self):
        # 获取源文件路径
        originPath = self.originPathEdit.text()
        # 获取保存路径
        destPath = self.destPathEdit.text()
        pos = originPath.rfind("/")
        # 判断保存最后一位是否为"/"
        if pos == len(originPath)-1:
            # 如果最后一位是"/"，则不需要修改上传文件名
            key = destPath + originPath[pos+1:]
        else:
            # 如果最后一位不是"/"，则修改上传文件名
            key = destPath
        self.fileSignal.emit("上传文件:" + originPath)
        self.fileSignal.emit("访问路径:" + key)
        # 设置当前bucketName
        bucketName = self.bucketSpinner.currentText()
        self.upload.setBucketName(bucketName)
        ret, _ = self.upload.putFile(originPath, key)
        if ret['key'] == '':
            self.fileSignal.emit("上传失败！")
        else:
            self.fileSignal.emit("上传成功！")
        self.progressSignal.emit(1,1)

    def putDir(self):
        # 设置当前bucketName
        bucketName = self.bucketSpinner.currentText()
        self.upload.setBucketName(bucketName)
        originPath = self.originPathEdit.text()
        destPath = self.destPathEdit.text()
        totalNum = sum([len(x) for _, _, x in os.walk(originPath)])
        progress = 0
        for root, dirs, files in os.walk(originPath):
            for name in files:
                origin = root.replace("\\","/")
                origin = origin+'/'+name
                pos = originPath.rfind("/")
                key = destPath + originPath[pos+1:] + "/" + name
                # print(origin)
                # print(key)
                self.fileSignal.emit("上传文件:" + origin)
                self.fileSignal.emit("访问路径:" + key)
                ret, _ = self.upload.putFile(origin, key)
                if ret['key'] == '':
                    self.fileSignal.emit("上传失败！")
                else:
                    self.fileSignal.emit("上传成功！")
                progress += 1
                self.progressSignal.emit(progress,totalNum)

    def submit(self):
        # 清空进度条和消息框
        self.progressSignal.emit(0, 1)
        self.msgTextEdit.clear()
        # 上传的是文件夹
        if self.dirRadio.isChecked():
            path = self.originPathEdit.text()
            if os.path.isdir(path):
                self.putFileBtn.setEnabled(False)
                _thread.start_new_thread(self.putDir,())
            else:
                self.putFileBtn.setEnabled(True)
                QMessageBox.warning(self,"提示","文件夹不存在")
        else:
            path = self.originPathEdit.text()
            if os.path.isfile(path):
                self.putFileBtn.setEnabled(False)
                _thread.start_new_thread(self.putFile,())
            else:
                self.putFileBtn.setEnabled(True)
                QMessageBox.warning(self,"提示","文件不存在")



if __name__=="__main__":
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())