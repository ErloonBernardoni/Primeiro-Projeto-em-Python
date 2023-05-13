from PyQt5 import uic, QtWidgets
import psycopg2

# Conexão
def tentaConexaoBanco():
    #Configurações do banco
    host = start.inputHost.text()
    user = start.inputUser.text()
    dbname = start.inputBase.text()
    password = start.inputPassword.text()

    try:
        conexao = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
        QtWidgets.QMessageBox.about(start, 'Aviso', 'Conectou!')

    except (Exception, psycopg2.Error) as error:
        QtWidgets.QMessageBox.about(start, 'Erro', 'Sem Conexão!')

def fechaInstalador():
    start.close()

def criaSistema():
    host = start.inputHost.text()
    user = start.inputUser.text()
    dbname = start.inputBase.text()
    password = start.inputPassword.text()
    port = start.inputPort.text()
    empresa = start.inputCompany.text().upper()
    CNPJ = start.inputCNPJ.text()


    if(host and user and dbname and password and empresa and CNPJ and port):
        conexao = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = conexao.cursor()

        #Tabelas do sistema
        cursor.execute("""CREATE TABLE IF NOT EXISTS empresa (
                                id SERIAL PRIMARY KEY NOT NULL, 
                                nome VARCHAR(50), 
                                cnpj VARCHAR(20));""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS setor (
                                id SERIAL PRIMARY KEY  NOT NULL,
                                nome VARCHAR(50) NOT NULL,
                                lider VARCHAR(50),
                                empresa INTEGER, 
                                foreign key (empresa) references empresa (id));""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS pessoa (
                                id SERIAL PRIMARY KEY NOT NULL, 
                                nome VARCHAR(50), 
                                sobrenome VARCHAR(50), 
                                usuario VARCHAR(20), 
                                setor INTEGER,
                                foreign key (setor) references setor (id));""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS usuario (
                                id SERIAL PRIMARY KEY NOT NULL, 
                                pessoa INTEGER, 
                                setor INTEGER, 
                                dia DATE, 
                                horas_ativo TIME, 
                                horas_inativo TIME, 
                                foreign key (pessoa) references pessoa (id), 
                                foreign key (setor) references setor (id));""")


        cursor.execute(f"INSERT INTO empresa (nome,cnpj) values ('{empresa}','{CNPJ}')")
        conexao.commit()

        f = open("C:/WorkTimeFull/DBConfig/config.txt", 'w')
        f.write(f"dbname={dbname} user={user} password={password} host={host} port={port}")

        QtWidgets.QMessageBox.about(start, 'Aviso', 'Instalação Concluida!')

        start.close()

    else:
        QtWidgets.QMessageBox.about(start, 'Erro', 'Falha na comunicação ou campos não preenchidos!')

#Leitura da tela
installer = QtWidgets.QApplication([])
start = uic.loadUi("template\ScreenStart.ui")

#Botões
start.buttonTest.clicked.connect(tentaConexaoBanco)
start.buttonClose.clicked.connect(fechaInstalador)
start.buttonConfirm.clicked.connect(criaSistema)

#Controle de inputs
start.inputCNPJ.setInputMask("99.999.999/9999-99")
start.inputPort.setInputMask('dddddddd')

#Inicio
start.show()
installer.exec()