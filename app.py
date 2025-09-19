# # import gspread
# # import os
# # import json
# # import google.generativeai as genai
# # from dotenv import load_dotenv
# # from fpdf import FPDF

# # def buscar_catalogo_da_planilha():
# #     """Se conecta à planilha do Google e retorna os produtos como uma lista de dicionários."""
# #     try:
# #         gc = gspread.service_account(filename='credentials.json')
# #         planilha = gc.open("dados-agente") # <-- ATENÇÃO: Verifique o nome da sua planilha
# #         aba = planilha.sheet1
# #         produtos = aba.get_all_records()
# #         print("✅ Catálogo de produtos carregado da planilha com sucesso!")
# #         return produtos
# #     except Exception as e:
# #         print(f"❌ Erro ao carregar catálogo da planilha: {e}")
# #         return None

# # def gerar_proposta(pedido_tecnico: str, catalogo_produtos: list) -> dict:
# #     """
# #     Orquestra a criação de uma proposta de sonorização usando a IA do Gemini.
# #     """
# #     print("🤖 Iniciando a geração da proposta com a IA...")
# #     prompt_template = f"""
# #     Você é um projetista sênior de sistemas de sonorização ambiente. Sua tarefa é criar uma proposta técnica e comercial detalhada.

# #     1.  **Base de Conhecimento:** Utilize estritamente os produtos listados abaixo. Não invente produtos.
# #         ```json
# #         {json.dumps(catalogo_produtos, indent=2, ensure_ascii=False)}
# #         ```

# #     2.  **Pedido do Técnico:** Analise a seguinte solicitação:
# #         "{pedido_tecnico}"

# #     3.  **Sua Tarefa:**
# #         -   Analise cada ambiente descrito no pedido.
# #         -   Selecione os produtos e quantidades apropriadas do catálogo para atender às necessidades.
# #         -   Calcule o subtotal para cada item (quantidade * preço).

# #     4.  **Formato da Resposta:** Sua resposta final DEVE SER APENAS um objeto JSON válido, sem nenhum texto antes ou depois. O JSON deve ter a seguinte estrutura:
# #         {{
# #             "analise_projeto": "Um parágrafo explicando suas escolhas técnicas para o projeto.",
# #             "itens_proposta": [
# #                 {{
# #                     "produto": "Nome do Produto",
# #                     "quantidade": X,
# #                     "preco_unitario": Y,
# #                     "subtotal": Z
# #                 }}
# #             ],
# #             "valor_total": W
# #         }}
# #     """
# #     try:
# #         print("🧠 Conectando ao cérebro do Gemini...")
# #         load_dotenv()
# #         api_key = os.getenv("GOOGLE_API_KEY")
# #         if not api_key:
# #             print("❌ Chave de API não encontrada. Verifique seu arquivo .env")
# #             return None
        
# #         genai.configure(api_key=api_key)
        
# #         model = genai.GenerativeModel('gemini-1.5-flash-latest')
# #         response = model.generate_content(prompt_template)
        
# #         print("💡 Resposta recebida da IA!")
        
# #         resposta_texto = response.text.strip()
# #         if resposta_texto.startswith("```json"):
# #             resposta_texto = resposta_texto[7:]
# #         if resposta_texto.endswith("```"):
# #             resposta_texto = resposta_texto[:-3]
        
# #         proposta_json = json.loads(resposta_texto)
# #         return proposta_json

# #     except json.JSONDecodeError:
# #         print("❌ ERRO: A IA retornou um formato que não é JSON válido.")
# #         print("Resposta recebida:", response.text)
# #         return None
# #     except Exception as e:
# #         print(f"❌ Ocorreu um erro inesperado ao conectar com a API do Gemini: {e}")
# #         return None

# # def gerar_pdf_proposta(proposta: dict, nome_cliente: str):
# #     """Pega o dicionário da proposta e gera um arquivo PDF."""
# #     try:
# #         pdf = FPDF()
# #         pdf.add_page()
# #         pdf.set_font("Arial", "B", 16)
        
# #         pdf.cell(0, 10, "Proposta de Sonorização Ambiente", 0, 1, "C")
# #         pdf.set_font("Arial", "", 12)
# #         pdf.cell(0, 10, f"Cliente: {nome_cliente}", 0, 1, "C")
# #         pdf.ln(10)

# #         pdf.set_font("Arial", "B", 12)
# #         pdf.cell(0, 10, "Análise do Projeto", 0, 1)
# #         pdf.set_font("Arial", "", 12)
# #         pdf.multi_cell(0, 5, proposta['analise_projeto'].encode('latin-1', 'replace').decode('latin-1'))
# #         pdf.ln(10)

# #         pdf.set_font("Arial", "B", 12)
# #         pdf.cell(100, 10, "Produto", 1, 0, "C")
# #         pdf.cell(20, 10, "Qtd", 1, 0, "C")
# #         pdf.cell(35, 10, "Preço Unit.", 1, 0, "C")
# #         pdf.cell(35, 10, "Subtotal", 1, 1, "C")

# #         pdf.set_font("Arial", "", 10)
# #         for item in proposta['itens_proposta']:
# #             pdf.cell(100, 10, item['produto'].encode('latin-1', 'replace').decode('latin-1'), 1, 0)
# #             pdf.cell(20, 10, str(item['quantidade']), 1, 0, "C")
# #             pdf.cell(35, 10, f"R$ {item['preco_unitario']:.2f}", 1, 0, "R")
# #             pdf.cell(35, 10, f"R$ {item['subtotal']:.2f}", 1, 1, "R")
        
# #         pdf.set_font("Arial", "B", 12)
# #         pdf.cell(155, 10, "VALOR TOTAL DO PROJETO", 1, 0)
# #         pdf.cell(35, 10, f"R$ {proposta['valor_total']:.2f}", 1, 1, "R")

# #         nome_arquivo = f"proposta_{nome_cliente.replace(' ', '_').lower()}.pdf"
# #         pdf.output(nome_arquivo)
# #         print(f"\n✅ PDF gerado com sucesso! Arquivo: {nome_arquivo}")

# #     except Exception as e:
# #         print(f"❌ Erro ao gerar PDF: {e}")


# # if __name__ == "__main__":
# #     catalogo_produtos = buscar_catalogo_da_planilha()
    
# #     if catalogo_produtos:
# #         cliente = "Vitorio Real" # Mudamos o nome para ver a diferença
# #         pedido = "Estou com um projeto para um apartamento. Preciso sonorizar uma sala de TV de 20m2, com forro de gesso, onde o cliente quer som de cinema. Também preciso de som para uma cozinha integrada de 15m2 e um lavabo pequeno de 4m2."

# #         proposta_final = gerar_proposta(pedido, catalogo_produtos)

# #         if proposta_final:
# #             gerar_pdf_proposta(proposta_final, cliente)

# from flask import Flask, render_template

# # Cria a nossa aplicação web
# app = Flask(__name__)

# # Isso é um "decorador". É como uma placa de trânsito.
# # Diz: "Quando alguém acessar a página principal ('/'), execute a função abaixo."
# @app.route('/')
# def homepage():
#     """Esta função é executada quando a rota principal é acessada."""
#     # A mágica acontece aqui: render_template busca um arquivo no diretório 'templates'
#     # e o envia para o navegador do usuário.
#     return render_template('index.html')

# # O código abaixo permite executar o app diretamente com "python app.py"
# # mas a forma recomendada é usar "flask run" no terminal.
# if __name__ == '__main__':
#     app.run(debug=True) # debug=True é ótimo para desenvolvimento, ele reinicia o servidor a cada alteração.

# Importações necessárias do Flask
from flask import Flask, render_template, request, send_file
import os
import io 

# Nossas importações antigas
import gspread
import json
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF

# Cria a nossa aplicação web
app = Flask(__name__)

# --- Nossas funções do backend ---

def buscar_catalogo_da_planilha():
    """Se conecta à planilha do Google e retorna os produtos."""
    try:
        gc = gspread.service_account(filename='credentials.json')
        # ATENÇÃO: Verifique se "dados-agente" é o nome exato da sua planilha.
        planilha = gc.open("dados-agente") 
        aba = planilha.sheet1
        produtos = aba.get_all_records()
        print("✅ Catálogo de produtos carregado da planilha.")
        return produtos
    except Exception as e:
        print(f"❌ Erro ao carregar catálogo: {e}")
        return None

def gerar_proposta_ia(pedido_tecnico: str, catalogo_produtos: list) -> dict:
    """Gera a proposta usando a IA do Gemini."""
    print("🤖 Iniciando a geração da proposta com a IA...")
    prompt_template = f"""
    Você é um projetista sênior de sistemas de sonorização ambiente. Sua tarefa é criar uma proposta técnica e comercial detalhada.

    1.  **Base de Conhecimento:** Utilize estritamente os produtos listados abaixo.
        ```json
        {json.dumps(catalogo_produtos, indent=2, ensure_ascii=False)}
        ```
    2.  **Pedido do Técnico:** Analise a seguinte solicitação:
        "{pedido_tecnico}"
    3.  **Formato da Resposta:** Sua resposta final DEVE SER APENAS um objeto JSON válido, com a seguinte estrutura:
        {{
            "analise_projeto": "...",
            "itens_proposta": [
                {{
                    "produto": "Nome do Produto",
                    "quantidade": X,
                    "preco_unitario": Y,
                    "subtotal": Z
                }}
             ],
            "valor_total": ...
        }}
    """
    try:
        print("🧠 Conectando ao Gemini...")
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ Chave de API não encontrada.")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt_template)
        
        print("💡 Resposta recebida da IA!")
        
        resposta_texto = response.text.strip().replace("```json", "").replace("```", "")
        proposta_json = json.loads(resposta_texto)
        return proposta_json
    except Exception as e:
        print(f"❌ Erro na chamada da IA: {e}")
        return None

def gerar_pdf_proposta(proposta: dict, nome_cliente: str) -> bytes:
    """Gera o PDF e o retorna em memória como bytes. (VERSÃO CORRIGIDA)"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        pdf.cell(0, 10, "Proposta de Sonorização Ambiente", 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Cliente: {nome_cliente}", 0, 1, "C")
        pdf.ln(10)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Análise do Projeto", 0, 1)
        pdf.set_font("Arial", "", 12)
        # ### CORREÇÃO ###: Usamos str() para garantir que o conteúdo seja texto e removemos o .encode()
        pdf.multi_cell(0, 5, str(proposta['analise_projeto']))
        pdf.ln(10)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 10, "Produto", 1, 0, "C")
        pdf.cell(20, 10, "Qtd", 1, 0, "C")
        pdf.cell(35, 10, "Preço Unit.", 1, 0, "C")
        pdf.cell(35, 10, "Subtotal", 1, 1, "C")

        pdf.set_font("Arial", "", 10)
        for item in proposta['itens_proposta']:
            # ### CORREÇÃO ###: Convertemos cada item para string antes de exibi-lo e removemos o .encode()
            produto = str(item.get('produto', 'N/A')) # .get() é mais seguro que []
            quantidade = str(item.get('quantidade', 0))
            preco_unit = f"R$ {item.get('preco_unitario', 0.0):.2f}"
            subtotal = f"R$ {item.get('subtotal', 0.0):.2f}"
            
            pdf.cell(100, 10, produto, 1, 0)
            pdf.cell(20, 10, quantidade, 1, 0, "C")
            pdf.cell(35, 10, preco_unit, 1, 0, "R")
            pdf.cell(35, 10, subtotal, 1, 1, "R")
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(155, 10, "VALOR TOTAL DO PROJETO", 1, 0)
        pdf.cell(35, 10, f"R$ {proposta.get('valor_total', 0.0):.2f}", 1, 1, "R")
        
        # ### CORREÇÃO ###: A biblioteca moderna lida com a codificação. Retornamos os bytes diretamente.
        return pdf.output()

    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return None


# --- ROTAS DA NOSSA APLICAÇÃO WEB ---

@app.route('/')
def homepage():
    """Renderiza a página inicial com o formulário."""
    return render_template('index.html')

@app.route('/gerar_proposta', methods=['POST'])
def rota_gerar_proposta():
    """Recebe os dados do formulário, processa tudo e retorna o PDF."""
    print("Recebida requisição para gerar proposta...")
    
    nome_cliente = request.form['nome_cliente']
    pedido_tecnico = request.form['pedido_tecnico']
    
    catalogo = buscar_catalogo_da_planilha()
    if not catalogo:
        return "Erro: Não foi possível carregar o catálogo de produtos da planilha.", 500

    proposta_ia = gerar_proposta_ia(pedido_tecnico, catalogo)
    if not proposta_ia:
        return "Erro: A IA não conseguiu gerar uma proposta.", 500
        
    pdf_bytes = gerar_pdf_proposta(proposta_ia, nome_cliente)
    if not pdf_bytes:
        return "Erro: Não foi possível gerar o arquivo PDF.", 500
        
    print(f"✅ Proposta para '{nome_cliente}' gerada com sucesso! Enviando PDF...")
    
    nome_arquivo = f"proposta_{nome_cliente.replace(' ', '_').lower()}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nome_arquivo
    )

if __name__ == '__main__':
    app.run(debug=True)