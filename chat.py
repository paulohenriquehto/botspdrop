#!/usr/bin/env python3
from agentes.agente_suporte import support_agent
from dotenv import load_dotenv

load_dotenv()

def main():
    print("\n" + "="*60)
    print("  CHAT COM AGENTE DE SUPORTE - Agno Framework")
    print("="*60)
    print("Digite suas dúvidas e receba suporte imediato.")
    print("Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_input = input("Você: ").strip()

            if user_input.lower() == 'sair':
                print("\nAté logo! 👋")
                break

            if not user_input:
                print("Digite algo para continuar...\n")
                continue

            print("\nAgente: ", end="")
            support_agent.print_response(user_input, stream=True)
            print("\n")

        except KeyboardInterrupt:
            print("\n\nAté logo! 👋")
            break
        except Exception as e:
            print(f"\nErro: {e}\n")

if __name__ == "__main__":
    main()
