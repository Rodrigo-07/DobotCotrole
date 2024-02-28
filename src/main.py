import pydobot
from serial.tools import list_ports
import time, inquirer, typer
from yaspin import yaspin
from tinydb import TinyDB, Query


class Dobot:
    def __init__(self) -> None:
        pass

    def conectar_dobot(self):
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
            self.device = pydobot.Dobot(port=port, verbose=True)
            print("Conectado ao dobot com sucesso.")
        except Exception as e:
            print("Falha ao conectar ao robô:" + str({e}))
    
    def conectar_DB(self):
        db = TinyDB('db.json')
        return db

    def desconectar_DB(self, db):
        db.close()

    def salvar_posicao(self, db, nomePosicao):
        if self.device:
            try:
                x,y,z,r = self.device.pose()
                db.insert({'nomePosicao': nomePosicao, 'x': x, 'y': y, 'z': z, 'r': r})
                print("Posição salva com sucesso.")
            except Exception as e:
                print("Erro ao salvar posição:" + str({e}))
        else:
            print('Conecte ao dobot primeiro.')
    
    def desconectar_robot(self):
        if self.device:
            try:
                self.device.close()
                print("Disconectado do dobot com sucesso.")
            except Exception as e:
                print("Erro ao desconectar:" + str({e}))
        else:
            print("Não há conexão com o dobot.")

    def mover_para_ponto(self, nomePosicao):
        if self.device:
            try:
                db = self.conectar_DB()
                Posicao = Query()
                posicao = db.search(Posicao.nomePosicao == nomePosicao)
                if posicao:
                    x = posicao[0]['x']
                    y = posicao[0]['y']
                    z = posicao[0]['z']
                    r = posicao[0]['r']
                    self.device.move_to(x, y, z, r, wait=True)
                else:
                    print("Posição não encontrada.")
                self.desconectar_DB(db)
            except Exception as e:
                print("Erro ao mover para a posição:" + str({e}))
        else:
            print("Conecte ao dobot primeiro.")

    def mover_para(self, x, y, z, r):
        if self.device:
            try:
                spiner = yaspin(text="Movendo o braço robotico...", color="yellow")

                spiner.start()
                self.device.move_to(x, y, z, r, wait=True)

                spiner.stop()

                print(f"Braço robotico movido para: ({x}, {y}, {z}, {r})")

            except Exception as e:
                print("Erro ao mover o braço" + str({e}))
        else:
            print("Conecte ao dobot primeiro.")

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

    def CLI(self):
        dobot_conectado = None
        continuar_prorgama = True

        # incializar_programa()

        while continuar_prorgama:

            opcoes = [
                inquirer.List("Comando", message="Qual comando deseja realizar?", choices=["Conectar", "Disconectar", "Mover para","Atuador", "Sair"])
                ]
            
            print("teste" + str(opcoes))

            resposta = inquirer.prompt(opcoes)
            resposta = resposta["Comando"]

            # Verifica qual comando foi escolhido
            if resposta == "Conectar":
                dobot_conectado = self.conectar_dobot()
            
            elif resposta == "Disconectar":
                self.desconectar_robot(dobot_conectado)
                dobot_conectado = None
            
            elif resposta == "Mover parar":
                if dobot_conectado:

                    opcoes = [
                    inquirer.List("Tipo de movimento", message="Mover para:", choices=["Localizacao espesifica", "Pontos pre determinados", 'Salvar Ponto', "Home"])
                    ]
                    
                    resposta = inquirer.prompt(opcoes)
                    resposta = resposta["Tipo de movimento"]

                    if resposta == "Localizacao espesifica":
                        x = float(input("X "))
                        y = float(input("Y"))
                        z = float(input("Z"))
                        r = float(input("R"))
                        self.mover_para(dobot_conectado, x, y, z, r)
                    elif resposta == "Pontos pre determinados":
                        db = self.conectar_DB()
                        pontos = Query
                        posicoes = db.search(pontos.nomePosicao)
                        opcoes = [
                            inquirer.List("Pontos", message="Para qual ponto mover o robo?:", choices=[x for x in posicoes])
                        ]

                        resposta = inquirer.prompt(opcoes)
                        port = resposta["Porta"]

                    elif resposta == "Salvar Ponto":
                        nomePosicao = input("Digite o nome da posição: ")
                        self.salvar_posicao(dobot_conectado, nomePosicao)
                    elif resposta == "Home":
                        pass
                else:
                    print("Please connect to Dobot first.")

            elif resposta == "Atuador":
                if dobot_conectado:
                    self.atuador(dobot_conectado)
                else:
                    print("Please connect to Dobot first.")
            
            elif resposta == "Sair":
                self.desconectar_robot(dobot_conectado)
                print("Exiting program.")
                break
            else:
                print("Invalid command.")

            # continuar_prorgama = typer.confirm("Deseja continuar?") 

meuRobo = Dobot()
meuRobo.CLI()