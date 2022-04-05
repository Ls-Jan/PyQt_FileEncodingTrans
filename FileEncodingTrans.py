'''
【XJ自制脚本(于2021年12月20日完成)】
这个脚本花了一整天完成的。
因为VS2019和QtCreator来回拖文件而且文件编码还不一致，导致了每次运行前都要手动选择编码(否则就显示乱码)。
一次两次就算了，但反复提示重选编码。实在受不了，就花了一天时间去写这个东西。
运行效果个人感觉还行，能跑，作为以后常用的工具使用。

因为编码判断是依据函数chardet.detect的，所以如果它判断失误的话转码出的文件必将乱码，
所以不要把导出目录选择在源目录下导致源文件被覆写。
编码判断错误不是一次两次的了所以需要注意转码后是否出现乱码
'''

import chardet
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt,QModelIndex,QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem,QFont
from PyQt5.QtWidgets import *


class XJ_TreeView(QTreeView):
    class XJ_Iter:
        def __init__(self,iter):
            self.__iter=iter

        def AppendRow(self,data):#添加数据(一个列表
            lst=[]
            for i in data:
                lst.append(QStandardItem(str(i)))
                lst[-1].setEditable(False)
            self.__iter.appendRow(lst)
            return XJ_TreeView.XJ_Iter(lst[0])
        
        def Copy(self):
            return XJ_TreeView.XJ_Iter(self.__iter)
            
        def Back(self):#返回上一级(返回失败则返回false
            if(type(self.__iter)==QStandardItemModel):
                return False
            if(self.__iter.parent()==None):
                self.__iter=self.__iter.model()
            else:
                self.__iter=self.__iter.parent()
            return True
            
        def Next(self,i):#进入下一级(进入失败则返回false
            if(0<=i<self.__iter.rowCount()):
                if(type(self.__iter)!=QStandardItemModel):
                    self.__iter=self.__iter.child(i,0)
                else:
                    self.__iter=self.__iter.itemFromIndex(self.__iter.index(i,0))
                return True
            else:
                return False
                
        def GetData(self):#获取数据(一个列表
            if(type(self.__iter)==QStandardItemModel):
                return None
            result=[]
            model=self.__iter.model()
            index=self.__iter.index()
            i=0
            while(index.isValid()):
                result.append(model.itemFromIndex(index).text())
                i+=1
                index=index.siblingAtColumn(i)
            return result
            
        def SetData(self,i,data):#设置第i个单元格的内容(设置失败则返回false
            if(type(self.__iter)==QStandardItemModel):
                return False
            model=self.__iter.model()
            index=self.__iter.index().siblingAtColumn(i)
            if(index.isValid()==False):
                return False
            item=model.itemFromIndex(index)
            item.setText(str(data))
            return True
            
        def SetFont(self,i,font):#设置第i个单元格的字体样式(设置失败则返回false
            if(type(self.__iter)==QStandardItemModel):
                return False
            model=self.__iter.model()
            index=self.__iter.index().siblingAtColumn(i)
            item=model.itemFromIndex(index)
            item.setFont(font)
            return True
        
        def SetCheckable(self,flag):#设置是否显示复选框(设置失败则返回false)，复选框为双态
            if(type(self.__iter)==QStandardItemModel):
                return False
            self.__iter.setCheckable(flag)
            if(flag==False):
                self.__iter.setCheckState(-1)
            return True
            
        def GetCheckable(self):#获取复选框状态(如果获取失败则返回false)，返回结果为：【全选：Qt.Checked(2)、部分选：Qt.PartiallyChecked(1)、不选：Qt.Unchecked(0)】
            if(type(self.__iter)==QStandardItemModel):
                return None
            return self.__iter.checkState()
        
        def SetEditable(self,i,flag):#设置第i个单元格可以双击修改(设置失败则返回false
            if(type(self.__iter)==QStandardItemModel):
                return False
            model=self.__iter.model()
            index=self.__iter.index().siblingAtColumn(i)
            item=model.itemFromIndex(index)
            item.setEditable(flag)
            return True

    def __init__(self,parent=None):
        super(XJ_TreeView, self).__init__(parent)
        model=QStandardItemModel(self)
        self.setModel(model)
        self.headerLables=[]
    def GetHead(self):
        return XJ_TreeView.XJ_Iter(self.model())
    def Clear(self):
        width=[]
        for i in range(self.model().columnCount()):
            width.append(self.columnWidth(i))
        self.model().clear()
        self.model().setHorizontalHeaderLabels(self.headerLables)
        for i in range(len(width)):
            self.setColumnWidth(i,width[i])
    def SetHeaderLabels(self,labels):#设置列头
        self.headerLables=labels
        self.model().setHorizontalHeaderLabels(labels)
    
    
class XJ_LineEdit(QWidget):
    def __init__(self,parent=None,hint='提示文本：',input='内容文本',button='按钮文本'):
        super(XJ_LineEdit, self).__init__(parent)
        self.__hint=QLabel(hint,self)
        self.__input=QLineEdit(input,self)
        self.__button=QPushButton(button,self)
        hbox=QHBoxLayout()
        hbox.addWidget(self.__hint)
        hbox.addWidget(self.__input)
        hbox.addWidget(self.__button)
        self.setLayout(hbox)
        
    def SetText_Hint(self,tx):
        self.__hint.setText(tx)
    def SetText_Button(self,tx):
        self.__button.setText(tx)
    def GetText_Input(self):
        return self.__input.text()
    def SetText_Input(self,tx):
        self.__input.setText(tx)    
    def SetClicked_Button(self,func):
        self.__button.clicked.connect(func)
    def SetEnable_Input(self,flag):
        self.__input.setReadOnly(not flag)
    def SetEnable_Button(self,flag):
        self.__button.setVisible(flag)
    def GetWidget_Hint(self):
        return self.__hint
    def GetWidget_Input(self):
        return self.__input
    def GetWidget_Button(self):
        return self.__button
        

class XJ_ComboBox(QWidget):
    def __init__(self,parent=None,hint='下拉框：'):
        super(XJ_ComboBox, self).__init__(parent)
        self.__box=QComboBox(self)
        self.__hint=QLabel(hint,self)
        self.__mapping={}

        hbox=QHBoxLayout()
        hbox.addWidget(self.__hint)
        hbox.addWidget(self.__box)
        hbox.addStretch(1)
        self.setLayout(hbox)
        
    def AddItem(self,tx,status=''):#添加选项（添加失败则返回false
        if(self.__mapping.get(tx)!=None):
            return False
        self.__box.addItem(tx)
        if(len(status)==0):
            status=tx
        self.__mapping[tx]=status
        return True
    def GetStatus(self):#返回下拉框当前内容的状态（状态不存在则返回None
        return self.__mapping.get(self.__box.currentText())
    def Clear(self):#清空内容
        self.__box.clear()
        self.__mapping.clear()
    def SetHint(self,hint):#设置提示内容
        self.__hint.setText(hint)


class XJ_MainWindow(QDialog):
    def __init__(self,parent=None):
        super(XJ_MainWindow, self).__init__(parent)
        self.__originPath=XJ_LineEdit(self,'选择源目录  ：','','选择路径')#源路径
        self.__targetPath=XJ_LineEdit(self,'选择生成目录：','','选择路径')#目标路径
        self.__structure=XJ_TreeView(self)#源目录结构(多级树状表)
        self.__fileType=XJ_TreeView(self)#文件类型(带复选框)
        self.__targetEncoding=XJ_ComboBox(self,"目标编码：")#目标编码类型(下拉框)
        self.__analyzeFile=QPushButton('分析文件编码',self)#按钮，分析文件编码
        self.__transformFile=QPushButton('转换文件编码',self)#按钮，转换文件编码
        
        self.__mapping_structure={}#给self.__structure使用的。{文件名：树迭代器}
        self.__mapping_fileType={}#给self.__fileType使用的。{文件后缀：文件名集合}
        self.__font=QFont()#字体，给self.__structure使用的
        self.__fileMaxSize=1024#1024KB，即文件超过这个大小时不进行转码处理
        
        self.__originPath.SetClicked_Button(self.__ClickButton_Origin)
        self.__targetPath.SetClicked_Button(self.__ClickButton_Target)
        self.__analyzeFile.clicked.connect(self.__ClickButton_Analyze)
        self.__transformFile.clicked.connect(self.__ClickButton_Transform)
        self.__font.setBold(True)
        self.__originPath.SetEnable_Input(False)
        self.__targetPath.SetEnable_Input(False)
        self.__structure.SetHeaderLabels(['文件名/文件夹名','文件大小(KB)','文件编码','编码置信率'])
        self.__fileType.SetHeaderLabels(['文件后缀'])
        self.__targetEncoding.AddItem('UTF-8','utf-8')
        self.__targetEncoding.AddItem('UTF-8-BOM','UTF-8-SIG')
        self.__targetEncoding.AddItem('ANSI','ansi')
        self.__targetEncoding.AddItem('GBK','gbk')
        self.__targetEncoding.AddItem('GB2312','gb2312')
        
        vbox_sub_1=QVBoxLayout()#[分析按钮]与[转换按钮]纵向排布
        vbox_sub_1.addWidget(self.__analyzeFile)
        vbox_sub_1.addWidget(self.__transformFile)
        hbox_sub_1=QHBoxLayout()#[下拉框]与[布局vbox_sub_1]水平排布
        hbox_sub_1.addWidget(self.__targetEncoding)
        hbox_sub_1.addLayout(vbox_sub_1)
        vbox_sub_2=QVBoxLayout()#[文件类型]与[布局hbox_sub_1]纵向排布
        vbox_sub_2.addWidget(self.__fileType)
        vbox_sub_2.addLayout(hbox_sub_1)
        hbox_sub_2=QHBoxLayout()#[源目录结构]与[布局vbox_sub_2]水平排布
        hbox_sub_2.addWidget(self.__structure,2)
        hbox_sub_2.addLayout(vbox_sub_2,1)
        vbox_main=QVBoxLayout()#[源路径]与[目标路径]与[布局hbox_sub_2]纵向排布
        vbox_main.addWidget(self.__originPath)
        vbox_main.addWidget(self.__targetPath)
        vbox_main.addLayout(hbox_sub_2)
        self.setLayout(vbox_main)
        self.resize(1200,500)
        self.__structure.setColumnWidth(0,300)
        
    def __ClickButton_Origin(self):#self.__originPath对应按钮，点击之后对__structure、__fileType、__mapping_structure和__mapping_fileType进行设置
        path=QFileDialog.getExistingDirectory(self,"选择源目录")
        if(len(path)==0):
            return
        self.__originPath.SetText_Input(path)
        self.__structure.Clear()
        self.__fileType.Clear()
        
        map_Stru={}#之后会赋值给self.__mapping_structure
        map_File={}#之后会赋值给self.__mapping_fileType
        
        folder=path
        if(folder.rfind('/')!=-1):
            folder=folder[folder.rfind('/')+1:]
        map_Stru[path]=self.__structure.GetHead()#.AppendRow([folder,"","",""])
        for dirpath,dirnames,files in os.walk(path):
            for p in dirnames:
                thePath=os.path.join(dirpath,p)
                map_Stru[thePath]=map_Stru[dirpath].AppendRow([p,"","",""])
            for p in files:
                thePath=os.path.join(dirpath,p)
                map_Stru[thePath]=map_Stru[dirpath].AppendRow([p,str(round(os.path.getsize(thePath)/1024,2)),"",""])
                map_Stru[thePath].SetFont(0,self.__font)
                suffix='(无后缀)'#后缀
                if(p.rfind('.')!=-1):#获取后缀
                    suffix=p[p.rfind('.'):]
                if(map_File.get(suffix)==None):
                    map_File[suffix]=set()
                    self.__fileType.GetHead().AppendRow([suffix]).SetCheckable(True)
                map_File[suffix].add(thePath)
        self.__mapping_structure=map_Stru
        self.__mapping_fileType=map_File
        
    def __ClickButton_Target(self):#self.__targetPath对应按钮
        path=QFileDialog.getExistingDirectory(self,"选择生成目录")
        if(len(path)==0):
            return
        self.__targetPath.SetText_Input(path)

    def __ClickButton_Analyze(self):#分析源路径所有文件
        fileTypes=set()
        i=0
        iter=self.__fileType.GetHead()
        while(iter.Next(i)):
            if(iter.GetCheckable()==Qt.Checked):
                fileTypes.add(iter.GetData()[0])
            i+=1
            iter.Back()

        for type in fileTypes:
            files=self.__mapping_fileType[type]
            for file in files:
                iter=self.__mapping_structure[file]
                if(len(iter.GetData()[2])==0):
                    with open(file,'rb') as f:
                        info=chardet.detect(f.read())
                        iter.SetData(2,info['encoding'])#文件编码
                        iter.SetData(3,info['confidence'])#编码置信率

    def __ClickButton_Transform(self):#生成文件
        path_input=self.__originPath.GetText_Input()
        path_output=self.__targetPath.GetText_Input()
        
        if(len(path_output)==0):
            QMessageBox.warning(None,r'转换错误','请选择生成目录')
            return
        
        fileTypes=set()
        i=0
        iter=self.__fileType.GetHead()
        while(iter.Next(i)):
            if(iter.GetCheckable()==Qt.Checked):
                fileTypes.add(iter.GetData()[0])
            i+=1
            iter.Back()
        
        QMessageBox.information(None,r'开始转换','开始转换文件编码')
        encoding=self.__targetEncoding.GetStatus()
        for type in fileTypes:
            files=self.__mapping_fileType[type]
            for file in files:
                iter=self.__mapping_structure[file]
                if(len(iter.GetData()[2])!=0):
                    if(float(iter.GetData()[1])>self.__fileMaxSize):#文件过大时不考虑处理(过大的文件很可能不是文本文件)
                        continue
                    with open(file,'rb') as f:
                        if(file.find(path_input)!=-1):
                            file=file[file.find(path_input)+len(path_input)+1:]
                        targetFile=os.path.join(path_output,file)
                        targetPath=targetFile[:targetFile.rfind('\\')]
                        if(os.path.exists(targetPath)==False):
                            os.makedirs(targetPath)
                        try:
                            decoding=iter.GetData()[2]
                            data=f.read().decode(decoding).encode(encoding)
                            with open(targetFile,'wb') as w:
                                w.write(data)
                        except:
                            iter=iter.Copy()
                            file=iter.GetData()[0]
                            while(iter.Back()):
                                data=iter.GetData()
                                if(data!=None):
                                    file=data[0]+'/'+file
                            QMessageBox.warning(None,r'转换错误','编码为【{}】的文件【{}】在转码过程中出错！'.format(decoding,file))
        QMessageBox.information(None,r'转换完毕','文件已经完成转换')





if __name__=='__main__':
    app = QApplication(sys.argv)

    win=XJ_MainWindow()
    win.show()

    sys.exit(app.exec())













