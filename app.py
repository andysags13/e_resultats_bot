from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from result_fetcher import get_exam_results

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms_reply():
    msg = request.form.get('Body')
    resp = MessagingResponse()
    
    table_number = msg.strip()
    results = get_exam_results(table_number)
    
    if isinstance(results, list):
        result_text = ", ".join(results)
    else:
        result_text = results
    
    resp.message(result_text)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
