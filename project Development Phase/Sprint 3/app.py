
from flask import render_template,Flask,request
import numpy as np
import pickle
import requests

# # NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
# API_KEY = "QCFx9k6096PpFRR8lVJGTkcy-XFNT4pj1SlbTvglDMw7"
# token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
# mltoken = token_response.json()["access_token"]

# header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}





API_KEY = "QCFx9k6096PpFRR8lVJGTkcy-XFNT4pj1SlbTvglDMw7"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]


app= Flask(__name__, template_folder='Template')

scale = pickle.load(open('model.pkl','rb'))

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/predict.html')
def formpg():
    return render_template('predict.html')
@app.route('/submit',methods = ['POST'])
def predict():
    gender,married,depend,education,self_emp,applicant_income,co_income,loan_amount,loan_term,credit_history,property_area = [x for x in request.form.values()]
    if gender == 'Male':
        gender = 1
    else:
        gender = 0

    if married == 'Yes':
        married = 1
    else:
        married = 0

    if education == 'Graduate':
        education = 0
    else:
        education = 1

    if self_emp == 'Yes':
        self_emp = 1
    else:
        self_emp = 0

    if depend == '3+':
        depend = 3

    applicant_income = int(applicant_income)
    applicant_income = np.log(applicant_income)
    loan_amount = int(loan_amount)
    loan_amount = np.log(loan_amount)

    if credit_history == 'Yes':
        credit_history = 1
    else:
        credit_history = 0

    if property_area == 'Urban':
        property_area = 2

    elif property_area == 'Rural':
        property_area = 0
    else:
        property_area = 1

    features = [[gender,married,education,self_emp,applicant_income,co_income,loan_amount,loan_term,credit_history,property_area]]
    con_features = np.array(features)
    
    sf = con_features.tolist()
    
    payload_scoring = {"input_data": [{"fields": ['gender','married','education','self_emp','applicant_income','co_income','loan_amount','loan_term','credit_history','property_area'], "values": sf}]}

    response_scoring = requests.post('https://eu-de.ml.cloud.ibm.com/ml/v4/deployments/c5826276-fada-4224-8e4d-4bc5e2050b56/predictions?version=2022-11-18', json=payload_scoring,headers={'Authorization': 'Bearer ' + mltoken})
    prediction = response_scoring.json()

    print(prediction)
    predict = prediction['predictions'][0]['values'][0][0]

    
    
    #prediction = model.predict(scale_features)
    if predict == 0:
        return render_template('submit.html', prediction_text ='You are eligible for loan')
    else:
        return render_template('submit.html',prediction_text = 'Sorry you are not eligible for loan')


if __name__ == "__main__":
    app.run(debug=True)
