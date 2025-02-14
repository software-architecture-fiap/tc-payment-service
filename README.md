# Payment Service

O **Payment Service** é um dos componentes do sistema de lanchonete desenvolvido com FastAPI. Ele lida com a integração de pagamentos, utilizando o MercadoPago para gerar QR codes e registrar os pagamentos. Este serviço utiliza **MongoDB** para armazenar dados relacionados a transações.

## Tecnologias Utilizadas

- **FastAPI**: Framework para desenvolvimento de APIs.
- **MongoDB**: Banco de dados NoSQL utilizado para armazenar dados de transações.
- **pymongo**: Driver Python para interação com MongoDB.
- **MercadoPago SDK**: Para integração com o sistema de pagamentos MercadoPago.
- **Poetry**: Gerenciador de dependências e ambiente virtual.

## Instalação

1. Clone o repositório:

   ```bash
   git clone <URL do repositório>
   cd payment-service
   ```

2. Crie um ambiente virtual e ative-o:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Para sistemas Unix
   venv\Scripts\activate     # Para Windows
   ```

3. Instale as dependências usando o Poetry:

   ```bash
   poetry install
   ```

## Configuração

1. **MongoDB**: Certifique-se de ter uma instância do MongoDB em funcionamento. A configuração de conexão com o banco de dados pode ser feita através das variáveis de ambiente ou diretamente no arquivo de configuração.

2. **MercadoPago**: Configure sua conta MercadoPago e adicione as credenciais (como `ACCESS_TOKEN`) nas variáveis de ambiente ou no arquivo de configuração.

## Endpoints

- **POST /payment**: Registra um novo pagamento, utilizando o MercadoPago para gerar o QR code.

    - **Body**:

      ```json
      {
        "amount": 100.0,
        "customer_id": "123456"
      }
      ```

    - **Response**:

      ```json
      {
        "payment_id": "78910",
        "qr_code_url": "<MercadoPago QR Code URL>"
      }
      ```

- **GET /payment/{payment_id}**: Consulta o status de um pagamento.

    - **Response**:

      ```json
      {
        "payment_id": "78910",
        "status": "approved",
        "amount": 100.0
      }
      ```

## Como Contribuir

1. Fork o repositório.
2. Crie uma branch para sua feature (`git checkout -b minha-feature`).
3. Faça commit das suas mudanças (`git commit -am 'Adiciona nova feature'`).
4. Faça push para a branch (`git push origin minha-feature`).
5. Abra um Pull Request.

## Licença

Este projeto é licenciado sob a licença MIT - consulte o [LICENSE](LICENSE) para mais detalhes.
