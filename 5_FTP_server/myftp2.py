# python3

import socket
import sys
import time
import threading
import os

dirname = os.path.join(os.getcwd(), 'docs')

def process(req):
    if req == 'pwd':
        return dirname
    elif req == 'ls':
        return '; '.join(os.listdir(dirname))
    return 'bad request'

def run_server(port=53210):
  serv_sock = create_serv_sock(port)
  cid = 0
  while True:
    client_sock = accept_client_conn(serv_sock, cid)
    t = threading.Thread(target=serve_client,
                         args=(serv_sock, client_sock, cid))
    t.start()
    cid += 1

def serve_client(serv_sock, client_sock, cid):
  request = read_request(client_sock)
  if request is None:
    print(f'Client #{cid} unexpectedly disconnected')
  else:
    if 'exit' in request.decode('utf-8'):
      write_response_close(client_sock, 'exit'.encode('utf-8'), cid)
    elif 'sstop' in request.decode('utf-8'):
      write_response_closes(serv_sock, client_sock, 'cstop'.encode('utf-8'), cid)
    else:
      response = handle_request(request.decode('utf-8'))
      write_response(client_sock, response.encode('utf-8'), cid)

def create_serv_sock(serv_port):
  serv_sock = socket.socket(socket.AF_INET,
                            socket.SOCK_STREAM,
                            proto=0)
  serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  serv_sock.bind(('', serv_port))
  serv_sock.listen()
  return serv_sock

def accept_client_conn(serv_sock, cid):
  client_sock, client_addr = serv_sock.accept()
  print(f'Client #{cid} connected '
        f'{client_addr[0]}:{client_addr[1]}')
  return client_sock

def read_request(client_sock):
  request = bytearray()
  try:
    while True:
      request = client_sock.recv(1024)
      if not request:
      # Клиент преждевременно отключился.
        return None
      return request

  except ConnectionResetError:
    # Соединение было неожиданно разорвано.
    return None
  except:
    raise

def handle_request(request):
  #time.sleep(5)
  return process(request)

def write_response(client_sock, response, cid):
  client_sock.sendall(response)
  client_sock.close()
  print(f'Client #{cid} has been served')

def write_response_close(client_sock, response, cid):
  client_sock.sendall(response)
  client_sock.close()
  print(f'Client #{cid} has been served')

def write_response_closes(serv_sock, client_sock, response, cid):
  client_sock.sendall(response)
  client_sock.close()
  serv_sock.close()
  print(f'Client #{cid} has been stoped server')
  os._exit(0)

if __name__ == '__main__':
  try:
    run_server(port=int(sys.argv[1]))
  except:
    os._exit(0)
