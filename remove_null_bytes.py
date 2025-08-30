# remove_null_bytes.py

def remove_null_bytes(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()
    content = content.replace(b'\x00', b'')
    with open(file_path, 'wb') as file:
        file.write(content)

if __name__ == "__main__":
    file_path = 'secretaria/models.py'
    remove_null_bytes(file_path)
    # print(f"Null bytes removed from {file_path}") # Removido para produção
