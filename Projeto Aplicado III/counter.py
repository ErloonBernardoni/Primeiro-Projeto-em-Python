import time
import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from pynput.mouse import Controller
from PyQt5 import uic, QtWidgets
import psycopg2

#Leitura do arquivo
f = open("C:/WorkTimeFull/DBConfig/config.txt")

#Configurações do banco
conexao = psycopg2.connect(f"{f.read()}")

#Cursor
cursor = conexao.cursor()

#Controlador do Mouse e Teclado
mouse = Controller()

def iniciaApp():
    usuario = counter.inputUser.text().upper()
    cursor.execute(f"SELECT 1 FROM pessoa WHERE usuario='{usuario}'")
    usuarioSQL = cursor.fetchone()

    if(usuarioSQL):
        cursor.execute(f"SELECT dia FROM usuario WHERE pessoa IN (SELECT id FROM pessoa WHERE usuario='{usuario}') ORDER BY dia DESC LIMIT 1;")
        data = cursor.fetchone()
        if(data[0] == None):
            counter.close()
            cursor.execute(f"""UPDATE usuario SET dia=(SELECT CURRENT_DATE) 
                                        WHERE pessoa IN (SELECT id FROM pessoa WHERE usuario='{usuario}');""")

        else:
            counter.close()
            cursor.execute(f"""INSERT INTO usuario (pessoa, setor) 
                                    SELECT pessoa, setor 
                                        FROM usuario 
                                        WHERE pessoa in 
                                            (SELECT id FROM pessoa WHERE usuario='{usuario}') LIMIT 1;""")
            cursor.execute(f"""UPDATE usuario SET dia= (SELECT CURRENT_DATE), horas_ativo= '00:00:00', horas_inativo = '00:00:00'
                                        WHERE dia is null""")

        conexao.commit()
        log(usuario)
    else:
        QtWidgets.QMessageBox.about(counter, 'Aviso', 'Informe um usuario válido!')
        counter.inputUser.clear()

def log(usuario):
    segundos = 0
    while segundos <= 31:

        time.sleep(1)
        segundos += 1


        print(segundos, end=' ')
        print("             Mouse -->", mouse.position)

        # Guarda a posição no primeiro segundo
        if segundos == 1:
            posicao = mouse.position

        # No segundo 30 valida se a posicao do primeiro segundo é diferente da posição do décimo quinto segundo, se for ele ativa e atualiza o horas ativo
        if segundos == 30:
            if posicao != mouse.position:
                cursor.execute(f"""UPDATE usuario SET horas_ativo=(horas_ativo + INTERVAL '30 SECONDS') 
                                        WHERE pessoa IN 
                                        (SELECT id FROM pessoa WHERE usuario='{usuario}') 
                                        AND id = (SELECT MAX(id) FROM usuario);""")
                segundos = 0

            # Se não, ele inativa e atualiza o horas inativo
            else:
                cursor.execute(f"""UPDATE usuario SET horas_inativo=(horas_inativo + INTERVAL '30 SECONDS') 
                                        WHERE pessoa IN 
                                        (SELECT id FROM pessoa WHERE usuario='{usuario}') 
                                        AND id = (SELECT MAX(id) FROM usuario);""")
                segundos = 0
        conexao.commit()

#Leitura da tela
counterApp = QtWidgets.QApplication(sys.argv)
counter = uic.loadUi("template\ScreenCounter.ui")

#Botão
counter.buttonStart.clicked.connect(iniciaApp)
counter.buttonStart.clicked.connect(counter.close)

#Inicio
trayIcone = QSystemTrayIcon(QIcon('icons/amp.png'), parent=counterApp)
trayIcone.setToolTip('Você está trabalhando!')
trayIcone.show()
menu = QMenu()
counter.show()
trayIcone.setContextMenu(menu)
sair = menu.addAction('Bater o Ponto')
sair.triggered.connect(counterApp.quit)
sys.exit(counterApp.exec())
