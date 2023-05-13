from PyQt5 import uic, QtWidgets
import psycopg2


#Leitura do arquivo
f = open("C:/WorkTimeFull/DBConfig/config.txt")

# Configurações do banco
conexao = psycopg2.connect(f"{f.read()}")

#Cursor
cursor = conexao.cursor()


def mostraOpcoes():
    options.show()

def fechaOpcoes():
    options.close()

def telaCadastroOpcoes():
    resposta = 0
    if options.radioButtonPeople.isChecked():
        resposta = 1
    elif options.radioButtonSector.isChecked():
        resposta = 2

    if (resposta == 1):
        cursor.execute("SELECT * FROM setor limit 1")
        repostaSQL = cursor.fetchall()

        if (repostaSQL):
            peopleForm.show()
            options.close()
        else:
            QtWidgets.QMessageBox.about(options, 'Alerta', 'Você precisa cadastrar um setor primeiro!')

    elif (resposta == 2):
        sectorForm.show()
        options.close()
    else:
        QtWidgets.QMessageBox.about(options, 'Alerta', 'Você precisa selecionar uma opção, é obrigatório')


def setorRegistra():
    setorNome = sectorForm.inputName.text().upper()
    setorLider = sectorForm.inputLeader.text().upper()

    if (setorNome):
        comandoSQL = "INSERT INTO setor (nome, lider, empresa) values (%s,%s,(select id from empresa limit 1))"
        dados = (str(setorNome), str(setorLider))

        cursor.execute(comandoSQL, dados)
        conexao.commit()
        QtWidgets.QMessageBox.about(options, 'Aviso', 'Setor Cadastrado!')
        sectorForm.close()
        sectorForm.inputName.clear()
        sectorForm.inputLeader.clear()
    else:
        QtWidgets.QMessageBox.about(options, 'Erro', 'Você precisa preencher todos os campos obrigatórios!')


def pessoaRegistra():
    pessoaNome = peopleForm.inputName.text().upper()
    pessoaSobrenome = peopleForm.inputLastname.text().upper()
    pessoaUsuario = peopleForm.inputUser.text().upper()
    pessoaSetor = peopleForm.inputSectorId.text()

    cursor.execute(f"select id from pessoa where usuario='{pessoaUsuario}'")
    usuarioSQL = cursor.fetchone()
    cursor.execute(f"select 1 from setor where id='{pessoaSetor}'")
    setorSQL = cursor.fetchone()

    if(usuarioSQL):
        QtWidgets.QMessageBox.about(options, 'Aviso', 'Este usuario já existe!')

    elif(setorSQL == None):
        QtWidgets.QMessageBox.about(options, 'Aviso', 'Este setor não existe!')

    elif(pessoaNome and pessoaSobrenome and pessoaUsuario and pessoaSetor):
        comandoSQL = "INSERT INTO pessoa (nome, sobrenome, usuario, setor) values (%s, %s, %s, %s)"
        dados = (str(pessoaNome), str(pessoaSobrenome), str(pessoaUsuario), str(int(pessoaSetor)))
        cursor.execute(comandoSQL, dados)
        conexao.commit()
        cursor.execute("INSERT INTO usuario (pessoa, setor) SELECT id, setor FROM pessoa ORDER BY id DESC limit 1;")
        cursor.execute("UPDATE usuario SET horas_ativo = '00:00:00' , horas_inativo = '00:00:00' where horas_ativo is null;")
        conexao.commit()
        QtWidgets.QMessageBox.about(options, 'Aviso', 'Pessoa Cadastrada!')
        peopleForm.close()
        peopleForm.inputName.clear()
        peopleForm.inputLastname.clear()
        peopleForm.inputUser.clear()
        peopleForm.inputSectorId.clear()
        peopleForm.inputSectorName.clear()

    else:
        QtWidgets.QMessageBox.about(options, 'Erro', 'Você precisa preencher todos os campos obrigatórios!')


def fechaCadastroPessoa():
    peopleForm.close()
    peopleForm.inputName.clear()
    peopleForm.inputLastname.clear()
    peopleForm.inputUser.clear()
    peopleForm.inputSectorId.clear()
    peopleForm.inputSectorName.clear()

def fechaCadastroSetor():
    sectorForm.close()
    sectorForm.inputName.clear()
    sectorForm.inputLeader.clear()

def buscaRelatorio():
    dataInicio = home.inputFirstDate.text()
    dataFim = home.inputLastDate.text()
    setor = home.inputSectorId.text()
    pessoa = home.inputPeopleId.text()
    comandoSQL = ""

    if(setor):
        if(pessoa):
            comandoSQL = f"""SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                                    FROM usuario u 
                                    JOIN pessoa p ON (u.pessoa=p.id) 
                                    JOIN setor s ON (u.setor=s.id)
                                    WHERE u.dia between '{dataInicio}' and '{dataFim}'
                                    AND p.id={pessoa}
                                    AND s.id={setor};"""

        else:
            comandoSQL = f"""SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                                    FROM usuario u 
                                    JOIN pessoa p ON (u.pessoa=p.id) 
                                    JOIN setor s ON (u.setor=s.id)
                                    WHERE u.dia between '{dataInicio}' and '{dataFim}'
                                    AND s.id={setor};"""

    elif(pessoa):
        comandoSQL = f"""SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                                        FROM usuario u 
                                        JOIN pessoa p ON (u.pessoa=p.id) 
                                        JOIN setor s ON (u.setor=s.id)
                                        WHERE u.dia between '{dataInicio}' and '{dataFim}'
                                        AND p.id={pessoa};"""

    elif(dataInicio and dataFim):
        comandoSQL = f"""SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                                                FROM usuario u 
                                                JOIN pessoa p ON (u.pessoa=p.id) 
                                                JOIN setor s ON (u.setor=s.id)
                                                WHERE u.dia between '{dataInicio}' and '{dataFim}';"""

    else:
        QtWidgets.QMessageBox.about(options, 'Erro', 'Você deve informar pelo menos uma data!')

    report.show()
    cursor.execute(comandoSQL)
    resultado = cursor.fetchall()


    report.tableWidget.setRowCount(len(resultado))
    report.tableWidget.setColumnCount(5)

    for i in range(0, len(resultado)):
        for j in range(0, 5):
            report.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(resultado[i][j])))

def exportaRelatorio():
    dataInicio = home.inputFirstDate.text()
    dataFim = home.inputLastDate.text()
    setor = home.inputSectorId.text()
    pessoa = home.inputPeopleId.text()
    a = QtWidgets.QFileDialog.getSaveFileName()[0]

    if (setor):
        if (pessoa):
            t = f"""    SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                                FROM usuario u 
                                JOIN pessoa p ON (u.pessoa=p.id) 
                                JOIN setor s ON (u.setor=s.id)
                                WHERE u.dia between '{dataInicio}' and '{dataFim}'
                                AND p.id={pessoa}
                                AND s.id={setor}"""

        else:
            t = f"""    SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                                FROM usuario u 
                                JOIN pessoa p ON (u.pessoa=p.id) 
                                JOIN setor s ON (u.setor=s.id)
                                WHERE u.dia between '{dataInicio}' and '{dataFim}'
                                AND s.id={setor}"""

    elif(pessoa):
        t = f"""    SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                            FROM usuario u 
                            JOIN pessoa p ON (u.pessoa=p.id) 
                            JOIN setor s ON (u.setor=s.id)
                            WHERE u.dia between '{dataInicio}' and '{dataFim}'
                            AND p.id={pessoa}"""

    else:
        t = f"""    SELECT p.nome AS pessoa, s.nome AS setor, u.dia, u.horas_ativo, u.horas_inativo 
                            FROM usuario u 
                            JOIN pessoa p ON (u.pessoa=p.id) 
                            JOIN setor s ON (u.setor=s.id)
                            WHERE u.dia between '{dataInicio}' and '{dataFim}'"""

    sql =f"""   copy ({t}) to stdout delimiter as ';' csv header    """

    with open(a + '.csv', "w") as rel:
        cursor.copy_expert(sql, rel)
    QtWidgets.QMessageBox.about(options, 'Aviso', 'Relatório Exportado!')

def fechaRelatorio():
    report.close()

def buscaSetor():
    sectorSelect.show()
    cursor = conexao.cursor()
    comandoSQL = "SELECT nome FROM setor"
    cursor.execute(comandoSQL)
    resultado = cursor.fetchall()
    sectorSelect.tableWidget.setRowCount(len(resultado))
    sectorSelect.tableWidget.setColumnCount(1)

    for i in range(0, len(resultado)):
        for j in range(0, 1):
            sectorSelect.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(resultado[i][j])))

def buscaSetor2():
    sectorSelect2.show()
    cursor = conexao.cursor()
    comandoSQL = "SELECT nome FROM setor"
    cursor.execute(comandoSQL)
    resultado = cursor.fetchall()
    sectorSelect2.tableWidget.setRowCount(len(resultado))
    sectorSelect2.tableWidget.setColumnCount(1)

    for i in range(0, len(resultado)):
        for j in range(0, 1):
            sectorSelect2.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(resultado[i][j])))

def buscaPessoa():
    peopleSelect.show()
    cursor = conexao.cursor()
    comandoSQL = "SELECT nome, usuario FROM pessoa"
    cursor.execute(comandoSQL)
    resultado = cursor.fetchall()
    peopleSelect.tableWidget.setRowCount(len(resultado))
    peopleSelect.tableWidget.setColumnCount(2)

    for i in range(0, len(resultado)):
        for j in range(0, 2):
            peopleSelect.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(resultado[i][j])))

def insereSetorId():
    setor = sectorSelect.tableWidget.currentRow()
    home.inputSectorId.setText(str(int(setor + 1)))
    sectorSelect.close()

def insereSetorNome():
    setor = sectorSelect.tableWidget.currentRow()
    comandoSQL = f"select nome from setor where id= {setor + 1}"
    cursor.execute(comandoSQL)
    resultadoSQL = cursor.fetchone()
    home.inputSectorName.setText(str(resultadoSQL))
    sectorSelect.close()

def insereSetorId2():
    setor2 = sectorSelect2.tableWidget.currentRow()
    peopleForm.inputSectorId.setText(str(int(setor2 + 1)))
    sectorSelect2.close()

def insereSetorNome2():
    setor2 = sectorSelect2.tableWidget.currentRow()
    comandoSQL = f"select nome from setor where id= {setor2 + 1}"
    cursor.execute(comandoSQL)
    resultadoSQL = cursor.fetchone()
    peopleForm.inputSectorName.setText(str(resultadoSQL))
    sectorSelect2.close()

def inserePessoaId():
    pessoa = peopleSelect.tableWidget.currentRow()
    home.inputPeopleId.setText(str(int(pessoa + 1)))
    peopleSelect.close()

def inserePessoaNome():
    pessoa = peopleSelect.tableWidget.currentRow()
    comandoSQL = f"SELECT nome from PESSOA where id= {pessoa + 1}"
    cursor.execute(comandoSQL)
    resultadoSQL = cursor.fetchone()
    home.inputPeopleName.setText(str(resultadoSQL))
    peopleSelect.close()

def fechaBuscaSetor():
    sectorSelect.close()

def fechaBuscaSetor2():
    sectorSelect2.close()

def fechaBuscaPessoa():
    peopleSelect.close()

# Fim
def fechaPrograma():
    home.close()
    options.close()
    peopleForm.close()
    sectorForm.close()
    report.close()
    peopleSelect.close()
    sectorSelect.close()
    sectorSelect2.close()
    cursor.close()
    conexao.close()

# Leitura das telas
App = QtWidgets.QApplication([])
home = uic.loadUi("template\ScreenHome.ui")
options = uic.loadUi("template\ScreenOption.ui")
peopleForm = uic.loadUi("template\ScreenPeopleRegistration.ui")
sectorForm = uic.loadUi("template\ScreenSectorRegistration.ui")
report = uic.loadUi("template\ScreenReport.ui")
peopleSelect = uic.loadUi("template\ScreenPeopleSelect.ui")
sectorSelect = uic.loadUi("template\ScreenSectorSelect.ui")
sectorSelect2 = uic.loadUi("template\ScreenSectorSelect2.ui")

# Botões
# Tela principal
home.buttonRegister.clicked.connect(mostraOpcoes)
home.buttonView.clicked.connect(buscaRelatorio)
home.buttonCloseApp.clicked.connect(fechaPrograma)
home.buttonSectorSelect.clicked.connect(buscaSetor)
sectorSelect.buttonSectorSelect.clicked.connect(insereSetorId)
sectorSelect.buttonSectorSelect.clicked.connect(insereSetorNome)
sectorSelect.buttonClose.clicked.connect(fechaBuscaSetor)
home.buttonPeopleSelect.clicked.connect(buscaPessoa)
peopleSelect.buttonPeopleSelect.clicked.connect(inserePessoaId)
peopleSelect.buttonPeopleSelect.clicked.connect(inserePessoaNome)
peopleSelect.buttonClose.clicked.connect(fechaBuscaPessoa)

# Tela de opções
options.buttonClose.clicked.connect(fechaOpcoes)
options.buttonConfirm.clicked.connect(telaCadastroOpcoes)

# Tela de cadastro de pessoas
peopleForm.buttonClose.clicked.connect(fechaCadastroPessoa)
peopleForm.buttonConfirm.clicked.connect(pessoaRegistra)
peopleForm.buttonSectorSelect.clicked.connect(buscaSetor2)
sectorSelect2.buttonSectorSelect.clicked.connect(insereSetorId2)
sectorSelect2.buttonSectorSelect.clicked.connect(insereSetorNome2)
sectorSelect2.buttonClose.clicked.connect(fechaBuscaSetor2)

# Tela de cadastro de setores
sectorForm.buttonClose.clicked.connect(fechaCadastroSetor)
sectorForm.buttonConfirm.clicked.connect(setorRegistra)

# Tela de exportar arquivos
report.buttonClose.clicked.connect(fechaRelatorio)
report.buttonExport.clicked.connect(exportaRelatorio)

#Controle de inputs (Opicional)
'''peopleForm.inputSectorId.setInputMask("DD")
peopleForm.inputSectorName.setInputMask("AAAAAAAAAAAA")
home.inputSectorId.setInputMask("DD")
home.inputSectorName.setInputMask("AAAAAAAA")
home.inputPeopleId.setInputMask("DD")
home.inputPeopleName.setInputMask("AAAAAAAAAA")
peopleForm.inputName.setInputMask("AAAAAAAAAA")
peopleForm.inputLastname.setInputMask("AAAAAAAAAA")'''


# Inicio
home.show()
App.exec()