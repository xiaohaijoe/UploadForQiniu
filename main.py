
from index import Ui_IndexWindow
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtWidgets import QApplication, QAction, QFileDialog, QTextEdit,QMessageBox
from upload import Upload
from urllib import request
import os
import _thread
import time

class mywindow(QtWidgets.QMainWindow,Ui_IndexWindow):
    upload = 0
    fileSignal = QtCore.pyqtSignal(str)
    progressSignal = QtCore.pyqtSignal(int,int)

    buckets = [
        {
            "bucket": "kingmahjong-test",
            "domain": "http://restest.xinxingtech.cn/"
        },
        {
            "bucket": "kingmahjong",
            "domain": "http://res.xinxingtech.cn/"
        }
    ]

    def __init__(self):
        super(mywindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("七牛上传辅助工具V1.0")
        self.putFileBtn.clicked.connect(self.submit)                # 上传按钮
        self.putUnityBtn.clicked.connect(self.submitUnity)                # Unity热更新上传按钮
        self.openFileBtn.clicked.connect(self.showFileSelector)
        # self.bucketSpinner.addItem("kingmahjong-test")
        # self.bucketSpinner.addItem("kingmahjong")
        for item in self.buckets:
            self.bucketSpinner.addItem(item["bucket"])
        self.originPathEdit.setPlaceholderText('如C://aaa/abc/或C://aaa/abc.jpg')
        self.destPathEdit.setPlaceholderText('如res/image/或res/image/abc.jpg(选填)')
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
        originPos = originPath.rfind("/")
        destPos = destPath.rfind("/")
        if self.dirRadio.isChecked():
            # ---------------------上传文件夹时----------------
            # originPath    -> C:/Users/xxx/Desktop/ttt
            # destPath      -> res/image/
            # url           -> http://xxx.cn/res/image/ttt
            # ------------------------------------------------
            url = 'http://xxx.cn/' + destPath + originPath[originPos + 1:]
        else:
            if destPos == len(destPath)-1 :
                # ---------------------上传文件时1----------------
                # originPath    -> C:/Users/xxx/Desktop/ttt/abc.jpg
                # destPath      -> res/image/
                # url           -> http://xxx.cn/res/image/abc.jpg
                # ------------------------------------------------
                url = 'http://xxx.cn/' + destPath + originPath[originPos + 1:]
            else:
                # ---------------------上传文件时2----------------
                # originPath    -> C:/Users/xxx/Desktop/ttt/abc.jpg
                # destPath      -> res/image/ccc.jpg
                # url           -> http://xxx.cn/res/image/ccc.jpg
                # ------------------------------------------------
                url = 'http://xxx.cn/' + destPath
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
            self.putUnityBtn.setEnabled(True)

    # 上传单个文件
    def putFile(self):
        # 获取源文件路径
        originPath = self.originPathEdit.text()
        # 获取保存路径
        destPath = self.destPathEdit.text()
        lastPos = destPath.rfind("/")
        # 判断保存最后一位是否为"/"
        if lastPos == len(destPath)-1:
            # originPath    -> C:/User/xxx/Desktop/abcd.jpg
            # destPath      -> res/image/
            # key           -> res/image/abcd.jpg
            # filename      -> abcd.jpg
            filename = originPath[originPath.rfind("/")+1:]
            # 如果最后一位是"/"，则不需要修改上传文件名
            key = destPath + filename
        else:
            # originPath    -> C:/User/xxx/Desktop/abcd.jpg
            # destPath      -> res/image/bbb.png
            # key           -> res/image/bbb.png
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
        self.progressSignal.emit(1, 1)

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
                # originPath->C:/User/xxx/Desktop/ttt
                # pos       ->                   ↑
                # origin    ->C:/User/xxx/Desktop/ttt/bb/cc
                # destPath  ->res/image/
                # relPath   ->ttt/bb/cc/
                # absPath   ->C:/User/xxx/Desktop/ttt/bb/cc/abc.jpg
                # key       ->res/image/ttt/bbb/cc/abc.jpg
                origin = root.replace("\\", "/")
                # 找到最后一个'/'出现的地方
                pos = originPath.rfind("/")
                relPath = origin[pos+1:]+"/"
                absPath = origin + "/" + name
                key = destPath + relPath + name
                self.fileSignal.emit("上传文件:" + absPath)
                self.fileSignal.emit("访问路径:" + key)
                ret, _ = self.upload.putFile(absPath, key)
                if ret['key'] == '':
                    self.fileSignal.emit("上传失败！")
                else:
                    self.fileSignal.emit("上传成功！")
                progress += 1
                self.progressSignal.emit(progress, totalNum)

    def putUnity(self):
        # originPath     ->C:/User/xxx/Desktop/ttt
        # destPath       ->res/image/
        bucketName = self.bucketSpinner.currentText()
        originPath = self.originPathEdit.text()
        destPath = self.destPathEdit.text()
        # absFolder            -> C:/User/xxx/Desktop/ttt/android/StreamingAssets/
        # absTxtPath           -> C:/User/xxx/Desktop/ttt/android/StreamingAssets/files.txt
        # destRelFolder        -> res/image/ttt/android/StreamingAssets/
        # destTxtRelPath       -> res/image/ttt/android/StreamingAssets/files.txt
        absFolder = ""                   # files.txt 绝对文件夹
        absTxtPath = ""                  # filex.txt 绝对路径
        destRelFolder = ""               # files.txt 所在目标文件夹
        destTxtRelPath = ""              # files.txt 所在目标路径

        # 遍历文件夹，寻找files.txt文件路径
        for root, dirs, files in os.walk(originPath):
            for name in files:
                if name == "files.txt":
                    absFolder = root.replace("\\", "/") + "/"
                    absTxtPath = absFolder + "files.txt"
                    pos = originPath.rfind("/")
                    destTxtRelPath = destPath + absTxtPath[pos+1:]
                    destRelFolder = destTxtRelPath[:destTxtRelPath.rfind("/")] + "/"
                    break

        # 如果找不到文件，则上传失败
        if absTxtPath == "":
            self.fileSignal.emit("找不到文件:files.txt")
            self.fileSignal.emit("上传失败！")
            self.putFileBtn.setEnabled(True)
            self.putUnityBtn.setEnabled(True)
            return
        else:
            self.fileSignal.emit("找到文件:" + absTxtPath)
            domain = ""
            # 下载远程files.txt文件
            for item in self.buckets:
                if item["bucket"] == bucketName:
                    domain = item["domain"]
                    break
            fileTxtUrl = domain + destTxtRelPath + "?t=" + str(int(time.time()))
            self.fileSignal.emit("读取文件:" + fileTxtUrl)
            try:
                file = request.urlopen(fileTxtUrl)
            except:
                # 如果找不到远程文件，则询问是否重新上传
                self.fileSignal.emit("找不到文件:"+fileTxtUrl)
                reply = QMessageBox.information(self, "提示", "找不到远程files.txt，是否新建上传?",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    llist = []
                    # 打开本地文件，也将内容保存到一个列表中
                    localFile = open(absTxtPath)
                    for line in localFile:
                        llist.append(line)

                    dlist = []
                    for sloc in llist:
                        sloc = sloc.strip()  # 去掉两边空格
                        ploc = sloc.rfind("|")
                        self.fileSignal.emit("需要更新:" + sloc[:ploc])
                        dlist.append(sloc[:ploc])

                    _thread.start_new_thread(self.putList, (dlist, absFolder, absTxtPath, destRelFolder, destTxtRelPath, ))
                    # self.putList()
                    return
                else:
                    self.fileSignal.emit("下载失败！")
                    self.putFileBtn.setEnabled(True)
                    self.putUnityBtn.setEnabled(True)
                return

            if file.getcode() == 200:
                rlist = []      # 远程files.txt内容列表
                llist = []      # 本地files.txt内容列表
                # 找到该文件，将内容保存到一个列表中
                for line in file:
                    rlist.append(line.decode('utf-8'))
                # 打开本地文件，也将内容保存到一个列表中
                localFile = open(absTxtPath)
                for line in localFile:
                    llist.append(line)

                print(len(rlist), len(llist))

                # 遍历两个files.txt内容，将远程与本地不一样的行,或者远程没有的行，存储起来
                dlist = []
                num = 0
                for sloc in llist:
                    isExist = False  # 文件是否存在
                    sloc = sloc.strip()  # 去掉两边空格
                    ploc = sloc.rfind("|")
                    for srem in rlist:
                        # 根据'|'分割字符串
                        srem = srem.strip()  # 去掉两边空格
                        prem = srem.rfind("|")
                        if sloc[:ploc] == srem[:prem]:
                            isExist = True
                            if sloc[ploc + 1:] != srem[prem + 1:]:
                                num += 1
                                self.fileSignal.emit("需要更新:" + sloc[:ploc])
                                dlist.append(sloc[:ploc])
                    if not isExist:
                        self.fileSignal.emit("需要更新:" + sloc[:ploc])
                        dlist.append(sloc[:ploc])

                print(num)
                _thread.start_new_thread(self.putList, (dlist, absFolder, absTxtPath, destRelFolder, destTxtRelPath,))
                # self.putList(dlist, absFolder, absTxtPath, destRelFolder, destTxtRelPath)
            else:
                self.fileSignal.emit("找不到文件:"+fileTxtUrl)
                self.fileSignal.emit("下载失败！")
                self.putFileBtn.setEnabled(True)
                self.putUnityBtn.setEnabled(True)
                return
        return

    # 上传列表
    # absFolder            -> C:/User/xxx/Desktop/ttt/android/StreamingAssets/
    # absTxtPath           -> C:/User/xxx/Desktop/ttt/android/StreamingAssets/files.txt
    # destRelFolder        -> res/image/ttt/android/StreamingAssets/
    # destTxtRelPath       -> res/image/ttt/android/StreamingAssets/files.txt
    def putList(self, dlist, absFolder, absTxtPath, destRelFolder, destTxtRelPath):
        if len(dlist) == 0:
            self.fileSignal.emit("没有可以更新的文件...")
            self.fileSignal.emit("更新完成...")
            self.progressSignal.emit(1, 1)
            self.putFileBtn.setEnabled(True)
            self.putUnityBtn.setEnabled(True)
        else:
            dlist.append("files.txt")
            self.fileSignal.emit("需要更新文件一共:" + str(len(dlist)) + "个")
            # 上传文件
            progress = 0
            totalNum = len(dlist)
            # 设置当前bucketName
            bucketName = self.bucketSpinner.currentText()
            self.upload.setBucketName(bucketName)
            for item in dlist:
                absPath = absFolder + item
                key = destRelFolder + item
                metaPath = absPath + ".meta"
                metaKey = key + ".meta"
                self.fileSignal.emit("上传文件:" + absPath)
                self.fileSignal.emit("访问路径:" + key)
                ret, _ = self.upload.putFile(absPath, key)
                if ret['key'] == '':
                    self.fileSignal.emit("上传失败！")
                else:
                    self.fileSignal.emit("上传成功！")
                # self.fileSignal.emit("上传成功！")
                self.fileSignal.emit("上传文件:" + metaPath)
                self.fileSignal.emit("访问路径:" + metaKey)
                ret, _ = self.upload.putFile(metaPath, metaKey)
                if ret['key'] == '':
                    self.fileSignal.emit("上传失败！")
                else:
                    self.fileSignal.emit("上传成功！")
                # self.fileSignal.emit("上传成功！")
                progress += 1
                self.progressSignal.emit(progress, totalNum)

    def submit(self):
        # 清空进度条和消息框
        self.progressSignal.emit(0, 1)
        self.msgTextEdit.clear()
        # 上传的是文件夹
        if self.dirRadio.isChecked():
            path = self.originPathEdit.text()
            if os.path.isdir(path):
                self.putFileBtn.setEnabled(False)
                self.putUnityBtn.setEnabled(False)
                _thread.start_new_thread(self.putDir, ())
            else:
                self.putFileBtn.setEnabled(True)
                self.putUnityBtn.setEnabled(True)
                QMessageBox.warning(self, "提示", "文件夹不存在")
        else:
            path = self.originPathEdit.text()
            if os.path.isfile(path):
                self.putFileBtn.setEnabled(False)
                self.putUnityBtn.setEnabled(False)
                _thread.start_new_thread(self.putFile,())
            else:
                self.putFileBtn.setEnabled(True)
                self.putUnityBtn.setEnabled(True)
                QMessageBox.warning(self, "提示", "文件不存在")

    def submitUnity(self):
        # 清空进度条和消息框
        self.progressSignal.emit(0, 1)
        self.msgTextEdit.clear()
        if not self.dirRadio.isChecked():
            QMessageBox.warning(self, "提示", "请选择文件夹上传类型")
            return
        path = self.originPathEdit.text()
        if os.path.isdir(path):
            self.putFileBtn.setEnabled(False)
            self.putUnityBtn.setEnabled(False)
            self.putUnity()
        else:
            self.putFileBtn.setEnabled(True)
            self.putUnityBtn.setEnabled(True)
            QMessageBox.warning(self, "提示", "文件夹不存在")



if __name__=="__main__":
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())