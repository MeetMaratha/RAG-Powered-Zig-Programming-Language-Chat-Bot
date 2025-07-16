from flask import Flask, Response, json, make_response, request
from flask_cors import CORS
from langchain_ollama import OllamaLLM

model: OllamaLLM = OllamaLLM(model="llama3.1")
# model: OllamaLLM = OllamaLLM(model="deepseek-r1")
app: Flask = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/get_inference", methods=["POST"])
def getInference() -> Response:
    request_data = request.json

    query: str = request_data["query"]
    context: str = request_data["context"]

    prompt: str = f"""<｜begin▁of▁sentence｜>Human:
    [INST] You are an expert AI assistant. Carefully analyze the provided context to answer the question.
    Your response must be:
    - Factual and precise
    - Based ONLY on the given context
    - In clear English paragraphs
    - With citations from context when possible [/INST]

    ### Context:
    {context}

    ### Question:
    {query}

    <｜begin▁of▁sentence｜>Assistant: """

    result = model.invoke(input=prompt)
    print(result)

    return make_response(json.dumps({"response": result}), 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
