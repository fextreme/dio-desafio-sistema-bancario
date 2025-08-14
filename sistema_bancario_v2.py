from datetime import datetime

# ==========================
# DADOS DO SISTEMA
# ==========================

usuarios = {}  # CPF -> dados do usuário
contas = []    # Lista de contas bancárias
NUM_AGENCIA = "0001"
num_conta_seq = 1  # Número sequencial das contas

# ==========================
# FUNÇÕES DE USUÁRIO E CONTA
# ==========================

def validar_cpf(cpf: str) -> str:
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    if len(cpf_limpo) != 11:
        return None
    return cpf_limpo

def cadastrar_usuario():
    global usuarios
    print("\n=== Cadastro de Usuário ===")
    nome = input("Nome: ").strip()
    data_nascimento = input("Data de Nascimento (dd/mm/aaaa): ").strip()
    
    while True:
        cpf = input("CPF (somente números ou com pontos/traço): ").strip()
        cpf_valido = validar_cpf(cpf)
        if not cpf_valido:
            print("CPF inválido. Deve conter 11 dígitos.")
        elif cpf_valido in usuarios:
            print("CPF já cadastrado. Informe outro.")
        else:
            break
    
    endereco = input("Endereço (logradouro, nro - bairro - cidade/UF): ").strip()
    
    usuarios[cpf_valido] = {
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf_valido,
        "endereco": endereco
    }
    print(f"Usuário {nome} cadastrado com sucesso!\n")

def listar_cpfs():
    if not usuarios:
        print("Nenhum CPF cadastrado.")
    else:
        print("CPFs cadastrados:")
        for cpf in usuarios:
            print(cpf)

def cadastrar_conta():
    global contas, num_conta_seq
    print("\n=== Cadastro de Conta Bancária ===")
    if not usuarios:
        print("Nenhum usuário cadastrado. Cadastre um usuário antes de criar uma conta.")
        return
    
    listar_cpfs()
    while True:
        cpf = input("Informe o CPF do usuário para vincular a conta: ").strip()
        cpf_valido = validar_cpf(cpf)
        if not cpf_valido or cpf_valido not in usuarios:
            print("CPF não encontrado ou inválido. Tente novamente.")
        else:
            break
    
    conta = {
        "agencia": NUM_AGENCIA,
        "numero_conta": num_conta_seq,
        "usuario_cpf": cpf_valido,
        "saldo": 0.0,
        "extrato": "",
        "numero_saques": 0,
        "limite_saques": 3,
        "limite_valor_saque": 500.0,
        "ultimo_dia_saque": None  # para reset diário
    }
    contas.append(conta)
    print(f"Conta {num_conta_seq} criada para {usuarios[cpf_valido]['nome']} (CPF: {cpf_valido})\n")
    num_conta_seq += 1

def listar_contas():
    if not contas:
        print("Nenhuma conta cadastrada.")
    else:
        print("\n=== Contas Cadastradas ===")
        for c in contas:
            usuario = usuarios[c["usuario_cpf"]]["nome"]
            print(f"Agência: {c['agencia']} | Conta: {c['numero_conta']} | Usuário: {usuario} | CPF: {c['usuario_cpf']}")
        print()

# ==========================
# FUNÇÕES DE OPERAÇÕES
# ==========================

# Depósito: positional-only
def depositar(saldo, valor, extrato, /):
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        print("Depósito realizado com sucesso!")
    else:
        print("Valor inválido. Depósito deve ser positivo.")
    return saldo, extrato

# Saque: keyword-only
def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    hoje = datetime.today().date()
    if numero_saques.get("data") != hoje:
        numero_saques["quantidade"] = 0
        numero_saques["data"] = hoje

    if valor > saldo:
        print("Saldo insuficiente.")
    elif valor > limite:
        print(f"Valor excede limite de R$ {limite:.2f}")
    elif numero_saques["quantidade"] >= limite_saques:
        print("Número máximo de saques atingido.")
    elif valor > 0:
        saldo -= valor
        extrato += f"Saque:    R$ {valor:.2f}\n"
        numero_saques["quantidade"] += 1
        print("Saque realizado com sucesso!")
    else:
        print("Valor inválido. Deve ser positivo.")
    return saldo, extrato

# Extrato: positional-only e keyword-only
def mostrar_extrato(saldo, /, *, extrato):
    print("\n================ EXTRATO ================")
    if not extrato:
        print("Não foram realizadas movimentações.")
    else:
        print(extrato, end="")
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("==========================================")

# ==========================
# AUXILIAR: ESCOLHER CONTA
# ==========================

def escolher_conta():
    if not contas:
        print("Nenhuma conta cadastrada.")
        return None
    listar_contas()
    while True:
        try:
            num = int(input("Informe o número da conta que deseja acessar: ").strip())
            for c in contas:
                if c["numero_conta"] == num:
                    # Preparar controle de saques diário
                    if "numero_saques" not in c or not isinstance(c["numero_saques"], dict):
                        c["numero_saques"] = {"quantidade": 0, "data": None}
                    return c
            print("Conta não encontrada. Tente novamente.")
        except ValueError:
            print("Digite um número válido.")

# ==========================
# MENU PRINCIPAL
# ==========================

menu_principal = """
[1] Cadastrar Usuário
[2] Cadastrar Conta Bancária
[3] Listar Usuários
[4] Listar Contas
[5] Operar Conta (Saque/Depósito/Extrato)
[q] Sair
=> """

while True:
    opcao = input(menu_principal).strip().lower()
    if opcao == "1":
        cadastrar_usuario()
    elif opcao == "2":
        cadastrar_conta()
    elif opcao == "3":
        if not usuarios:
            print("Nenhum usuário cadastrado.")
        else:
            print("\n=== Usuários Cadastrados ===")
            for u in usuarios.values():
                print(f"Nome: {u['nome']} | CPF: {u['cpf']} | Data Nasc.: {u['data_nascimento']} | Endereço: {u['endereco']}")
            print()
    elif opcao == "4":
        listar_contas()
    elif opcao == "5":
        conta = escolher_conta()
        if conta:
            while True:
                menu_conta = """
[d] Depositar
[s] Sacar
[e] Extrato
[q] Voltar ao menu principal
=> """
                opc = input(menu_conta).strip().lower()
                if opc == "d":
                    # depósito: positional-only
                    conta["saldo"], conta["extrato"] = depositar(conta["saldo"], float(input("Informe o valor do depósito: ")), conta["extrato"])
                elif opc == "s":
                    # saque: keyword-only
                    conta["saldo"], conta["extrato"] = sacar(
                        saldo=conta["saldo"],
                        valor=float(input("Informe o valor do saque: ")),
                        extrato=conta["extrato"],
                        limite=conta["limite_valor_saque"],
                        numero_saques=conta["numero_saques"],
                        limite_saques=conta["limite_saques"]
                    )
                elif opc == "e":
                    mostrar_extrato(conta["saldo"], extrato=conta["extrato"])
                elif opc == "q":
                    break
                else:
                    print("Opção inválida.")
    elif opcao == "q":
        print("Saindo do sistema...")
        break
    else:
        print("Opção inválida. Tente novamente.")
