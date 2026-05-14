import speech_recognition as sr

class WakeOnSpeech:
    def __init__(self, wake_words=["sam", "sem", "cem"]):
        self.wake_words = wake_words
        self.comandos = {}  # Dicionário que guardará as frases e funções
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def registrar_comando(self, frases_gatilho, funcao):
        """Associa uma lista de frases a uma função específica."""
        for frase in frases_gatilho:
            self.comandos[frase.lower()] = funcao

    def _capturar_audio(self, tempo_espera=None, tempo_frase=3):
        """Método interno para ouvir o microfone e converter em texto."""
        with self.mic as source:
            try:
                audio = self.recognizer.listen(source, timeout=tempo_espera, phrase_time_limit=tempo_frase)
                texto = self.recognizer.recognize_google(audio, language='pt-BR').lower()
                return texto
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return None
            except sr.RequestError as e:
                print(f"[Erro] Falha na API do Google: {e}")
                return None

    def iniciar(self):
        """Inicia o loop principal de escuta."""
        print("Ajustando microfone para ruído ambiente...")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("\n" + "="*40)
        print(f"🤖 Assistente Online! Diga '{self.wake_words[0].upper()}' para ativar.")
        print("="*40)

        while True:
            try:
                # Aguarda a palavra de ativação
                texto_ativacao = self._capturar_audio(tempo_espera=None, tempo_frase=3)
                
                # Verifica se alguma das wake_words foi dita
                if texto_ativacao and any(ww in texto_ativacao for ww in self.wake_words):
                    print("\n[🔊] Ativado! Ouvindo seu comando...")
                    
                    # Escuta o comando
                    texto_comando = self._capturar_audio(tempo_espera=5, tempo_frase=5)
                    
                    if texto_comando:
                        print(f"    🗣️ Comando recebido: '{texto_comando}'")
                        self._processar_comando(texto_comando)
                    else:
                        print("    [!] Silêncio detectado. Voltando a dormir...")
                        
            except KeyboardInterrupt:
                print("\n[!] Encerrando o assistente...")
                break

    def _processar_comando(self, texto_comando):
        """Verifica se o comando dito existe no dicionário e o executa."""
        for frase_gatilho, funcao in self.comandos.items():
            if frase_gatilho in texto_comando:
                funcao() # Executa a função do arquivo de comandos
                return
        
        print("    [?] Comando não reconhecido ou não cadastrado.")