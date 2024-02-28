import pydobot
from serial.tools import list_ports
import time, inquirer, typer
from yaspin import yaspin

class Dobot:
    def __init__(self) -> None:
        pass

    def conectar_dobot():
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
            device = pydobot.Dobot(port=port, verbose=True)
            print("Conectado ao dobot com sucesso.")
            return device
        except Exception as e:
            print("Falha ao conectar ao robô:" + str({e}))
            return None
        