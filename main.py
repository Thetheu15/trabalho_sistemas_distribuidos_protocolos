from trabalho_distribuidos_string import servidor_string
from trabalho_distribuidos_json import servidor_json
from trabalho_distribuidos_protobuff import servidor_protobuf


if __name__=="__main__":

    while True:
        print('''\nDigite o numero da operações deseja executar:
                1. Estatisticas
                2. Echo
                3. Timestamp
                4. Status
                5. Historico
                6. Info
                7. Parar a execuçao do código''')
        
        resp = int(input("Resposta: "))

        match resp:

            case 1:

                numeros = input("Digite os numeros separados por virgulas: ")

                servidor_string(resp, numeros)
                print("\n")
                servidor_json(resp, numeros)
                print("\n")
                servidor_protobuf(resp, numeros)

            case 2:

                mensagem = input("Digite a mensagem para o eco: ")

                servidor_string(resp, mensagem)
                print("\n")
                servidor_json(resp, mensagem)
                print("\n")
                servidor_protobuf(resp, mensagem)
            
            case 3:

                servidor_string(resp)
                print("\n")
                servidor_json(resp)
                print("\n")
                servidor_protobuf(resp)

            case 4:

                servidor_string(resp)
                print("\n")
                servidor_json(resp)
                print("\n")
                servidor_protobuf(resp)

            case 5:
        
                servidor_string(resp)
                print("\n")
                servidor_json(resp)
                print("\n")
                servidor_protobuf(resp)

            case 6:

                servidor_string(resp)
                print("\n")
                servidor_json(resp)
                print("\n")
                servidor_protobuf(resp)

            case 7:

                print('Parando a execução do código!')

                break