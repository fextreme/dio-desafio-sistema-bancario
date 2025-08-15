from datetime import datetime
from abc import ABC, abstractmethod


# ==========================
# CLASSES DE CLIENTE
# ==========================
class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas = []

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = self.validar_cpf(cpf)

    @staticmethod
    def validar_cpf(cpf: str):
        cpf_limpo = "".join(filter(str.isdigit, cpf))
        if len(cpf_limpo) != 11:
            raise ValueError("CPF inválido")
        return cpf_limpo


# ==========================
# CLASSES DE CONTA
# ==========================
class Conta:
    def __init__(self, numero: int, cliente: Cliente, agencia: str = "0001"):
        self.agencia = agencia
        self.numero = numero
        self.cliente = cliente
        self.saldo = 0.0
        self.historico = Historico()


class ContaCorrente(Conta):
    def __init__(self, numero: int, cliente: Cliente, limite: float = 500.0, limite_saques: int = 3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_hoje = {"quantidade": 0, "data": None}

    def sacar(self, valor: float):
        hoje = datetime.today().date()
        if self.saques_hoje["data"] != hoje:
            self.saques_hoje = {"quantidade": 0, "data": hoje}

        if valor > self.saldo:
            print("Saldo insuficiente.")
            return False
        elif valor > self.limite:
            print(f"Valor excede o limite de R$ {self.limite:.2f}")
            return False
        elif self.saques_hoje["quantidade"] >= self.limite_saques:
            print("Número máximo de saques atingido hoje.")
            return False
        elif valor <= 0:
            print("Valor inválido.")
            return False

        self.saldo -= valor
        self.saques_hoje["quantidade"] += 1
        self.historico.adicionar_transacao(Saque(valor))
        print("Saque realizado com sucesso!")
        return True

    def depositar(self, valor: float):
        if valor <= 0:
            print("Valor inválido.")
            return False
        self.saldo += valor
        self.historico.adicionar_transacao(Deposito(valor))
        print("Depósito realizado com sucesso!")
        return True


# ==========================
# HISTÓRICO E TRANSAÇÕES
# ==========================
class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append(transacao)

    def mostrar(self, saldo):
        print("\n================ EXTRATO ================")
        if not self.transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for t in self.transacoes:
                print(f"{t.tipo}: R$ {t.valor:.2f} em {t.data.strftime('%d/%m/%Y %H:%M')}")
        print(f"\nSaldo: R$ {saldo:.2f}")
        print("==========================================")


class Transacao(ABC):
    def __init__(self, valor: float):
        self.valor = valor
        self.data = datetime.now()

    @property
    @abstractmethod
    def tipo(self):
        pass


class Saque(Transacao):
    @property
    def tipo(self):
        return "Saque"


class Deposito(Transacao):
    @property
    def tipo(self):
        return "Depósito"


# ==========================
# PROGRAMA PRINCIPAL
# ==========================
class SistemaBancario:
    def __init__(self):
        self.usuarios = {}
        self.contas = []
        self.num_conta_seq = 1

    def cadastrar_usuario(self):
        print("\n=== Cadastro de Usuário ===")
        nome = input("Nome: ").strip()
        data_nascimento = input("Data de Nascimento (dd/mm/aaaa): ").strip()

        while True:
            cpf = input("CPF: ").strip()
            try:
                cpf_valido = PessoaFisica.validar_cpf(cpf)
                if cpf_valido in self.usuarios:
                    print("CPF já cadastrado.")
                else:
                    break
            except ValueError:
                print("CPF inválido.")

        endereco = input("Endereço: ").strip()
        pessoa = PessoaFisica(nome, data_nascimento, cpf_valido, endereco)
        self.usuarios[cpf_valido] = pessoa
        print(f"Usuário {nome} cadastrado com sucesso!")

    def listar_usuarios(self):
        if not self.usuarios:
            print("Nenhum usuário cadastrado.")
            return
        for pessoa in self.usuarios.values():
            print(f"{pessoa.nome} | CPF: {pessoa.cpf} | Nasc.: {pessoa.data_nascimento} | End.: {pessoa.endereco}")

    def cadastrar_conta(self):
        if not self.usuarios:
            print("Cadastre um usuário primeiro.")
            return

        self.listar_usuarios()
        cpf = input("Informe o CPF do usuário: ").strip()
        if cpf not in self.usuarios:
            print("CPF não encontrado.")
            return

        cliente = self.usuarios[cpf]
        conta = ContaCorrente(self.num_conta_seq, cliente)
        cliente.adicionar_conta(conta)
        self.contas.append(conta)
        print(f"Conta {self.num_conta_seq} criada para {cliente.nome}")
        self.num_conta_seq += 1

    def listar_contas(self):
        if not self.contas:
            print("Nenhuma conta cadastrada.")
            return
        for c in self.contas:
            print(f"Agência: {c.agencia} | Conta: {c.numero} | Cliente: {c.cliente.nome} | CPF: {c.cliente.cpf}")

    def escolher_conta(self):
        self.listar_contas()
        try:
            num = int(input("Número da conta: "))
            for c in self.contas:
                if c.numero == num:
                    return c
            print("Conta não encontrada.")
        except ValueError:
            print("Entrada inválida.")
        return None

    def operar_conta(self):
        conta = self.escolher_conta()
        if not conta:
            return

        while True:
            opc = input("\n[d] Depositar\n[s] Sacar\n[e] Extrato\n[q] Voltar\n=> ").lower()
            if opc == "d":
                conta.depositar(float(input("Valor do depósito: ")))
            elif opc == "s":
                conta.sacar(float(input("Valor do saque: ")))
            elif opc == "e":
                conta.historico.mostrar(conta.saldo)
            elif opc == "q":
                break
            else:
                print("Opção inválida.")

    def menu(self):
        while True:
            opc = input("\n[1] Cadastrar Usuário\n[2] Cadastrar Conta\n[3] Listar Usuários\n[4] Listar Contas\n[5] Operar Conta\n[q] Sair\n=> ").lower()
            if opc == "1":
                self.cadastrar_usuario()
            elif opc == "2":
                self.cadastrar_conta()
            elif opc == "3":
                self.listar_usuarios()
            elif opc == "4":
                self.listar_contas()
            elif opc == "5":
                self.operar_conta()
            elif opc == "q":
                print("Saindo...")
                break
            else:
                print("Opção inválida.")


if __name__ == "__main__":
    sistema = SistemaBancario()
    sistema.menu()
