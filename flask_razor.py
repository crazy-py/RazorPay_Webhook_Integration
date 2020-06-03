import hmac
import json
import hashlib
import razorpay
import requests
from flask import Flask ,request, json, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class WebhookHmac(Resource):

    def get(self):
        return {"Hello":"RazorPay Hmac Method"}

    def post(self):
        event_list = []
        webhook_event_id = request.headers['X-Razorpay-Event-Id']
        webhook_signature = request.headers['X-Razorpay-Signature']
        webhook_key = 'lead@123'
        raw_body = request.get_data()
        data_body = json.dumps(request.json , separators=(',',':')) #Returns String
        data = json.loads(data_body)

        dig = hmac.new(key=bytes(webhook_key ,'utf-8'), #Converting Into Bytes
                    msg=raw_body, #Already in Bytes
                    digestmod=hashlib.sha256)

        generated_signature = dig.hexdigest()
        
        if (generated_signature == webhook_signature and webhook_event_id not in event_list):
            payload = data['payload']
            group_id = "*********" #Your Creds
            api_key = "********"

            if(payload['payment']['entity']['notes']['full_name']):
                name =  payload['payment']['entity']['notes']['full_name']
            else:
                name = " "
            if(payload['payment']['entity']['notes']['phone']):
                phone = payload['payment']['entity']['notes']['phone']
            else:
                phone = " "
            if(payload['payment']['entity']['notes']['email']):
                email = payload['payment']['entity']['notes']['email']
            else:
                email = " "

            if(payload['payment']['entity']['notes']['source']):
                url = "https://api.mailerlite.com/api/v2/groups/{0}/subscribers".format(group_id)
                
                data = {
                        'name'   : name,
                        'email'  : email,
                        'fields' : {'phone': phone}
                    }

                payload = json.dumps(data)

                headers = {
                    'content-type': "application/json",
                    'x-mailerlite-apikey': api_key
                }

                response = requests.request("POST", url, data=payload, headers=headers)
                print(response.text)
                event_list = event_list.append(webhook_event_id)
                return '',200
            else:
                return '',200

class WebhookSdk(Resource):
    '''
    Using RazorPay SDK 
    Required : RazorPay Key , RazorPay Secret , Webhook Secret
    '''
    def get(self):
        return {'hello': 'world'}

    def post(self):
        webhook_signature = request.headers['X-Razorpay-Signature']
        webhook_secret = 'XXXXXXX' 
        webhook_body = str(request.get_data())

        client = razorpay.Client(auth=("<YOUR_KEY_ID>", "<YOUR_KEY_SECRET>"))
        client.utility.verify_webhook_signature(webhook_body, webhook_signature, webhook_secret)
        print(webhook_body)
        return '', 200

api.add_resource(WebhookHmac, '/webhook-razorpay')
api.add_resource(WebhookSdk, '/webhook-sdk')


if __name__ == '__main__':
    app.run(debug=True)