import io
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from PIL import ImageGrab
import keyboard
from google import genai
from google.genai import types

# Carrega as variáveis do ficheiro .env
load_dotenv()

API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
MODELO_PADRAO: str = "gemini-3.8-flash"

if not API_KEY:
    print("❌ Erro: Chave GEMINI_API_KEY não encontrada no ficheiro .env.")
    print("Certifique-se de preencher: GEMINI_API_KEY=sua_chave dentro de .env")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
_em_processamento: bool = False


def capturar_e_otimizar_ecra(resolucao_maxima: tuple[int, int] = (1280, 720), qualidade: int = 60) -> bytes:
    """Captura o ecrã atual, redimensiona e comprime em formato JPEG na memória."""
    screenshot = ImageGrab.grab()
    screenshot.thumbnail(resolucao_maxima)
    
    with io.BytesIO() as buffer:
        screenshot.save(buffer, format="JPEG", quality=qualidade)
        return buffer.getvalue()


def processar_copiloto() -> None:
    """Função disparada pelo atalho de teclado global."""
    global _em_processamento
    if _em_processamento:
        print("\n⏳ [Aguarde] Já existe uma requisição em processamento...")
        return

    _em_processamento = True
    print("\n" + "=" * 60)
    print("📸 [1/3] A capturar e comprimir o ecrã...")

    try:
        imagem_bytes = capturar_e_otimizar_ecra()

        print(" [2/3] A consultar o modelo Gemini...")
        instrucao_sistema = (
            "Você é um copiloto técnico de ecrã focado em alta produtividade. "
            "Analise a imagem da tela em anexo de forma direta e objetiva. "
            "Se houver um erro de código ou terminal, forneça a causa e a correção exata. "
            "Se houver uma interface ou texto, sintetize o ponto crítico. "
            "Responda em português brasileiro formatado em tópicos curtos."
        )

        resposta = client.models.generate_content(
            model=MODELO_PADRAO,
            contents=[
                types.Part.from_bytes(data=imagem_bytes, mime_type="image/jpeg"),
                instrucao_sistema,
            ],
        )

        print("\n [3/3] Análise Concluída:\n")
        print(resposta.text)
        print("=" * 60)
        print("Pronto para o próximo atalho: [Ctrl + Shift + S] | [Esc] para sair")

    except Exception as erro:
        print(f"\n❌ Falha na execução: {erro}")

    finally:
        _em_processamento = False


def main() -> None:
    """Ponto de entrada do script."""
    print("=" * 60)
    print(" Copiloto de Ecrã com IA Iniciado com Sucesso!")
    print("• Disparar análise: Ctrl + Shift + S")
    print("• Finalizar script: Esc")
    print("=" * 60)

    keyboard.add_hotkey("ctrl+shift+s", processar_copiloto)
    keyboard.wait("esc")
    print("\nSessão encerrada.")


if __name__ == "__main__":
    main()