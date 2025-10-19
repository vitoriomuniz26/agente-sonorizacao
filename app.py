# # Importações necessárias do Flask
# from flask import Flask, render_template, request, send_file
# import os
# import io

# # Nossas importações para IA, planilhas e PDF
# import gspread
# import json
# import openai
# from dotenv import load_dotenv
# from fpdf import FPDF

# # Cria a nossa aplicação web
# app = Flask(__name__)

# # --- FUNÇÕES DO BACKEND ---

# def buscar_catalogo_da_planilha():
#     """Se conecta à planilha do Google e retorna os produtos."""
#     try:
#         gc = gspread.service_account(filename='credentials.json')
#         # ATENÇÃO: Verifique se "dados-agente" é o nome exato da sua planilha
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
#             print("❌ Chave de API da OpenAI não encontrada no ficheiro .env")
#             return None
        
#         client = openai.OpenAI(api_key=api_key)

#         # O "manual de instruções" para a IA
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

#         # Prepara o conteúdo a ser enviado para a IA
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
#     """Gera o PDF com a proposta (uma única página)."""
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
#     """Recebe os dados do formulário, processa tudo e retorna o PDF."""
#     print("Recebida requisição para gerar proposta...")
#     nome_cliente = request.form['nome_cliente']
#     pedido_tecnico = request.form['pedido_tecnico']
            
#     catalogo = buscar_catalogo_da_planilha()
#     if not catalogo:
#         return "Erro: Não foi possível carregar o catálogo de produtos da planilha.", 500

#     proposta_ia = gerar_proposta_ia(pedido_tecnico, catalogo)
#     if not proposta_ia:
#         return "Erro: A IA não conseguiu gerar uma proposta. Verifique o terminal para mais detalhes.", 500
    
#     pdf_bytes = gerar_pdf_proposta(proposta_ia, nome_cliente)
#     if not pdf_bytes:
#         return "Erro: Não foi possível gerar o arquivo PDF.", 500
        
#     print(f"✅ Proposta para '{nome_cliente}' gerada com sucesso! Enviando PDF...")
#     nome_arquivo = f"proposta_{nome_cliente.replace(' ', '_').lower()}.pdf"
#     return send_file(
#         io.BytesIO(pdf_bytes),
#         mimetype='application/pdf',
#         as_attachment=True,
#         download_name=nome_arquivo
#     )

# if __name__ == '__main__':
#     app.run(debug=True)

# Importações necessárias do Flask
from flask import Flask, render_template, request, send_file
import os
import io

# Nossas importações para IA, planilhas e PDF
import gspread
import json
import openai
from dotenv import load_dotenv
from fpdf import FPDF

# Cria a nossa aplicação web
app = Flask(__name__)

# --- FUNÇÕES DO BACKEND ---

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
                # ### CORREÇÃO ###: Adicionámos as aspas em 'content'
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

def gerar_pdf_proposta(proposta: dict, nome_cliente: str) -> bytes:
    """Gera o PDF com a proposta final (uma única página)."""
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
    """Passo 1: Recebe o pedido inicial, chama a IA e exibe a página de revisão."""
    print("PASSO 1: Recebida requisição inicial...")
    nome_cliente = request.form['nome_cliente']
    pedido_tecnico = request.form['pedido_tecnico']
            
    catalogo = buscar_catalogo_da_planilha()
    if not catalogo:
        return "Erro: Não foi possível carregar o catálogo de produtos da planilha.", 500

    proposta_sugerida = gerar_proposta_ia(pedido_tecnico, catalogo)
    if not proposta_sugerida:
        return "Erro: A IA não conseguiu gerar uma proposta. Tente novamente.", 500
    
    print("✅ Proposta da IA recebida. A exibir página de revisão...")
    return render_template('review.html', 
                           nome_cliente=nome_cliente, 
                           proposta=proposta_sugerida, 
                           catalogo_completo=catalogo)

@app.route('/criar_pdf', methods=['POST'])
def rota_criar_pdf():
    """Passo 2: Recebe os dados editados da página de revisão e gera o PDF final."""
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

    pdf_bytes = gerar_pdf_proposta(proposta_final, proposta_final['nome_cliente'])
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