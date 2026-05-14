from wake_on_speech import WakeOnSpeech

# Importando as funções dos arquivos dentro da pasta "comandos"
from commands.turn_off_computer.turn_off_computer import turn_off_computer

def main():
    # 1. Cria uma instância do motor de escuta
    # Passamos variações de "Sam" para evitar erros de pronúncia do Google
    assistente = WakeOnSpeech(wake_words=["sam", "sem", "cem"])

    # 2. Registra os comandos do assistente
    # A estrutura é: assistente.registrar_comando([lista de frases], função_importada)
    assistente.registrar_comando(
        ["desligue o computador", "desligar o computador", "desligue a máquina", "desligue o pc"], 
        turn_off_computer
    )
    
    assistente.registrar_comando(
        ["abra a calculadora", "abrir calculadora"], 
        cmd_abrir_calculadora
    )
    
    assistente.registrar_comando(
        ["que horas são", "me diga as horas", "qual a hora atual"], 
        cmd_dizer_hora
    )

    # 3. Inicia o assistente
    assistente.iniciar()

if __name__ == "__main__":
    main()