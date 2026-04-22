from openpyxl import Workbook


from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Pessoas"

# Cabeçalhos

ws.append([
    "CPF", "Nome", "Nome do Pai", "Nome da Mãe", "Data de Nascimento", "Gênero", "Igreja", "Status", "Tipo",
    "Rua", "Número", "Bairro", "Cidade", "Estado", "Telefone", "E-mail"
])

# Definir máscaras de exibição para CPF, Data de Nascimento e Telefone
from openpyxl.styles import numbers
cpf_col = 1
data_col = 5
telefone_col = 15
for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
    # CPF: formato 000.000.000-00 (como texto)
    row[cpf_col-1].number_format = '@'
    # Data de Nascimento: formato dd/mm/aaaa
    row[data_col-1].number_format = 'DD/MM/YYYY'
    # Telefone: formato texto
    row[telefone_col-1].number_format = '@'

# Exemplo de dados
ws.append([
    "123.456.789-00", "João da Silva", "Carlos da Silva", "Ana Souza", "01/01/1990", "M", "Central", "Ativo", "Membro",
    "Rua Exemplo", "123", "Centro", "São Paulo", "SP", "(11) 99999-9999", "joao@email.com"
])
ws.append([
    "987.654.321-00", "Maria Souza", "José Souza", "Clara Lima", "15/05/1985", "F", "Central", "Ativo", "Visitante",
    "Av. Teste", "456", "Bairro Novo", "São Paulo", "SP", "(11) 98888-8888", "maria@email.com"
])

# Aba de dicas
dicas = wb.create_sheet(title="Dicas")
dicas["A1"] = "Dicas de Preenchimento para Importação em Massa"
dicas["A2"] = "- CPF: Obrigatório, formato 000.000.000-00, sem duplicidade."
dicas["A3"] = "- Nome: Obrigatório."
dicas["A4"] = "- Data de Nascimento: Obrigatório, formato dd/mm/aaaa."
dicas["A5"] = "- Gênero: M ou F."
dicas["A6"] = "- Igreja, Status, Tipo: Devem existir no sistema."
dicas["A7"] = "- Endereço, Nome do Pai/Mãe: Opcionais."
dicas["A8"] = "- Telefone/E-mail: Opcionais, mas recomendados."
dicas["A9"] = "- Visitantes: Podem ter menos dados obrigatórios."
dicas["A10"] = "- Se o CPF já existir, o cadastro será atualizado."

wb.save("secretaria/static/docs/modelo_importacao_pessoas.xlsx")
print("Arquivo Excel modelo gerado com sucesso!")
