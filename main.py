import socket
import threading

# Estrutura para gerenciar salas
salas = {}

def handle_client(client_socket, client_address):
    global salas
    sala_atual = None

    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Comando: Criar sala
            if data == "1":
                client_socket.send("Digite o nome da sala:".encode())
                nome_sala = client_socket.recv(1024).decode()
                client_socket.send("Digite a senha da sala:".encode())
                senha_sala = client_socket.recv(1024).decode()

                if nome_sala in salas:
                    client_socket.send("Sala já existe. Tente outro nome.".encode())
                else:
                    salas[nome_sala] = {
                        "senha": senha_sala,
                        "usuarios": [client_socket],
                        "ip": f"192.168.0.{len(salas) + 1}",  # Exemplo de IP fictício
                    }
                    sala_atual = nome_sala
                    client_socket.send(f"Sala {nome_sala} criada com sucesso!".encode())

            # Comando: Entrar em sala
            elif data == "2":
                client_socket.send("Digite o nome da sala:".encode())
                nome_sala = client_socket.recv(1024).decode()
                client_socket.send("Digite a senha da sala:".encode())
                senha_sala = client_socket.recv(1024).decode()

                if nome_sala not in salas:
                    client_socket.send("Sala não encontrada.".encode())
                elif salas[nome_sala]["senha"] != senha_sala:
                    client_socket.send("Senha incorreta.".encode())
                else:
                    salas[nome_sala]["usuarios"].append(client_socket)
                    sala_atual = nome_sala
                    client_socket.send(f"Entrou na sala {nome_sala}!".encode())

            # Comando: Ver IP da sala
            elif data.lower() == "ver_ip":
                if sala_atual:
                    ip_sala = salas[sala_atual]["ip"]
                    client_socket.send(f"O IP da sala {sala_atual} é {ip_sala}".encode())
                else:
                    client_socket.send("Você não está em nenhuma sala.".encode())

            # Comando: Sair da sala
            elif data.lower() == "sair":
                if sala_atual:
                    salas[sala_atual]["usuarios"].remove(client_socket)
                    if not salas[sala_atual]["usuarios"]:
                        del salas[sala_atual]
                    sala_atual = None
                client_socket.send("Você saiu da sala.".encode())
                break

            # Qualquer outra mensagem é repassada para todos os usuários da sala
            else:
                if sala_atual:
                    for user in salas[sala_atual]["usuarios"]:
                        if user != client_socket:
                            user.send(data.encode())
                else:
                    client_socket.send("Você não está em nenhuma sala.".encode())
        except:
            break

    client_socket.close()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 80))
    server_socket.listen(5)
    print("Servidor rodando na porta 80.")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Nova conexão de {client_address}.")
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

server()