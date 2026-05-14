from wake_on_speech import WakeOnSpeech

from commands.turn_off_computer.turn_off_computer import turn_off_computer
from commands.ask_gemini.ask_gemini import ask_gemini

def main():
    assistente = WakeOnSpeech(wake_words=["sam", "sem", "cem"])

    # Comando: desligar o computador
    assistente.registrar_comando(
        ["desligue o computador", "desligar o computador", "desligue a máquina",
         "desligue o pc", "desligar pc"],
        turn_off_computer
    )

    # Comando: fazer uma pergunta ao Gemini
    # Ex: "Sam, pergunta" → grava a pergunta → Gemini responde em voz
    assistente.registrar_comando(
        ["pergunta", "me responda", "quero perguntar", "me diga"],
        ask_gemini
    )

    assistente.iniciar()

if __name__ == "__main__":
    main()