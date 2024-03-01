import pydobot
from serial.tools import list_ports
import time, inquirer, typer
from yaspin import yaspin
from tinydb import TinyDB, Query

# Classe do Dobot
class Dobot:
    def __init__(self) -> None:
        pass

    # Função para conectar ao dobot
    def conectar_dobot(self):
        # Dar a opção de escolher a porta de conexão
        portas_disponiveis = list_ports.comports()

        portas = [x.device for x in portas_disponiveis]

        print(f'Portas disponiveis: {[x.device for x in portas_disponiveis]}')

        opcoes = [
        inquirer.List("Porta", message="Qual porta deseja conectar", choices=[x for x in portas if "ttyUSB" in x or "COM" in x
        ])
        ]

        resposta = inquirer.prompt(opcoes)
        port = resposta["Porta"]

        print(f"Conectando ao dobot na porta: {resposta}")

        if not portas_disponiveis:
            print("Sem portas de conexão disponíveis.")
            return None

        try:
            # Incializar o dobot
            self.device = pydobot.Dobot(port=port)
            print("Conectado ao dobot com sucesso.")
        except Exception as e:
            print("Falha ao conectar ao robô:" + str({e}))
    
    # Função de conexão com banco de dados TinyDB
    def conectar_DB(self):
        db = TinyDB('db.json', indent=4)
        return db

    # Função para desconectar do banco de dados
    def desconectar_DB(self, db):
        db.close()

    # Função para salvar a posição atual do dobot
    def salvar_posicao(self, nomePosicao):
        # Instanciar o banco de dados
        db = self.conectar_DB()
        if self.device:
            try:
                # Pegar a posição atual do dobot e inserir no banco de dados
                posicao = self.device.pose()

                db.insert({'nomePosicao': nomePosicao, 'x': posicao[0], 'y': posicao[1], 'z': posicao[2], 'r': posicao[3]})
                print("Posição salva com sucesso.")
            except Exception as e:
                print("Erro ao salvar posição:" + str({e}))
        else:
            print('Conecte ao dobot primeiro.')
    
    # Função para desconectar do dobot
    def desconectar_robot(self):
        if self.device:
            try:
                self.device.close()
                print("Disconectado do dobot com sucesso.")
            except Exception as e:
                print("Erro ao desconectar:" + str({e}))
        else:
            print("Não há conexão com o dobot.")

    # Função para mover o dobot para uma posição salva
    def mover_para_ponto(self, nomePosicao):
        if self.device:
            try:
                # Conectar ao banco de dados
                db = self.conectar_DB()
                # Instanciar a Query
                Posicao = Query()
                nome_da_posicao = nomePosicao['Pontos'] if isinstance(nomePosicao, dict) else nomePosicao
                posicao = db.search(Posicao.nomePosicao == nome_da_posicao)  # Busca no banco de dados o nome itens com o nome da posição
                if posicao:
                    x = posicao[0]['x']
                    y = posicao[0]['y']
                    z = posicao[0]['z']
                    r = posicao[0]['r']
                    # Mover o dobot para a posição
                    self.device.move_to(x, y, z, r, wait=True)
                else:
                    print("Posição não encontrada.")
                self.desconectar_DB(db)
            except Exception as e:
                print("Erro ao mover para a posição:" + str(e))  # Melhor formatação da mensagem de erro
        else:
            print("Conecte ao dobot primeiro.")

    # Função para executar uma sequencia de movimentos
    def sequencia_de_movimentos(self, comandos):
        print(comandos)
        if self.device:
            try:
                # Exemplo de comados
                # comandos = [
                #     {'tipo': 'ponto', 'nome': 'ponto1'},
                #     {'tipo': 'atuador', 'estado': 'on'}
                #     ]
                
                # Interar nos comandos escolhidos
                for comando in comandos:
                    # Executar cada tipo de comando
                    if comando['tipo'] == 'ponto':
                        print(comando['nome'])
                        self.mover_para_ponto(comando['nome'])
                    elif comando['tipo'] == 'atuador':
                        if comando['estado'] == 'On':
                            self.device.suck(True)
                        else:
                            self.device.suck(False)
            except Exception as e:
                print("Erro ao mover para a posição:" + str({e}))
        else:
            print("Conecte ao dobot primeiro.")

    # Função para mover o dobot para uma posição especifica
    def mover_para(self, x, y, z, r):
        if self.device:
            try:
                # Inicializar o spinner
                spiner = yaspin(text="Movendo o braço robotico...", color="yellow")

                spiner.start()
                # Mover o dobot para a posição
                self.device.move_to(x, y, z, r, wait=True)

                spiner.stop()

                print(f"Braço robotico movido para: ({x}, {y}, {z}, {r})")

            except Exception as e:
                print("Erro ao mover o braço" + str({e}))
        else:
            print("Conecte ao dobot primeiro.")

    # Controle de movimentação livre
    def movimentacao_livre(self):
        continuar = True
        if self.device:
            
            # POssibilidade de mover o dobot em qualquer eixo
            while continuar:
                options = [ inquirer.List("Movimentacao", message="Em qual eixo deseja mover?", choices=["X", "Y", "Z", "R", 'Sair']) ]
                
                resposta = inquirer.prompt(options)
                resposta = resposta["Movimentacao"]

                posicaoAtual = self.device.pose()
                
                # Mover o dobot no eixo escolhido e a taxa de movimentação
                if resposta == "X":
                    taxaX = float(input("Quanto deseja mover em X?"))
                    self.device.move_to(posicaoAtual[0]+taxaX, posicaoAtual[1], posicaoAtual[2], posicaoAtual[3], wait=True)
                elif resposta == "Y":
                    taxaY = float(input("Quanto deseja mover em Y?"))
                    self.device.move_to(posicaoAtual[0], posicaoAtual[1]+taxaY, posicaoAtual[2], posicaoAtual[3], wait=True)
                elif resposta == "Z":
                    taxaZ = float(input("Quanto deseja mover em Z?"))
                    self.device.move_to(posicaoAtual[0], posicaoAtual[1], posicaoAtual[2]+taxaZ, posicaoAtual[3], wait=True)
                elif resposta == "R":
                    taxaR = float(input("Quanto deseja mover em R?"))
                    self.device.move_to(posicaoAtual[0], posicaoAtual[1], posicaoAtual[2], posicaoAtual[3]+taxaR, wait=True)
                elif resposta == 'Sair':
                    continuar = False
        else:
            print("Conecte ao dobot primeiro.")

    # Função para controlar o atuador
    def atuador(self):
        opcoesAcao = [
            inquirer.List("Ação", message="Qual ação deseja realizar?", choices=["suck", "grip"])
            ]
        
        respostaAcao = inquirer.prompt(opcoesAcao)
        respostaAcao = respostaAcao["Ação"]

        opcoesEstado = [
        inquirer.List("Estado", message="Ligar ou Desligar?", choices=["On", "off"])
        ]

        respostaEstado = inquirer.prompt(opcoesEstado)
        respostaEstado = respostaEstado["Estado"]

        # Ligar ou desligar o suck ou grip
        if self.device:
            try:
                if respostaAcao == "suck":
                    if respostaEstado == "On":
                        self.device.suck(True)
                    else:
                        self.device.suck(False)
                elif respostaAcao == "grip":
                    if respostaEstado == "On":
                        self.device.grab(True)
                    else:
                        self.device.grab(False)
            except Exception as e:
                print("Erro na ação:" + str({e}))

    # Função principal para controlar o dobot pela CLI
    def CLI(self):
        dobot_conectado = None
        continuar_prorgama = True

        # incializar_programa()

        while continuar_prorgama:
            
            # Oferecer as opções de comandos
            opcoes = [
                inquirer.List("Comando", message="Qual comando deseja realizar?", choices=["Conectar", "Disconectar", "Mover para","Atuador", "Posição Atual", "Sair"])
                ]
            
            print("teste" + str(opcoes))

            resposta = inquirer.prompt(opcoes)
            resposta = resposta["Comando"]

            match resposta:
            # Verifica qual comando foi escolhido
                case "Conectar":
                    dobot_conectado = self.conectar_dobot()
                
                case "Disconectar":
                    self.desconectar_robot(dobot_conectado)
                    dobot_conectado = None
                
                case "Mover para":

                    # Ofercer as opções de movimentação
                    opcoes = [
                    inquirer.List("Tipo de movimento", message="Mover para:", choices=["Localizacao espesifica", "Pontos pre determinados", 'Salvar Ponto', "Sequencia de movimentos","Movimentacao Livre", "Home", 'Voltar menu'])
                    ]
                    
                    resposta = inquirer.prompt(opcoes)
                    resposta = resposta["Tipo de movimento"]

                    match resposta:

                        case "Localizacao espesifica":
                            x = float(input("X:"))
                            y = float(input("Y:"))
                            z = float(input("Z:"))
                            r = float(input("R:"))
                            self.mover_para(x, y, z, r)
                        case "Pontos pre determinados":
                            # Conectar ao banco de dados
                            db = self.conectar_DB()
                            Posicao = Query()  # Instanciar Query
                            posicoes = db.search(Posicao.nomePosicao.exists())  # Buscar todas as posições

                            # Dar a opção do usuário escolher qual posição salva
                            opcoes = [
                                inquirer.List("Pontos", message="Para qual ponto mover o robo?:", choices=[p['nomePosicao'] for p in posicoes])
                            ]

                            resposta = inquirer.prompt(opcoes)
                            self.mover_para_ponto(resposta)

                        case "Salvar Ponto":
                            nomePosicao = input("Digite o nome da posição: ")
                            self.salvar_posicao(nomePosicao)
                        case "Sequencia de movimentos":
                            comandos = []
                            continuar = True

                            # Oferecer número ilimitado de comandos
                            while continuar:
                                opcoes = [
                                    inquirer.List("Tipo de movimento", message="Mover para:", choices=["Ponto", "Atuador", "Sair"])
                                ]
                                resposta = inquirer.prompt(opcoes)
                                resposta = resposta["Tipo de movimento"]

                                # Adicionar cada resposta a lista de comandos para enviar para a função
                                if resposta == "Ponto":
                                    db = self.conectar_DB()
                                    Posicao = Query()  # Instanciar Query
                                    posicoes = db.search(Posicao.nomePosicao.exists())  # Buscar todas as posições
                                    
                                    # Oferecer a opção de escolher um ponto salvo
                                    opcoes = [
                                        inquirer.List("Pontos", message="Para qual ponto mover o robo?:", choices=[p['nomePosicao'] for p in posicoes])
                                    ]

                                    resposta = inquirer.prompt(opcoes)
                                    resposta = resposta["Pontos"]
                                    comandos.append({'tipo': 'ponto', 'nome': resposta})
                                elif resposta == "Atuador":
                                    opcoesAcao = [
                                        inquirer.List("Ação", message="Qual ação deseja realizar?", choices=["suck", "grip"])
                                    ]
                                    
                                    respostaAcao = inquirer.prompt(opcoesAcao)
                                    respostaAcao = respostaAcao["Ação"]

                                    opcoesEstado = [
                                    inquirer.List("Estado", message="Ligar ou Desligar?", choices=["On", "off"])
                                    ]

                                    respostaEstado = inquirer.prompt(opcoesEstado)
                                    respostaEstado = respostaEstado["Estado"]
                                    comandos.append({'tipo': 'atuador', 'estado': respostaEstado})
                                else:
                                    continuar = False
                            self.sequencia_de_movimentos(comandos)
                        case "Movimentacao Livre":
                            self.movimentacao_livre()
                        case "Home":
                            # Coordenados para a posição home
                            self.mover_para(243, 0, 151, 0)
                        case 'Voltar menu':
                            self.CLI()
                        case _:
                            print("Comando invalido.")

                case "Atuador":
                    self.atuador()

                case "Posição Atual":
                    if self.device:
                        print(f'A posição do braço é: \n {self.device.pose()}')
                    else:
                        print("Conecte ao dobot primeiro.")
                case "Sair":
                    self.desconectar_robot()
                    print("Saindo do programa")
                    break
                case _:
                    print("Comando invalido.")

            # continuar_prorgama = typer.confirm("Deseja continuar?") 

# Inicializar uma instacncia da classe dobot
meuRobo = Dobot()
meuRobo.CLI()