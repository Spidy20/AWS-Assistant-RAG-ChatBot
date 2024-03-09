# AWS Assistant GPT-4 ChatBot with Chat-History with Langchain RAG + Lambda + API Gateway + PostgreSQL

### [Watch this tutorial►](https://youtu.be/e9XhPMmXI2Q)
<img src="https://github.com/Spidy20/AWS-Assistant-RAG-ChatBot/blob/master/yt_thumbnail.jpg">

- In this tutorial, we'll be creating a GPT-4 AWS Helper ChatBot utilizing Langchain, Lambda, API Gateway, and PostgreSQL PGVector hosted on an EC2 instance as our Vector database.

### Implementation Architecture
<img src="https://github.com/Spidy20/AWS-Assistant-RAG-ChatBot/blob/master/AWS-Assistant-ChatBot-Architecture.png">

### Used Services
- **AWS Lambda**: Responsible for managing API backend Object Detection processing.
- **AWS SAM**: Utilized for orchestrating AWS serverless services such as Lambda and API Gateway.
- **API Gateway**: Facilitates the creation of a public REST API.
- **AWS EC2**: Employed to host the PostgreSQL Vector database.

### Steps that we followed!
1. PostgreSQL PGVector EC2 Setup with host.
2. Data ingestion in PostgreSQL PGVector VectorDB.
3. AWS SAM setup in EC2 for deploying Lambda funtion with API Gateway. 
4. Deployment of Lambda application with SAM using EC2(Docker).
5. Testing API with Postman.
6. Chatbot Application Demo Streamlit App.

### Folder Structure of Repostiory
- `Lambda-App` is directory for SAM App for Lambda & API Gateway.
- `app.py` is `Streamlit` app for demo purpose.
- `DataIngestion.py` is used to ingest data in PostgreSQL PGVector DB.
- `connect.py` is used for checking connectivity with PostgreSQL DB hosted in EC2. 
- `aws_sample_qa.csv` is CSV sample data that we ingested in DB.
### Lambda SAM App Folder Structure
```
Lambda-SAM-App
│ -- template.yaml  - This is template that will create resources like Lambda, API Gateway in AWS account.
│
└───Backend
│   │ -- Lambda_Response_App.py -- Lambda Handler Code 
│   │ -- requirements.txt - To install depedencies in Lambda like Langchain, PyPDF, psycopg2, etc
│   └───
```
- This directory sturcture should be created in EC2 for deploying SAM App from EC2. 
### To setp AWS Credentials & docker
- To Download Docker in Ubuntu.
  ```
  apt install docker.io
  ```
- To install AWS CLI in Ubuntu.
  ```
  apt install awscli
  ```
- To setup credentials in AWS CLI.
  ```
  aws configure --profile <profile-name>
  ```
  This will prompt you to enter AWS Credentials. 
  
### SAM Build Commannds
- Sam Installation
  [Follow](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- SAM Build
  ```
  sam build --use-container -parallel
  ```
- SAM Deploy
  ```
  sam deploy --stack-name <stack-name> --region <region-name> --guided
  ```
  Once this is done successfully, you will see the Lambda function created in your selected region. From Lambda console, you can get rest API URL to invoke API. 

### Demo of ChatBot
<img src="https://github.com/Spidy20/AWS-Assistant-RAG-ChatBot/blob/master/Chatbot-demo.PNG">

### Give Star⭐ to this repository, and fork it to support me. 

### [Buy me a Coffee☕](https://www.buymeacoffee.com/spidy20)
### [Donate me on PayPal(It will inspire me to do more projects)](https://www.paypal.me/spidy1820)
