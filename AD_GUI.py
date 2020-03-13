from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
                             QFormLayout, QGridLayout, QGroupBox,
                             QLabel, QLineEdit, QVBoxLayout, QMainWindow)
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import ezdxf
import math
import pandas as pd
from ApplyMethod import Otimizacao_ArmSimples
from ApplyMethod2 import Otimizacao_ArmDupla


#  Cálculo da reação de apoios
def biapoiada(q, L):
    # Cortante Q = q*L/2 - q*x
    # Momento: M = q*L*x/2 - q*(x**2)/2
    x = []
    y_Q = []
    y_M = []
    for i in range(101):
        step = (L/100)*i
        x.append(step)
        y_Q.append(q*L/2 - q*step)
        y_M.append(q*L*step/2 - q*(step**2)/2)

    return [x, y_Q, y_M, q*L/2, q*(L**2)/8]


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle('AutoDesign')
        self.setWindowIcon(QIcon('engineer.png'))
        self.dialog = Dialog()
        self.dialog2 = Dialog2()
        self.dialog3 = Dialog3()
        self.dialog4 = Dialog4()
        self.dialog5 = Dialog5()
        self.dialog6 = Dialog6()
        self.chart = Chart()
        self.initUI()

    def initUI(self):
        self.mainMenu = self.menuBar()
        self.saveMenu = self.mainMenu.addMenu("File")
        self.helpMenu = self.mainMenu.addMenu("Help")
        self.setStyleSheet("""
                QMenuBar {
                    background-color: rgb(49,49,49);
                    color: rgb(255,255,255);
                    border: 1px solid #000;
                }

                QMenuBar::item {
                    background-color: rgb(49,49,49);
                    color: rgb(255,255,255);
                }

                QMenuBar::item::selected {
                    background-color: rgb(30,30,30);
                }

                QMenu::item::selected {
                    background-color: rgb(30,30,30);
                }
            """)

        self.label = QtWidgets.QLabel(self)
        self.label.setText("Beam Optimizer")
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setGeometry(QtCore.QRect(300, 10, 211, 51))
        self.label.move(300, 30)

        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(-50, 0, 900, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.move(0, 75)

        self.label2 = QtWidgets.QLabel(self)
        self.label2.setText("Informações sobre a viga")
        font2 = QtGui.QFont()
        font2.setPointSize(10)
        font2.setBold(False)
        self.label2.setFont(font2)
        self.label2.setGeometry(QtCore.QRect(300, 300, 300, 300))
        self.label2.move(150, 5)

        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText("Resultados")
        font3 = QtGui.QFont()
        font3.setPointSize(10)
        font3.setBold(False)
        self.label3.setFont(font3)
        self.label3.setGeometry(QtCore.QRect(300, 300, 300, 300))
        self.label3.move(440, 5)

        self.label4 = QtWidgets.QLabel(self)
        self.label4.setText("AutoDesign©2019 - Todos os direitos reservados")
        font4 = QtGui.QFont()
        font4.setPointSize(8)
        self.label4.setFont(font4)
        self.label4.setGeometry(QtCore.QRect(300, 300, 300, 300))
        self.label4.move(250, 300)

        self.button = QtWidgets.QPushButton(self)
        self.button.setText("Dados Projeto")
        self.button.move(180, 180)
        self.button.clicked.connect(self.clicked)

        self.button2 = QtWidgets.QPushButton(self)
        self.button2.setText("CAA")
        self.button2.move(180, 300)
        self.button2.clicked.connect(self.clicked2)

        self.button3 = QtWidgets.QPushButton(self)
        self.button3.setText("Armadura")
        self.button3.move(180, 220)
        self.button3.clicked.connect(self.clicked3)

        self.button4 = QtWidgets.QPushButton(self)
        self.button4.setText("Apoios")
        self.button4.move(180, 260)
        self.button4.clicked.connect(self.clicked4)

        self.button5 = QtWidgets.QPushButton(self)
        self.button5.setText("Diagramas")
        self.button5.move(430, 180)
        self.button5.clicked.connect(self.clicked5)

        self.button6 = QtWidgets.QPushButton(self)
        self.button6.setText("Otimizar")
        self.button6.move(430, 220)
        self.button6.clicked.connect(self.optimize)

        self.button7 = QtWidgets.QPushButton(self)
        self.button7.setText("Desenhar")
        self.button7.move(430, 300)
        self.button7.clicked.connect(self.draw)

        self.button8 = QtWidgets.QPushButton(self)
        self.button8.setText("Relatório")
        self.button8.move(430, 260)
        self.button8.clicked.connect(self.clicked6)


    def clicked(self):
        self.dialog.show()

    def clicked2(self):
        self.dialog2.show()

    def clicked3(self):
        self.dialog3.show()

    def clicked4(self):
        self.dialog4.show()

    def clicked5(self):
        self.chart.show()

    def clicked6(self):
        if pd.read_csv('tipo.txt').columns[0] == 'Simples':
            self.dialog5.show()
        else:
            self.dialog6.show()

    def optimize(self):
        def get_cobrimento():
            caa = int(pd.read_csv('caa.txt').columns[0])
            if caa == 1:
                return 25
            elif caa == 2:
                return 30
            elif caa == 3:
                return 40
            else:
                return 50

        project_data = pd.read_csv('project_data.txt')
        variables = {'fck': float(project_data.columns[0]),
                     'fyk': float(project_data.columns[1]),
                     'mk': biapoiada(float(project_data.columns[2]), float(project_data.columns[3]))[4],
                     'vsk': biapoiada(float(project_data.columns[2]), float(project_data.columns[3]))[3],
                     'L': float(project_data.columns[3]),
                     'h': float(project_data.columns[4]),
                     'Cobrimento': get_cobrimento()}
        print(variables)
        tipo = pd.read_csv('tipo.txt').columns[0]
        if tipo == 'Simples':
            try:
                output = Otimizacao_ArmSimples(variables, 0.12)
                results = [output['bw'], output['h'], output['L'],
                           output['d'], output['x'], output['dl'],
                           output['nl'], output['dt'], output['nt'], variables['Cobrimento'],
                           output['sh'], variables['vsk'], variables['mk'], 0, 0]

                def write_results(results_list):
                    f = open("results.txt", "w+")
                    for result in results_list:
                        f.write(str(result) + ",")
                    f.close()

                write_results(results)

                QtWidgets.QMessageBox().about(self, "Otimização", "Otimização Finalizada!")
            except:
                QtWidgets.QMessageBox().about(self, "Otimização", "Erro na Otimização")
        else:
            try:
                output = Otimizacao_ArmDupla(variables, 0.12)
                results = [output['bw'], output['h'], output['L'],
                           output['d'], output['dl_inf'], output['dl_sup'],
                           output['nl_inf'], output['nl_sup'], output['dt'], output['nt'],
                           variables['Cobrimento'], output['sh_inf'], output['sh_sup'],
                           variables['vsk'], variables['mk']]

                def write_results(results_list):
                    f = open("results.txt", "w+")
                    for result in results_list:
                        f.write(str(result) + ",")
                    f.close()

                write_results(results)

                QtWidgets.QMessageBox().about(self, "Otimização", "Otimização Finalizada!")
            except:
                QtWidgets.QMessageBox().about(self, "Otimização", "Erro na Otimização")


    def draw(self):
        tipo = pd.read_csv('tipo.txt').columns[0]
        if tipo == 'Simples':
            dialog = QtWidgets.QFileDialog()
            folder_path = dialog.getExistingDirectory(None, "Select Folder")
            f = open('results.txt', 'r')
            if f.mode == 'r':
                contents = f.read()
            r = contents.split(',')
            print(r)
            bw = float(r[0])
            h = float(r[1])/100
            diametro_long = float(r[5])/1000
            n_long = float(r[6])
            diametro_trans = float(r[7])/1000
            cobrimento = float(r[9])/1000
            sh = float(r[10])/1000
            d_sup_min = 5/1000

            dwg = ezdxf.new('R2018')
            msp = dwg.modelspace()
            dwg.layers.new(name='Viga', dxfattribs={'linetype': 'Continuous', 'color': 7})
            dwg.layers.new(name='Armadura', dxfattribs={'linetype': 'Continuous', 'color': 5})
            dwg.layers.new(name='Cotas', dxfattribs={'linetype': 'Continuous', 'color': 2})
            dwg.styles.new(name='descricao_armadura', dxfattribs={'font': 'times.ttf', 'width': 8})

            def coord_points(number_of_points):
                points = []
                for i in range(int(number_of_points)):
                    points.append((cobrimento + diametro_trans + (2 * i + 1) * diametro_long / 2 + i * sh,
                                   cobrimento + diametro_trans))
                return points

            # ALTERAR PARA N BARRAS
            p_viga_1 = (0, 0)
            p_viga_2 = (bw, 0)
            p_viga_3 = (bw, h)
            p_viga_4 = (0, h)
            poly_01 = [p_viga_1, p_viga_2, p_viga_3, p_viga_4, p_viga_1]
            msp.add_lwpolyline(poly_01, dxfattribs={'layer': 'Viga'})

            raio = diametro_long / 2
            for j in range(int(n_long)):
                msp.add_circle(coord_points(n_long)[j], raio, dxfattribs={'layer': 'Armadura'})

            p_armsup_1 = (cobrimento + diametro_trans + d_sup_min/2, h - (cobrimento+diametro_trans))
            p_armsup_2 = (bw - (cobrimento + diametro_trans + d_sup_min/2), h-(cobrimento + diametro_trans))
            msp.add_circle(p_armsup_1, d_sup_min/2, dxfattribs={'layer': 'Armadura'})
            msp.add_circle(p_armsup_2, d_sup_min/2, dxfattribs={'layer': 'Armadura'})

            pex = cobrimento + diametro_trans
            pey = cobrimento + diametro_trans - diametro_long/2
            pey2 = cobrimento + diametro_trans - d_sup_min/2
            p_estribo_1 = (pex, pey)
            p_estribo_2 = (bw-pex, pey)
            p_estribo_3 = (bw-pex, h-pey2)
            p_estribo_4 = (pex, h-pey2)
            poly_02 = [p_estribo_1, p_estribo_2, p_estribo_3, p_estribo_4, p_estribo_1]
            msp.add_lwpolyline(poly_02, dxfattribs={'layer': 'Armadura'})

            txt_arm = 'Ø' + str(diametro_long * 1000)
            pos_txt_arm_t = (bw / 2, 0.25 * h)
            msp.add_text(txt_arm,
                         dxfattribs={'layer': 'Cotas', 'style': 'descricao_armadura', 'height': 0.025}).set_pos(
                pos_txt_arm_t, align='MIDDLE')
            dwg.saveas(folder_path+'/viga.dxf')

            QtWidgets.QMessageBox().about(self, "Otimização", "Desenho Finalizado!")

        else:
            dialog = QtWidgets.QFileDialog()
            folder_path = dialog.getExistingDirectory(None, "Select Folder")
            f = open('results.txt', 'r')
            if f.mode == 'r':
                contents = f.read()
            r = contents.split(',')
            print(r)
            bw = float(r[0])
            h = float(r[1])/100
            diametro_long_inf = float(r[4])/1000
            n_long_inf = float(r[6])
            diametro_long_sup = float(r[5])/1000
            n_long_sup = float(r[7])
            diametro_trans = float(r[8])/1000
            cobrimento = float(r[10])/1000
            sh_inf = float(r[11])/1000
            sh_sup = float(r[12])/1000

            dwg = ezdxf.new('R2018')
            msp = dwg.modelspace()
            dwg.layers.new(name='Viga', dxfattribs={'linetype': 'Continuous', 'color': 7})
            dwg.layers.new(name='Armadura', dxfattribs={'linetype': 'Continuous', 'color': 5})
            dwg.layers.new(name='Cotas', dxfattribs={'linetype': 'Continuous', 'color': 2})
            dwg.styles.new(name='descricao_armadura', dxfattribs={'font': 'times.ttf', 'width': 8})

            def coord_points_inf(number_of_points):
                points = []
                for i in range(int(number_of_points)):
                    points.append((cobrimento + diametro_trans + (2 * i + 1) * diametro_long_inf / 2 + i * sh_inf,
                                   cobrimento + diametro_trans))
                return points

            def coord_points_sup(number_of_points):
                points = []
                for i in range(int(number_of_points)):
                    points.append((cobrimento + diametro_trans + (2 * i + 1) * diametro_long_sup / 2 + i * sh_sup,
                                   h - (cobrimento + diametro_trans)))
                return points

            # ALTERAR PARA N BARRAS
            p_viga_1 = (0, 0)
            p_viga_2 = (bw, 0)
            p_viga_3 = (bw, h)
            p_viga_4 = (0, h)
            poly_01 = [p_viga_1, p_viga_2, p_viga_3, p_viga_4, p_viga_1]
            msp.add_lwpolyline(poly_01, dxfattribs={'layer': 'Viga'})

            raio_inf = diametro_long_inf / 2
            raio_sup = diametro_long_sup/2
            for j in range(int(n_long_inf)):
                msp.add_circle(coord_points_inf(n_long_inf)[j], raio_inf, dxfattribs={'layer': 'Armadura'})
            for j in range(int(n_long_sup)):
                msp.add_circle(coord_points_sup(n_long_sup)[j], raio_sup, dxfattribs={'layer': 'Armadura'})

            pex = cobrimento + diametro_trans
            pey = cobrimento + diametro_trans - diametro_long_inf/2
            pey2 = cobrimento + diametro_trans - diametro_long_sup/2
            p_estribo_1 = (pex, pey)
            p_estribo_2 = (bw-pex, pey)
            p_estribo_3 = (bw-pex, h-pey2)
            p_estribo_4 = (pex, h-pey2)
            poly_02 = [p_estribo_1, p_estribo_2, p_estribo_3, p_estribo_4, p_estribo_1]
            msp.add_lwpolyline(poly_02, dxfattribs={'layer': 'Armadura'})

            txt_arm = 'Ø' + str(diametro_long_inf * 1000)
            pos_txt_arm_t_inf = (bw / 2, 0.25 * h)
            msp.add_text(txt_arm,
                         dxfattribs={'layer': 'Cotas', 'style': 'descricao_armadura', 'height': 0.025}).set_pos(
                pos_txt_arm_t_inf, align='MIDDLE')

            txt_arm = 'Ø' + str(diametro_long_sup * 1000)
            pos_txt_arm_t_sup = (bw / 2, 0.75 * h)
            msp.add_text(txt_arm,
                         dxfattribs={'layer': 'Cotas', 'style': 'descricao_armadura', 'height': 0.025}).set_pos(
                pos_txt_arm_t_sup, align='MIDDLE')

            dwg.saveas(folder_path+'/viga.dxf')

            QtWidgets.QMessageBox().about(self, "Otimização", "Desenho Finalizado!")


class Dialog(QDialog):
    NumGridRows = 6
    NumButtons = 4

    def __init__(self):
        super(Dialog, self).__init__()
        self.createFormGroupBox()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)
        self.setWindowIcon(QIcon('engineer.png'))
        self.setWindowTitle("AutoDesign")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Dados do Projeto")
        layout = QFormLayout()
        fck_le = QLineEdit()
        fyk_le = QLineEdit()
        q_le = QLineEdit()
        L_le = QLineEdit()
        h_le = QLineEdit()
        layout.addRow(QLabel("Fck(MPa):"), fck_le)
        layout.addRow(QLabel("Fyk(MPa):"), fyk_le)
        layout.addRow(QLabel("Carga Distribuída(kN/m):"), q_le)
        layout.addRow(QLabel("L(m):"), L_le)
        layout.addRow(QLabel("h(cm):"), h_le)

        self.formGroupBox.setLayout(layout)

        def print_data():
            variables = [fck_le, fyk_le, q_le, L_le, h_le]
            c = 0
            for variable in variables:
                if len(variable.text()) >= 1:
                    c += 1
            if c != 5:
                warning = QtWidgets.QMessageBox()
                warning.setWindowTitle('AutoDesign')
                warning.setText('Digite todos os parâmetros!')
                warning.setWindowIcon(QIcon('engineer.png'))
                warning.exec_()
            else:
                f = open("project_data.txt", "w+")
                for variable in variables:
                    f.write(variable.text() + ",")
                f.close()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close)
        buttonBox.clicked.connect(print_data)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)


class Dialog2(QDialog):
    def __init__(self):
        super(Dialog2, self).__init__()

        grid = QGridLayout()
        grid.addWidget(self.createExampleGroup(), 0, 0)
        self.setLayout(grid)

        self.setWindowTitle("AutoDesign")
        self.setWindowIcon(QIcon('engineer.png'))
        self.resize(400, 200)

    def createExampleGroup(self):
        groupBox = QGroupBox("CAA")

        radio1 = QtWidgets.QRadioButton("Classe I - Fraca")
        radio2 = QtWidgets.QRadioButton("Classe II - Moderada")
        radio3 = QtWidgets.QRadioButton("Classe III - Forte")
        radio4 = QtWidgets.QRadioButton("Classe IV - Muito Forte")

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        vbox.addWidget(radio4)
        vbox.addStretch(1)

        def checked():
            if radio1.isChecked() == True:
                caa = 1
            elif radio2.isChecked() == True:
                caa = 2
            elif radio3.isChecked() == True:
                caa = 3
            else:
                caa = 4

            f = open("caa.txt", "w+")
            f.write(str(caa))
            f.close()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.clicked.connect(checked)
        buttonBox.accepted.connect(self.accept)
        vbox.addWidget(buttonBox)
        groupBox.setLayout(vbox)

        return groupBox


class Dialog3(QDialog):
    def __init__(self):
        super(Dialog3, self).__init__()

        grid = QGridLayout()
        grid.addWidget(self.createExampleGroup(), 0, 0)
        self.setLayout(grid)

        self.setWindowTitle("AutoDesign")
        self.setWindowIcon(QIcon('engineer.png'))
        self.resize(240, 120)

    def createExampleGroup(self):
        groupBox = QGroupBox("Tipo de Armadura")

        radio1 = QtWidgets.QRadioButton("Simples")
        radio2 = QtWidgets.QRadioButton("Dupla")

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addStretch(1)

        def checked():
            if radio1.isChecked() == True:
                tipo = "Simples"
            else:
                tipo = "Dupla"

            f = open("tipo.txt", "w+")
            f.write(str(tipo))
            f.close()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.clicked.connect(checked)
        buttonBox.accepted.connect(self.accept)
        vbox.addWidget(buttonBox)
        groupBox.setLayout(vbox)

        return groupBox


class Dialog4(QDialog):
    def __init__(self):
        super(Dialog4, self).__init__()

        grid = QGridLayout()
        grid.addWidget(self.createExampleGroup1(), 0, 0)
        grid.addWidget(self.createExampleGroup2(), 0, 1)
        self.setLayout(grid)

        self.setWindowTitle("AutoDesign")
        self.setWindowIcon(QIcon('engineer.png'))
        self.resize(400, 200)

    def createExampleGroup1(self):
        groupBox = QGroupBox("1° apoio")

        radio1 = QtWidgets.QRadioButton("Apoio de 1° gênero")
        radio2 = QtWidgets.QRadioButton("Apoio de 2° gênero")
        # radio3 = QtWidgets.QRadioButton("Apoio engastado")

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        # vbox.addWidget(radio3)
        vbox.addStretch(1)


        def checked():
            if radio1.isChecked() == True:
                apoio = "1genero"
            elif radio2.isChecked() == True:
                apoio = "2genero"
            else:
                apoio = "engastado"

            f = open("apoio1.txt", "w+")
            f.write(apoio)
            f.close()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.clicked.connect(checked)
        vbox.addWidget(buttonBox)

        groupBox.setLayout(vbox)

        return groupBox

    def createExampleGroup2(self):
        groupBox = QGroupBox("2° apoio")

        radio1 = QtWidgets.QRadioButton("Apoio de 1° gênero")
        radio2 = QtWidgets.QRadioButton("Apoio de 2° gênero")
        # radio3 = QtWidgets.QRadioButton("Apoio engastado")

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        # vbox.addWidget(radio3)
        vbox.addStretch(1)

        def checked():
            if radio1.isChecked() == True:
                apoio = "1genero"
            elif radio2.isChecked() == True:
                apoio = "2genero"
            else:
                apoio = "engastado"

            f = open("apoio2.txt", "w+")
            f.write(apoio)
            f.close()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.clicked.connect(checked)
        buttonBox.accepted.connect(self.accept)
        vbox.addWidget(buttonBox)

        groupBox.setLayout(vbox)

        return groupBox


class Dialog5(QDialog):
    NumGridRows = 6
    NumButtons = 4

    def __init__(self):
        super(Dialog5, self).__init__()
        self.createFormGroupBox()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)
        self.setWindowIcon(QIcon('engineer.png'))
        self.setWindowTitle("AutoDesign")

        self.update_labels()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(1000)

    def update_labels(self):
        f = open('results.txt', 'r')
        if f.mode == 'r':
            contents = f.read()
        r = contents.split(',')

        bw = int(float(r[0])*100)
        h = float(r[1])
        diametro_long = float(r[5])
        n_long = float(r[6])
        area_long = round(math.pi*((diametro_long/10)**2)*n_long/4, 2)
        diametro_trans = float(r[7])
        n_trans = float(r[8])
        area_trans = round(math.pi * ((diametro_trans/10) ** 2) * n_trans / 4, 2)
        vsk = float(r[11])
        mk = float(r[12])

        self.bw_.setText(str(bw))

        self.h_.setText(str(h))

        self.diametro_long_.setText(str(diametro_long))

        self.n_long_.setText(str(n_long))

        self.area_long_.setText(str(area_long))

        self.diametro_trans_.setText(str(diametro_trans))

        self.n_trans_.setText(str(n_trans))

        self.area_trans_.setText(str(area_trans))

        self.vsk_.setText('{} kN ; {} tf'.format(str(vsk), str(vsk * 0.10)))

        self.mk_.setText('{} kNm ; {} tfm'.format(str(mk), str(mk * 0.10)))


    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Relatório")

        f = open('results.txt', 'r')
        if f.mode == 'r':
            contents = f.read()
        r = contents.split(',')

        bw = int(float(r[0])*100)
        h = int(float(r[1]))
        diametro_long = float(r[5])
        n_long = float(r[6])
        area_long = round(math.pi*((diametro_long/10)**2)*n_long/4, 2)
        diametro_trans = float(r[7])
        n_trans = float(r[8])
        area_trans = round(math.pi * ((diametro_trans/10) ** 2) * n_trans / 4, 2)
        vsk = float(r[11])
        mk = float(r[12])

        layout = QFormLayout()

        self.vsk_ = QLabel()
        self.vsk_.setText('{} kN ; {} tf'.format(str(vsk), str(vsk*0.10)))

        self.mk_ = QLabel()
        self.mk_.setText('{} kNm ; {} tfm'.format(str(mk), str(mk*0.10)))

        self.bw_ = QLabel()
        self.bw_.setText(str(bw))

        self.h_ = QLabel()
        self.h_.setText(str(h))

        self.diametro_long_ = QLabel()
        self.diametro_long_.setText(str(diametro_long))

        self.n_long_ = QLabel()
        self.n_long_.setText(str(n_long))

        self.area_long_ = QLabel()
        self.area_long_.setText(str(area_long))

        self.diametro_trans_ = QLabel()
        self.diametro_trans_.setText(str(diametro_trans))

        self.n_trans_ = QLabel()
        self.n_trans_.setText(str(n_trans))

        self.area_trans_ = QLabel()
        self.area_trans_.setText(str(area_trans))

        layout.addRow(QLabel("Vsk:"), self.vsk_)
        layout.addRow(QLabel("Mk:"), self.mk_)

        layout.addRow(QLabel("Largura da Viga (cm):"), self.bw_)
        layout.addRow(QLabel("Altura da Viga (cm):"), self.h_)

        layout.addRow(QLabel("Diâmetro Longitudinal (mm):"), self.diametro_long_)
        layout.addRow(QLabel("Número de Barras Longitudinais (mm):"), self.n_long_)
        layout.addRow(QLabel("Área de aço Longitudinal (cm2):"), self.area_long_)

        layout.addRow(QLabel("Diâmetro Transversal (mm):"), self.diametro_trans_)
        layout.addRow(QLabel("Número de Barras Transversais (mm):"), self.n_trans_)
        layout.addRow(QLabel("Área de aço Transversal (cm2):"), self.area_trans_)

        self.formGroupBox.setLayout(layout)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close)
        buttonBox.clicked.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)


class Dialog6(QDialog):
    NumGridRows = 6
    NumButtons = 4

    def __init__(self):
        super(Dialog6, self).__init__()
        self.createFormGroupBox()

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)
        self.setWindowIcon(QIcon('engineer.png'))
        self.setWindowTitle("AutoDesign")

        self.update_labels()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(1000)

    def update_labels(self):
        f = open('results.txt', 'r')
        if f.mode == 'r':
            contents = f.read()
        r = contents.split(',')

        bw = int(float(r[0])*100)
        h = float(r[1])
        diametro_long_inf = float(r[4])
        diametro_long_sup = float(r[5])
        n_long_inf = float(r[6])
        n_long_sup = float(r[7])
        area_long_inf = round(math.pi*((diametro_long_inf/10)**2)*n_long_inf/4, 2)
        area_long_sup = round(math.pi * ((diametro_long_sup / 10) ** 2) * n_long_sup / 4, 2)
        diametro_trans = float(r[8])
        n_trans = float(r[9])
        area_trans = round(math.pi * ((diametro_trans/10) ** 2) * n_trans / 4, 2)
        vsk = float(r[13])
        mk = float(r[14])


        self.bw_.setText(str(bw))

        self.h_.setText(str(h))

        self.diametro_long_inf_.setText(str(diametro_long_inf))

        self.n_long_inf_.setText(str(n_long_inf))

        self.area_long_inf_.setText(str(area_long_inf))

        self.diametro_long_sup_.setText(str(diametro_long_sup))

        self.n_long_sup_.setText(str(n_long_sup))

        self.area_long_sup_.setText(str(area_long_sup))

        self.diametro_trans_.setText(str(diametro_trans))

        self.n_trans_.setText(str(n_trans))

        self.area_trans_.setText(str(area_trans))

        self.vsk_.setText('{} kN ; {} tf'.format(str(vsk), str(vsk * 0.10)))

        self.mk_.setText('{} kNm ; {} tfm'.format(str(mk), str(mk * 0.10)))


    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Relatório")

        f = open('results.txt', 'r')
        if f.mode == 'r':
            contents = f.read()
        r = contents.split(',')

        bw = int(float(r[0])*100)
        h = int(float(r[1]))
        diametro_long_inf = float(r[4])
        diametro_long_sup = float(r[5])
        n_long_inf = float(r[6])
        n_long_sup = float(r[7])
        area_long_inf = round(math.pi * ((diametro_long_inf/10) ** 2) * n_long_inf / 4, 2)
        area_long_sup = round(math.pi * ((diametro_long_sup / 10) ** 2) * n_long_sup / 4, 2)
        diametro_trans = float(r[8])
        n_trans = float(r[9])
        area_trans = round(math.pi * ((diametro_trans/10) ** 2) * n_trans / 4, 2)
        vsk = float(r[13])
        mk = float(r[14])

        layout = QFormLayout()

        self.bw_ = QLabel()
        self.bw_.setText(str(bw))

        self.h_ = QLabel()
        self.h_.setText(str(h))

        self.diametro_long_inf_ = QLabel()
        self.diametro_long_inf_.setText(str(diametro_long_inf))

        self.n_long_inf_ = QLabel()
        self.n_long_inf_.setText(str(n_long_inf))

        self.area_long_inf_ = QLabel()
        self.area_long_inf_.setText(str(area_long_inf))

        self.diametro_long_sup_ = QLabel()
        self.diametro_long_sup_.setText(str(diametro_long_sup))

        self.n_long_sup_ = QLabel()
        self.n_long_sup_.setText(str(n_long_sup))

        self.area_long_sup_ = QLabel()
        self.area_long_sup_.setText(str(area_long_sup))

        self.diametro_trans_ = QLabel()
        self.diametro_trans_.setText(str(diametro_trans))

        self.n_trans_ = QLabel()
        self.n_trans_.setText(str(n_trans))

        self.area_trans_ = QLabel()
        self.area_trans_.setText(str(area_trans))

        self.vsk_ = QLabel()
        self.vsk_.setText('{} kN ; {} tf'.format(str(vsk), str(vsk * 0.10)))

        self.mk_ = QLabel()
        self.mk_.setText('{} kNm ; {} tfm'.format(str(mk), str(mk * 0.10)))

        layout.addRow(QLabel("Vsk:"), self.vsk_)
        layout.addRow(QLabel("Mk:"), self.mk_)

        layout.addRow(QLabel("Largura da Viga (cm):"), self.bw_)
        layout.addRow(QLabel("Altura da Viga (cm):"), self.h_)

        layout.addRow(QLabel("Diâmetro Longitudinal Inferior (mm):"), self.diametro_long_inf_)
        layout.addRow(QLabel("Número de Barras Longitudinais Inferiores (mm):"), self.n_long_inf_)
        layout.addRow(QLabel("Área de aço Longitudinal Inferior (cm2):"), self.area_long_inf_)

        layout.addRow(QLabel("Diâmetro Longitudinal Superior (mm):"), self.diametro_long_sup_)
        layout.addRow(QLabel("Número de Barras Longitudinais Superior (mm):"), self.n_long_sup_)
        layout.addRow(QLabel("Área de aço Longitudinal Superior (cm2):"), self.area_long_sup_)

        layout.addRow(QLabel("Diâmetro Transversal (mm):"), self.diametro_trans_)
        layout.addRow(QLabel("Número de Barras Transversais (mm):"), self.n_trans_)
        layout.addRow(QLabel("Área de aço Transversal (cm2):"), self.area_trans_)

        self.formGroupBox.setLayout(layout)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close)
        buttonBox.clicked.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.suptitle("Diagrama: Esforço Cortante e Momento Fletor")
        self.axes1 = fig.add_subplot(211)
        self.axes2 = fig.add_subplot(212)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class Chart(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.setWindowTitle("AutoDesign")
        self.setWindowIcon(QIcon('engineer.png'))
        self.resize(800, 600)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        project_data = pd.read_csv('project_data.txt')
        q = float(project_data.columns[2])
        L = float(project_data.columns[3])
        apoio1 = pd.read_csv('apoio1.txt').columns[0]
        apoio2 = pd.read_csv('apoio2.txt').columns[0]

        x = biapoiada(q, L)[0]
        y_Q = biapoiada(q, L)[1]
        y_M = biapoiada(q, L)[2]

        tri1_x = [0, -0.1, 0.1, 0]
        tri1_y = [0, -5, -5, 0]
        tri2_x = [L, L - 0.1, L + 0.1, L]
        tri2_y = [0, -5, -5, 0]

        self.axes1.plot(x, y_Q, color='navy')
        self.axes1.vlines(x=0, ymin=0, ymax=q * L / 2, color='navy')
        self.axes1.vlines(x=L, ymin=-q * L / 2, ymax=0, color='navy')
        self.axes1.hlines(y=0, xmin=0, xmax=L, color='black')
        self.axes1.hlines(y=-5, xmin=-0.15, xmax=0.15, color='black')
        self.axes1.hlines(y=-5.5, xmin=L - 0.15, xmax=L + 0.15, color='black')
        self.axes1.plot(tri1_x, tri1_y, color='black')
        self.axes1.plot(tri2_x, tri2_y, color='black')

        tri3_x = [0, -0.1, 0.1, 0]
        tri3_y = [0, 5, 5, 0]
        tri4_x = [L, L - 0.1, L + 0.1, L]
        tri4_y = [0, 5, 5, 0]

        self.axes2.plot(x, y_M, color='navy')
        self.axes2.hlines(y=0, xmin=0, xmax=L, color='black')
        self.axes2.hlines(y=5, xmin=-0.15, xmax=0.15, color='black')
        self.axes2.hlines(y=5.5, xmin=L - 0.15, xmax=L + 0.15, color='black')
        self.axes2.plot(tri3_x, tri3_y, color='black')
        self.axes2.plot(tri4_x, tri4_y, color='black')
        self.axes2.set_ylim(self.axes2.get_ylim()[::-1])

    def update_figure(self):
        project_data = pd.read_csv('project_data.txt')
        q = float(project_data.columns[2])
        L = float(project_data.columns[3])
        apoio1 = pd.read_csv('apoio1.txt').columns[0]
        apoio2 = pd.read_csv('apoio2.txt').columns[0]

        x = biapoiada(q, L)[0]
        y_Q = biapoiada(q, L)[1]
        y_M = biapoiada(q, L)[2]

        tri1_x = [0, -0.1, 0.1, 0]
        tri1_y = [0, -5, -5, 0]
        tri2_x = [L, L - 0.1, L + 0.1, L]
        tri2_y = [0, -5, -5, 0]

        self.axes1.cla()
        self.axes1.plot(x, y_Q, color='navy')
        self.axes1.vlines(x=0, ymin=0, ymax=q * L / 2, color='navy')
        self.axes1.vlines(x=L, ymin=-q * L / 2, ymax=0, color='navy')
        self.axes1.hlines(y=0, xmin=0, xmax=L, color='black')
        self.axes1.hlines(y=-5, xmin=-0.15, xmax=0.15, color='black')
        self.axes1.hlines(y=-5.5, xmin=L - 0.15, xmax=L + 0.15, color='black')
        self.axes1.plot(tri1_x, tri1_y, color='black')
        self.axes1.plot(tri2_x, tri2_y, color='black')

        tri3_x = [0, -0.1, 0.1, 0]
        tri3_y = [0, 5, 5, 0]
        tri4_x = [L, L - 0.1, L + 0.1, L]
        tri4_y = [0, 5, 5, 0]

        self.axes2.cla()
        self.axes2.plot(x, y_M, color='navy')
        self.axes2.hlines(y=0, xmin=0, xmax=L, color='black')
        self.axes2.hlines(y=5, xmin=-0.15, xmax=0.15, color='black')
        self.axes2.hlines(y=5.5, xmin=L - 0.15, xmax=L + 0.15, color='black')
        self.axes2.plot(tri3_x, tri3_y, color='black')
        self.axes2.plot(tri4_x, tri4_y, color='black')
        self.axes2.set_ylim(self.axes2.get_ylim()[::-1])

        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
