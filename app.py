# # # Importações necessárias do Flask
# # from flask import Flask, render_template, request, send_file
# # import os
# # import io
# # from werkzeug.utils import secure_filename # <-- Nova importação para segurança de ficheiros

# # # Nossas importações para IA, planilhas e PDF
# # import gspread
# # import json
# # import openai
# # from dotenv import load_dotenv
# # from fpdf import FPDF

# # # Cria a nossa aplicação web
# # app = Flask(__name__)

# # # --- CONFIGURAÇÃO DO UPLOAD ---
# # # Define a pasta onde os uploads serão guardados
# # UPLOAD_FOLDER = os.path.join('static', 'uploads')
# # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # # Garante que a pasta de uploads existe
# # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# # # --- FUNÇÕES DO BACKEND (gerar_proposta_ia, buscar_catalogo, etc.) ---
# # # (Estas funções continuam EXATAMENTE IGUAIS a antes)
# # # ... (copie e cole aqui as suas funções buscar_catalogo_da_planilha, gerar_proposta_ia, e gerar_pdf_proposta) ...
# # def buscar_catalogo_da_planilha():
# #     """Se conecta à planilha do Google e retorna os produtos."""
# #     try:
# #         gc = gspread.service_account(filename='credentials.json')
# #         planilha = gc.open("dados-agente") 
# #         aba = planilha.sheet1
# #         produtos = aba.get_all_records()
# #         print("✅ Catálogo de produtos carregado da planilha.")
# #         return produtos
# #     except Exception as e:
# #         print(f"❌ Erro ao carregar catálogo: {e}")
# #         return None

# # def gerar_proposta_ia(pedido_tecnico: str, catalogo_produtos: list) -> dict:
# #     """Gera a proposta usando a IA da OpenAI (GPT-4o), focada em texto."""
# #     print("🤖 Iniciando a geração da proposta com o cérebro OpenAI...")
    
# #     try:
# #         load_dotenv()
# #         api_key = os.getenv("OPENAI_API_KEY")
# #         if not api_key:
# #             print("❌ Chave de API da OpenAI não encontrada no ficheiro .env")
# #             return None
        
# #         client = openai.OpenAI(api_key=api_key)
# #         system_message = """
# #         Você é um projetista sênior de sistemas de sonorização ambiente. Sua tarefa é criar uma proposta técnica e comercial detalhada com base na descrição fornecida.
# #         **Regras Estritas:**
# #         1.  **Análise do Pedido:** Analise a descrição do projeto, incluindo medidas, tipo de teto, e desejos do cliente.
# #         2.  **Seleção de Produtos:** Utilize estritamente os produtos do catálogo JSON fornecido. Use o nome exato do produto do catálogo, não o código.
# #         3.  **Formato da Resposta:** Sua resposta final DEVE SER APENAS um objeto JSON válido, sem texto adicional ou markdown. A estrutura do JSON deve ser exatamente esta:
# #             {
# #                 "analise_projeto": "Um parágrafo explicando suas escolhas técnicas com base na descrição fornecida.",
# #                 "itens_proposta": [
# #                     {
# #                         "produto": "Nome Exato do Produto do Catálogo",
# #                         "quantidade": 0,
# #                         "preco_unitario": 0.0,
# #                         "subtotal": 0.0
# #                     }
# #                 ],
# #                 "valor_total": 0.0
# #             }
# #         """
# #         user_content = f"""
# #         Base de Conhecimento (Catálogo de Produtos):
# #         ```json
# #         {json.dumps(catalogo_produtos, indent=2, ensure_ascii=False)}
# #         ```
# #         Pedido do Técnico:
# #         "{pedido_tecnico}"
# #         """
# #         print("🧠 Conectando ao GPT-4o...")
# #         response = client.chat.completions.create(
# #             model="gpt-4o",
# #             messages=[
# #                 {"role": "system", "content": system_message},
# #                 {"role": "user", "content": user_content}
# #             ],
# #             response_format={"type": "json_object"}
# #         )
# #         print("💡 Resposta recebida da IA!")
# #         if response.choices and response.choices[0].message and response.choices[0].message.content:
# #             proposta_texto = response.choices[0].message.content
# #             proposta_json = json.loads(proposta_texto)
# #             return proposta_json
# #         else:
# #             print("❌ A IA retornou uma resposta vazia.")
# #             return None
# #     except Exception as e:
# #         print(f"❌ Erro na chamada da IA (OpenAI): {e}")
# #         return None

# # def gerar_pdf_proposta(proposta: dict, nome_cliente: str) -> bytes:
# #     """Gera o PDF com a proposta final (uma única página)."""
# #     # (Esta função também não muda por agora)
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
# #         pdf.multi_cell(0, 5, str(proposta.get('analise_projeto', 'Nenhuma análise fornecida.')))
# #         pdf.ln(10)
# #         pdf.set_font("Arial", "B", 12)
# #         pdf.cell(100, 10, "Produto", 1, 0, "C")
# #         pdf.cell(20, 10, "Qtd", 1, 0, "C")
# #         pdf.cell(35, 10, "Preço Unit.", 1, 0, "C")
# #         pdf.cell(35, 10, "Subtotal", 1, 1, "C")
# #         pdf.set_font("Arial", "", 10)
# #         for item in proposta.get('itens_proposta', []):
# #             produto = str(item.get('produto', 'N/A'))
# #             quantidade = str(item.get('quantidade', 0))
# #             preco_unit = f"R$ {item.get('preco_unitario', 0.0):.2f}"
# #             subtotal = f"R$ {item.get('subtotal', 0.0):.2f}"
# #             pdf.cell(100, 10, produto, 1, 0)
# #             pdf.cell(20, 10, quantidade, 1, 0, "C")
# #             pdf.cell(35, 10, preco_unit, 1, 0, "R")
# #             pdf.cell(35, 10, subtotal, 1, 1, "R")
# #         pdf.set_font("Arial", "B", 12)
# #         pdf.cell(155, 10, "VALOR TOTAL DO PROJETO", 1, 0)
# #         pdf.cell(35, 10, f"R$ {proposta.get('valor_total', 0.0):.2f}", 1, 1, "R")
# #         return pdf.output()
# #     except Exception as e:
# #         print(f"❌ Erro ao gerar PDF: {e}")
# #         return None

# # # --- ROTAS DA APLICAÇÃO WEB ---

# # @app.route('/')
# # def homepage():
# #     """Renderiza a página inicial com o formulário."""
# #     return render_template('index.html')

# # @app.route('/gerar_proposta', methods=['POST'])
# # def rota_gerar_proposta():
# #     """
# #     Passo 1: Recebe o pedido, GUARDA A IMAGEM, chama a IA e exibe a página de revisão.
# #     """
# #     print("PASSO 1: Recebida requisição inicial...")
# #     nome_cliente = request.form['nome_cliente']
# #     pedido_tecnico = request.form['pedido_tecnico']
# #     planta_url = None # Começamos sem URL

# #     # --- LÓGICA DE UPLOAD DA IMAGEM ---
# #     if 'planta_imagem' in request.files:
# #         ficheiro_planta = request.files['planta_imagem']
        
# #         # Verifica se o utilizador realmente selecionou um ficheiro
# #         if ficheiro_planta.filename != '':
# #             # Limpa o nome do ficheiro para segurança
# #             filename = secure_filename(ficheiro_planta.filename)
# #             # Cria o caminho completo para guardar o ficheiro
# #             caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
# #             # Guarda o ficheiro no nosso servidor
# #             ficheiro_planta.save(caminho_completo)
            
# #             # Criamos o URL que o HTML pode usar para encontrar a imagem
# #             planta_url = f"/static/uploads/{filename}"
# #             print(f"🖼️ Imagem da planta guardada em: {caminho_completo}")
    
# #     # --- LÓGICA DA IA (não mudou) ---
# #     catalogo = buscar_catalogo_da_planilha()
# #     if not catalogo:
# #         return "Erro: Não foi possível carregar o catálogo de produtos da planilha.", 500

# #     proposta_sugerida = gerar_proposta_ia(pedido_tecnico, catalogo)
# #     if not proposta_sugerida:
# #         return "Erro: A IA não conseguiu gerar uma proposta. Tente novamente.", 500
    
# #     # --- ENVIA TUDO PARA A PÁGINA DE REVISÃO ---
# #     print("✅ Proposta da IA recebida. A exibir página de revisão com a planta...")
# #     return render_template('review.html', 
# #                            nome_cliente=nome_cliente, 
# #                            proposta=proposta_sugerida, 
# #                            catalogo_completo=catalogo,
# #                            planta_url=planta_url) # <-- A nova informação que estamos a enviar!

# # @app.route('/criar_pdf', methods=['POST'])
# # def rota_criar_pdf():
# #     """
# #     Passo 2: Recebe os dados editados da página de revisão e gera o PDF final.
# #     """
# #     # (Esta função não muda por agora, mas na Aula 17 ela também receberá a planta)
# #     print("PASSO 2: Recebidos dados editados para gerar PDF final...")
# #     proposta_final = {}
# #     proposta_final['nome_cliente'] = request.form.get('nome_cliente')
# #     proposta_final['analise_projeto'] = request.form.get('analise_projeto')
# #     itens = []
# #     valor_total_calculado = 0
# #     produtos = request.form.getlist('produto')
# #     quantidades = request.form.getlist('quantidade')
# #     precos = request.form.getlist('preco_unitario')
    
# #     for i in range(len(produtos)):
# #         try:
# #             quantidade = int(quantidades[i])
# #             preco = float(precos[i])
# #             subtotal = quantidade * preco
            
# #             itens.append({
# #                 "produto": produtos[i],
# #                 "quantidade": quantidade,
# #                 "preco_unitario": preco,
# #                 "subtotal": subtotal
# #             })
# #             valor_total_calculado += subtotal
# #         except (ValueError, IndexError):
# #             continue
            
# #     proposta_final['itens_proposta'] = itens
# #     proposta_final['valor_total'] = valor_total_calculado

# #     pdf_bytes = gerar_pdf_proposta(proposta_final, proposta_final['nome_cliente'])
# #     if not pdf_bytes:
# #         return "Erro: Não foi possível gerar o arquivo PDF final.", 500
        
# #     print(f"✅ PDF final para '{proposta_final['nome_cliente']}' gerado com sucesso! Enviando...")
# #     nome_arquivo = f"proposta_{proposta_final['nome_cliente'].replace(' ', '_').lower()}.pdf"
    
# #     return send_file(
# #         io.BytesIO(pdf_bytes),
# #         mimetype='application/pdf',
# #         as_attachment=True,
# #         download_name=nome_arquivo
# #     )

# # if __name__ == '__main__':
# #     app.run(debug=True)

# # Importações necessárias do Flask
# from flask import Flask, render_template, request, send_file
# import os
# import io
# from werkzeug.utils import secure_filename # <-- Nova importação para segurança de ficheiros

# # Nossas importações para IA, planilhas e PDF
# import gspread
# import json
# import openai
# from dotenv import load_dotenv
# from fpdf import FPDF

# # Cria a nossa aplicação web
# app = Flask(__name__)

# # --- CONFIGURAÇÃO DO UPLOAD ---
# # Define a pasta onde os uploads serão guardados
# UPLOAD_FOLDER = os.path.join('static', 'uploads')
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# # Garante que a pasta de uploads existe
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# # --- FUNÇÕES DO BACKEND ---

# def buscar_catalogo_da_planilha():
#     """Se conecta à planilha do Google e retorna os produtos."""
#     try:
#         gc = gspread.service_account(filename='credentials.json')
#         planilha = gc.open("dados-agente") 
#         aba = planilha.sheet1
#         produtos = aba.get_all_records()
#         print("✅ Catálogo de produtos carregado da planilha.")
#         return produtos
#     except Exception as e:
#         print(f"❌ Erro ao carregar catálogo: {e}")
#         return None

# def gerar_proposta_ia(pedido_tecnico: str, catalogo_produtos: list) -> dict:
#     """Gera a proposta usando a IA da OpenAI (GPT-4o), focada em texto."""
#     print("🤖 Iniciando a geração da proposta com o cérebro OpenAI...")
#     try:
#         load_dotenv()
#         api_key = os.getenv("OPENAI_API_KEY")
#         if not api_key:
#             print("❌ Chave de API da OpenAI não encontrada.")
#             return None
        
#         client = openai.OpenAI(api_key=api_key)
#         system_message = """
#         Você é um projetista sênior de sistemas de sonorização ambiente. Sua tarefa é criar uma proposta técnica e comercial detalhada com base na descrição fornecida.

#         **Regras Estritas:**
#         1.  **Análise do Pedido:** Analise a descrição do projeto, incluindo medidas, tipo de teto, e desejos do cliente.
#         2.  **Seleção de Produtos:** Utilize estritamente os produtos do catálogo JSON fornecido. Use o nome exato do produto do catálogo, não o código.
#         3.  **Formato da Resposta:** Sua resposta final DEVE SER APENAS um objeto JSON válido, sem texto adicional ou markdown. A estrutura do JSON deve ser exatamente esta:
#             {
#                 "analise_projeto": "Um parágrafo explicando suas escolhas técnicas com base na descrição fornecida.",
#                 "itens_proposta": [
#                     {
#                         "produto": "Nome Exato do Produto do Catálogo",
#                         "quantidade": 0,
#                         "preco_unitario": 0.0,
#                         "subtotal": 0.0
#                     }
#                 ],
#                 "valor_total": 0.0
#             }
#         """
#         user_content = f"""
#         Base de Conhecimento (Catálogo de Produtos):
#         ```json
#         {json.dumps(catalogo_produtos, indent=2, ensure_ascii=False)}
#         ```

#         Pedido do Técnico:
#         "{pedido_tecnico}"
#         """

#         print("🧠 Conectando ao GPT-4o...")
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": user_content}
#             ],
#             response_format={"type": "json_object"}
#         )
        
#         print("💡 Resposta recebida da IA!")
        
#         if response.choices and response.choices[0].message and response.choices[0].message.content:
#             proposta_texto = response.choices[0].message.content
#             proposta_json = json.loads(proposta_texto)
#             return proposta_json
#         else:
#             print("❌ A IA retornou uma resposta vazia.")
#             return None

#     except Exception as e:
#         print(f"❌ Erro na chamada da IA (OpenAI): {e}")
#         return None

# def gerar_pdf_proposta(proposta: dict, nome_cliente: str) -> bytes:
#     """Gera o PDF com a proposta final (uma única página)."""
#     try:
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Arial", "B", 16)
#         pdf.cell(0, 10, "Proposta de Sonorização Ambiente", 0, 1, "C")
#         pdf.set_font("Arial", "", 12)
#         pdf.cell(0, 10, f"Cliente: {nome_cliente}", 0, 1, "C")
#         pdf.ln(10)
#         pdf.set_font("Arial", "B", 12)
#         pdf.cell(0, 10, "Análise do Projeto", 0, 1)
#         pdf.set_font("Arial", "", 12)
#         pdf.multi_cell(0, 5, str(proposta.get('analise_projeto', 'Nenhuma análise fornecida.')))
#         pdf.ln(10)
#         pdf.set_font("Arial", "B", 12)
#         pdf.cell(100, 10, "Produto", 1, 0, "C")
#         pdf.cell(20, 10, "Qtd", 1, 0, "C")
#         pdf.cell(35, 10, "Preço Unit.", 1, 0, "C")
#         pdf.cell(35, 10, "Subtotal", 1, 1, "C")
#         pdf.set_font("Arial", "", 10)
#         for item in proposta.get('itens_proposta', []):
#             produto = str(item.get('produto', 'N/A'))
#             quantidade = str(item.get('quantidade', 0))
#             preco_unit = f"R$ {item.get('preco_unitario', 0.0):.2f}"
#             subtotal = f"R$ {item.get('subtotal', 0.0):.2f}"
#             pdf.cell(100, 10, produto, 1, 0)
#             pdf.cell(20, 10, quantidade, 1, 0, "C")
#             pdf.cell(35, 10, preco_unit, 1, 0, "R")
#             pdf.cell(35, 10, subtotal, 1, 1, "R")
#         pdf.set_font("Arial", "B", 12)
#         pdf.cell(155, 10, "VALOR TOTAL DO PROJETO", 1, 0)
#         pdf.cell(35, 10, f"R$ {proposta.get('valor_total', 0.0):.2f}", 1, 1, "R")

#         return pdf.output()
#     except Exception as e:
#         print(f"❌ Erro ao gerar PDF: {e}")
#         return None

# # --- ROTAS DA APLICAÇÃO WEB ---

# @app.route('/')
# def homepage():
#     """Renderiza a página inicial com o formulário."""
#     return render_template('index.html')

# @app.route('/gerar_proposta', methods=['POST'])
# def rota_gerar_proposta():
#     """
#     Passo 1: Recebe o pedido, GUARDA A IMAGEM, chama a IA e exibe a página de revisão.
#     """
#     print("PASSO 1: Recebida requisição inicial...")
#     nome_cliente = request.form['nome_cliente']
#     pedido_tecnico = request.form['pedido_tecnico']
#     planta_url = None # Começamos sem URL

#     # --- LÓGICA DE UPLOAD DA IMAGEM ---
#     if 'planta_imagem' in request.files:
#         ficheiro_planta = request.files['planta_imagem']
        
#         # Verifica se o utilizador realmente selecionou um ficheiro
#         if ficheiro_planta.filename != '':
#             # Limpa o nome do ficheiro para segurança
#             filename = secure_filename(ficheiro_planta.filename)
#             # Cria o caminho completo para guardar o ficheiro
#             caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             # Guarda o ficheiro no nosso servidor
#             ficheiro_planta.save(caminho_completo)
            
#             # Criamos o URL que o HTML pode usar para encontrar a imagem
#             planta_url = f"/static/uploads/{filename}"
#             print(f"🖼️ Imagem da planta guardada em: {caminho_completo}")
    
#     # --- LÓGICA DA IA (não mudou) ---
#     catalogo = buscar_catalogo_da_planilha()
#     if not catalogo:
#         return "Erro: Não foi possível carregar o catálogo de produtos da planilha.", 500

#     proposta_sugerida = gerar_proposta_ia(pedido_tecnico, catalogo)
#     if not proposta_sugerida:
#         return "Erro: A IA não conseguiu gerar uma proposta. Tente novamente.", 500
    
#     # --- ENVIA TUDO PARA A PÁGINA DE REVISÃO ---
#     print("✅ Proposta da IA recebida. A exibir página de revisão com a planta...")
#     return render_template('review.html', 
#                            nome_cliente=nome_cliente, 
#                            proposta=proposta_sugerida, 
#                            catalogo_completo=catalogo,
#                            planta_url=planta_url) # <-- A nova informação que estamos a enviar!

# @app.route('/criar_pdf', methods=['POST'])
# def rota_criar_pdf():
#     """
#     Passo 2: Recebe os dados editados da página de revisão e gera o PDF final.
#     """
#     # (Esta função não muda por agora, mas na Aula 17 ela também receberá a planta)
#     print("PASSO 2: Recebidos dados editados para gerar PDF final...")
#     proposta_final = {}
#     proposta_final['nome_cliente'] = request.form.get('nome_cliente')
#     proposta_final['analise_projeto'] = request.form.get('analise_projeto')
#     itens = []
#     valor_total_calculado = 0
#     produtos = request.form.getlist('produto')
#     quantidades = request.form.getlist('quantidade')
#     precos = request.form.getlist('preco_unitario')
    
#     for i in range(len(produtos)):
#         try:
#             quantidade = int(quantidades[i])
#             preco = float(precos[i])
#             subtotal = quantidade * preco
            
#             itens.append({
#                 "produto": produtos[i],
#                 "quantidade": quantidade,
#                 "preco_unitario": preco,
#                 "subtotal": subtotal
#             })
#             valor_total_calculado += subtotal
#         except (ValueError, IndexError):
#             continue
            
#     proposta_final['itens_proposta'] = itens
#     proposta_final['valor_total'] = valor_total_calculado

#     pdf_bytes = gerar_pdf_proposta(proposta_final, proposta_final['nome_cliente'])
#     if not pdf_bytes:
#         return "Erro: Não foi possível gerar o arquivo PDF final.", 500
        
#     print(f"✅ PDF final para '{proposta_final['nome_cliente']}' gerado com sucesso! Enviando...")
#     nome_arquivo = f"proposta_{proposta_final['nome_cliente'].replace(' ', '_').lower()}.pdf"
    
#     return send_file(
#         io.BytesIO(pdf_bytes),
#         mimetype='application/pdf',
#         as_attachment=True,
#         download_name=nome_arquivo
#     )

# if __name__ == '__main__':
#     app.run(debug=True)

# Importações necessárias do Flask
from flask import Flask, render_template, request, send_file, url_for
import os
import io
import uuid # Para gerar nomes de ficheiro únicos
from werkzeug.utils import secure_filename # Para segurança no nome do ficheiro
import base64 # Para descodificar a imagem desenhada

# Nossas importações para IA, planilhas e PDF
import gspread
import json
import openai
from dotenv import load_dotenv
from fpdf import FPDF
from PIL import Image

# Cria a nossa aplicação web
app = Flask(__name__)

# --- Configurações ---
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Funções Auxiliares ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- FUNÇÕES DO BACKEND (buscar_catalogo, gerar_proposta_ia) ---
# (Estas duas funções continuam as mesmas da versão anterior)

def buscar_catalogo_da_planilha():
    """Se conecta à planilha do Google e retorna os produtos."""
    try:
        gc = gspread.service_account(filename='credentials.json')
        planilha = gc.open("dados-agente") 
        aba = planilha.sheet1
        produtos = aba.get_all_records()
        print("✅ Catálogo de produtos carregado da planilha.")
        return produtos
    except Exception as e:
        print(f"❌ Erro ao carregar catálogo: {e}")
        return None

def gerar_proposta_ia(pedido_tecnico: str, catalogo_produtos: list) -> dict:
    """Gera a proposta usando a IA da OpenAI (GPT-4o), focada em texto."""
    print("🤖 Iniciando a geração da proposta com o cérebro OpenAI...")
    try:
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ Chave de API da OpenAI não encontrada.")
            return None
        
        client = openai.OpenAI(api_key=api_key)
        system_message = """
        Você é um projetista sênior de sistemas de sonorização ambiente. Sua tarefa é criar uma proposta técnica e comercial detalhada com base na descrição fornecida.
        **Regras Estritas:**
        1.  **Análise do Pedido:** Analise a descrição do projeto, incluindo medidas, tipo de teto, e desejos do cliente.
        2.  **Seleção de Produtos:** Utilize estritamente os produtos do catálogo JSON fornecido. Use o nome exato do produto do catálogo, não o código.
        3.  **Formato da Resposta:** Sua resposta final DEVE SER APENAS um objeto JSON válido, sem texto adicional ou markdown. A estrutura do JSON deve ser exatamente esta:
            {
                "analise_projeto": "Um parágrafo explicando suas escolhas técnicas com base na descrição fornecida.",
                "itens_proposta": [
                    {
                        "produto": "Nome Exato do Produto do Catálogo",
                        "quantidade": 0,
                        "preco_unitario": 0.0,
                        "subtotal": 0.0
                    }
                ],
                "valor_total": 0.0
            }
        """
        user_content = f"""
        Base de Conhecimento (Catálogo de Produtos):
        ```json
        {json.dumps(catalogo_produtos, indent=2, ensure_ascii=False)}
        ```
        Pedido do Técnico:
        "{pedido_tecnico}"
        """
        print("🧠 Conectando ao GPT-4o...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
        print("💡 Resposta recebida da IA!")
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            proposta_texto = response.choices[0].message.content
            proposta_json = json.loads(proposta_texto)
            return proposta_json
        else:
            print("❌ A IA retornou uma resposta vazia.")
            return None
    except Exception as e:
        print(f"❌ Erro na chamada da IA (OpenAI): {e}")
        return None

# ### FUNÇÃO ATUALIZADA ###: Agora aceita a imagem desenhada
def gerar_pdf_proposta(proposta: dict, nome_cliente: str, imagem_desenhada_bytes: bytes = None) -> bytes:
    """Gera o PDF com a proposta (pág 1) e a planta desenhada (pág 2)."""
    try:
        pdf = FPDF()
        
        # --- Página 1: A Proposta ---
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Proposta de Sonorização Ambiente", 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Cliente: {nome_cliente}", 0, 1, "C")
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Análise do Projeto", 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 5, str(proposta.get('analise_projeto', 'Nenhuma análise fornecida.')))
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(100, 10, "Produto", 1, 0, "C")
        pdf.cell(20, 10, "Qtd", 1, 0, "C")
        pdf.cell(35, 10, "Preço Unit.", 1, 0, "C")
        pdf.cell(35, 10, "Subtotal", 1, 1, "C")
        pdf.set_font("Arial", "", 10)
        for item in proposta.get('itens_proposta', []):
            produto = str(item.get('produto', 'N/A'))
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

        # --- Página 2: A Planta Desenhada ---
        if imagem_desenhada_bytes:
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Planta do Ambiente com Posicionamento", 0, 1, "C")
            pdf.ln(10)
            
            try:
                # O FPDF pode ler a imagem diretamente dos bytes em memória
                pdf.image(io.BytesIO(imagem_desenhada_bytes), x=10, y=30, w=190, type='PNG')
            except Exception as e:
                print(f"⚠️ Erro ao adicionar imagem ao PDF: {e}")
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 10, "Ocorreu um erro ao processar a imagem da planta desenhada.", 0, 1)

        return pdf.output()
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return None

# --- ROTAS DA APLICAÇÃO WEB ---

@app.route('/')
def homepage():
    """Renderiza a página inicial com o formulário."""
    return render_template('index.html')

@app.route('/gerar_proposta', methods=['POST'])
def rota_gerar_proposta():
    """
    PASSO 1: Recebe pedido e imagem, guarda a imagem, chama a IA (só com texto)
    e exibe a página de revisão, passando o URL da imagem.
    """
    print("PASSO 1: Recebida requisição inicial...")
    nome_cliente = request.form['nome_cliente']
    pedido_tecnico = request.form['pedido_tecnico']
    imagem_planta_url = None

    if 'planta_imagem' in request.files:
        ficheiro = request.files['planta_imagem']
        if ficheiro and ficheiro.filename != '' and allowed_file(ficheiro.filename):
            try:
                extensao = ficheiro.filename.rsplit('.', 1)[1].lower()
                nome_seguro = secure_filename(f"{uuid.uuid4()}.{extensao}")
                caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
                
                imagem = Image.open(ficheiro.stream)
                imagem.save(caminho_salvar)
                
                imagem_planta_url = url_for('static', filename=f'uploads/{nome_seguro}')
                print(f"🖼️ Imagem da planta guardada em: {caminho_salvar}")
            except Exception as e:
                print(f"⚠️ Erro ao processar ou guardar a imagem: {e}")
                
    catalogo = buscar_catalogo_da_planilha()
    if not catalogo:
        return "Erro: Não foi possível carregar o catálogo.", 500

    proposta_sugerida = gerar_proposta_ia(pedido_tecnico, catalogo)
    if not proposta_sugerida:
        return "Erro: A IA não conseguiu gerar uma proposta.", 500
    
    print("✅ Proposta da IA recebida. A exibir página de revisão...")
    return render_template('review.html', 
                           nome_cliente=nome_cliente, 
                           proposta=proposta_sugerida, 
                           catalogo_completo=catalogo,
                           imagem_planta_url=imagem_planta_url)


# ### ROTA ATUALIZADA ###: Agora recebe a imagem desenhada
@app.route('/criar_pdf', methods=['POST'])
def rota_criar_pdf():
    """
    Passo 2: Recebe os dados editados E a imagem desenhada, e gera o PDF final.
    """
    print("PASSO 2: Recebidos dados editados para gerar PDF final...")
    proposta_final = {}
    proposta_final['nome_cliente'] = request.form.get('nome_cliente')
    proposta_final['analise_projeto'] = request.form.get('analise_projeto')
    itens = []
    valor_total_calculado = 0
    produtos = request.form.getlist('produto')
    quantidades = request.form.getlist('quantidade')
    precos = request.form.getlist('preco_unitario')
    
    for i in range(len(produtos)):
        try:
            quantidade = int(quantidades[i])
            preco = float(precos[i])
            subtotal = quantidade * preco
            
            itens.append({
                "produto": produtos[i],
                "quantidade": quantidade,
                "preco_unitario": preco,
                "subtotal": subtotal
            })
            valor_total_calculado += subtotal
        except (ValueError, IndexError):
            continue
            
    proposta_final['itens_proposta'] = itens
    proposta_final['valor_total'] = valor_total_calculado

    # --- LÓGICA PARA RECEBER A IMAGEM DESENHADA ---
    imagem_desenhada_bytes = None
    imagem_base64 = request.form.get('imagem_desenhada')
    
    if imagem_base64:
        try:
            # A imagem vem como "data:image/png;base64,..."
            # Precisamos de remover o cabeçalho antes de descodificar
            dados_imagem = imagem_base64.split(',')[1]
            imagem_desenhada_bytes = base64.b64decode(dados_imagem)
            print("🖼️ Imagem desenhada recebida e descodificada com sucesso.")
        except Exception as e:
            print(f"⚠️ Erro ao descodificar a imagem desenhada: {e}")

    # Passamos os bytes da imagem (ou None) para a função de gerar o PDF
    pdf_bytes = gerar_pdf_proposta(proposta_final, proposta_final['nome_cliente'], imagem_desenhada_bytes) 
    if not pdf_bytes:
        return "Erro: Não foi possível gerar o arquivo PDF final.", 500
        
    print(f"✅ PDF final para '{proposta_final['nome_cliente']}' gerado com sucesso! Enviando...")
    nome_arquivo = f"proposta_{proposta_final['nome_cliente'].replace(' ', '_').lower()}.pdf"
    
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nome_arquivo
    )

if __name__ == '__main__':
    app.run(debug=True)

