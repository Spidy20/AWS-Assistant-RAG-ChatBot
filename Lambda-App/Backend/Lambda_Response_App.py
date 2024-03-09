import os
import boto3
import logging
from langchain.vectorstores.pgvector import PGVector
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import json
from datetime import datetime
import time
from langchain.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.memory import PostgresChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Reading Environment variables
host = os.environ.get('HOST', '--YOUR EC2 DB host--').strip()
database = os.environ.get('DATABASE', 'postgres').strip()
user = os.environ.get('USER', 'postgres').strip()
password = os.environ.get('PASSWORD', 'spidy20').strip()
collection_name = os.environ.get('COLLECTION_NAME', '----Collection Name---').strip()
openai_model_id = os.environ.get('OPENAI_MODEL_ID', 'gpt-4-1106-preview').strip()
model_temp = float(os.environ.get('MODEL_TEMP', '0.0'))
chat_hist_msg_count = int(os.environ.get('CHAT_HISTORY_MESSAGE_COUNT', '24').strip())
openai_key = os.environ.get('OPENAI_API_KEY', "----YOUR API KEY----").strip()

# Initialize BedrockEmbeddings and Bedrock
session = boto3.Session()
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(temperature=model_temp, model=openai_model_id, max_tokens=4096)

# Build the connection string
connection_string = PGVector.connection_string_from_db_params(
    driver="psycopg2",
    host=host,
    port=5432,
    database=database,
    user=user,
    password=password,
)

logger.info(f"The Connection String is: {connection_string}")


class ResponseAPI:
    def __init__(self, user_input, session_id):  # Setting default k=10
        self.user_input = user_input
        self.session_id = session_id

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def clean_response(self, response):
        cleaned_response = re.sub(r'\s+', ' ', response).strip()
        cleaned_response = re.sub(r'[^a-zA-Z0-9\s,.!]', '', cleaned_response)
        return cleaned_response

    def generate_response(self, ):
        try:
            # Init retriver
            # Init store
            store = PGVector(
                collection_name=collection_name,
                connection_string=connection_string,
                embedding_function=embeddings,
            )
            retriever = store.as_retriever(search_kwargs={"k": 20})

            # Reading prompt from S3
            qa_system_prompt = """
            As AWS Assistant Bot, your goal is to provide help related to AWS services, and it's questions which is asked by AWS professional. Follow these principles:
            
            When it's first conversation with user, always greetings them with "Hello Professional, as AWS Assistant Bot How may I assist you?"
            Understand user's answer then give answers from available database of question and answers. 
            If you don't know answer, just mention that "I don't know about this, please refer AWS Documentation."
            Make sure your answer should be correct grammar, point wise, and proper explained.
            Please generate properly formatted answer in markdown, and if it is new line or line gap in answer, please add double space then \n, so I can render that answer as markdown at my app.
    
            {context}
            """
            logger.info(f"Got the following prompt: \n {qa_system_prompt}")

            # Init connection with Postgres for storing chat history
            chat_history = PostgresChatMessageHistory(
                connection_string=f"postgresql://{user}:{password}@{host}:5432/{database}",
                session_id=self.session_id,
            )
            # Contextual prompt
            contextualize_q_system_prompt = """Given a chat history and the latest user question \
            which might reference context in the chat history, formulate a standalone question \
            which can be understood without the chat history. Do NOT answer the question, \
            just reformulate it if needed and otherwise return it as is."""
            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", contextualize_q_system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{question}"),
                ]
            )
            contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

            def contextualized_question(input: dict):
                if input.get("chat_history"):
                    return contextualize_q_chain
                else:
                    return input["question"]

            # RAG Chain
            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", qa_system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{question}"),
                ]
            )
            rag_chain = (
                    RunnablePassthrough.assign(
                        context=contextualized_question | retriever | self.format_docs
                    )
                    | qa_prompt
                    | llm
            )
            # Giving last 24 message (12 conv) in memory
            if len(chat_history.messages) <= chat_hist_msg_count:
                msgs = chat_history.messages
            else:
                msgs = chat_history.messages[-chat_hist_msg_count:]

            # Asking question to LLM
            ai_msg = rag_chain.invoke({"question": self.user_input, "chat_history": msgs})

            # response_ans = self.clean_response(ai_msg.content)
            chat_history.add_user_message(self.user_input)
            chat_history.add_ai_message(ai_msg.content)

            # return answer and prompt
            return ai_msg.content
        except Exception as e:
            logger.error(e)
            return e


def lambda_handler(event, context):
    try:
        # Check if 'body' is in the event
        if 'body' in event:
            # Print or log the event for debugging
            logger.info(f"Event details: {event}")
            # Check if the value associated with 'body' is not None and not an empty string
            headers = event['headers']
            if event['body'] is not None and event['body'].strip():
                user_input = str(event['body']).strip()
                if 'session_id' in headers:
                    session_id = headers['session_id'].lower()
                    # Generate response
                    start_time = time.time()
                    response_api = ResponseAPI(user_input, session_id=session_id)
                    response = response_api.generate_response()
                    end_time = time.time()
                    response_time = round(end_time - start_time, 2)
                    logger.info(f"Generated Response: {response}")

                    # Return success response
                    timestamps = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    response_dict = {"Status": "Success", "Query": user_input, "Response": response.strip()
                        , "Timestamp": timestamps,
                                     "ResponseTime": response_time}
                    return {
                        'statusCode': 200,
                        'body': json.dumps(response_dict)
                    }
                # Return failure response for session_id missing
                else:
                    response_dict = {"Status": "Failed", "Reason": 'Bad Request: session_id is missing from headers', "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    return {
                        'statusCode': 400,
                        'body': json.dumps(response_dict)
                    }
            else:
                # Return failure response for None or empty body
                timestamps = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                response_dict = {"Status": "Failed", "Reason": 'Bad Request: None or Empty Body',
                                 "Timestamp": timestamps}
                return {
                    'statusCode': 400,
                    'body': json.dumps(response_dict)
                }
        else:
            # Return failure response for missing 'body' key
            timestamps = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_dict = {"Status": "Failed", "Reason": 'Bad Request: Missing Body', "Timestamp": timestamps}
            return {
                'statusCode': 400,
                'body': json.dumps(response_dict)
            }

    except Exception as e:
        # Return error response
        logger.error(f"Error: {e}")
        timestamps = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response_dict = {"Status": "Error", "Reason": str(e), "Timestamp": timestamps}
        return {
            'statusCode': 500,
            'body': json.dumps(response_dict)
        }
