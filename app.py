from flask import Flask, render_template, request
import urllib.request
import json
import os
import ssl

app = Flask(__name__)

# ==========================================
# ⚠️ 請填入你的 Azure 資訊
# ==========================================
url = 'http://c6fd6834-9893-4f45-9107-d47edce5b687.eastasia.azurecontainer.io/score'
api_key = 'UzD9LIseaIgdWhiM6a72RVa050gapUu7' 
# ==========================================

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context
allowSelfSignedHttps(True)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    probability = None
    result_class = None
    error = None

    if request.method == 'POST':
        try:
            # 1. 只抓取網頁輸入的 3 個數值
            age = int(request.form.get('age', 0))
            monthly_income = int(request.form.get('MonthlyIncome', 0))
            dependents = int(request.form.get('NumberOfDependents', 0))
            
            # 第 4 個特徵我們直接設為 0 (不讓使用者填)
            real_estate = 0

            # 2. 組合 Azure 需要的完整 JSON
            data = {
                "Inputs": {
                    "input1": [
                        {
                            "Column1": 0,
                            "SeriousDlqin2yrs": 0,
                            "RevolvingUtilizationOfUnsecuredLines": 0,
                            "age": age,                                  # <--- 使用者輸入
                            "NumberOfTime30-59DaysPastDueNotWorse": 0,
                            "DebtRatio": 0,
                            "MonthlyIncome": monthly_income,             # <--- 使用者輸入
                            "NumberOfOpenCreditLinesAndLoans": 0,
                            "NumberOfTimes90DaysLate": 0,
                            "NumberRealEstateLoansOrLines": real_estate, # <--- 自動填 0
                            "NumberOfTime60-89DaysPastDueNotWorse": 0,
                            "NumberOfDependents": dependents             # <--- 使用者輸入
                        }
                    ]
                },
                "GlobalParameters": {}
            }

            # 3. 呼叫 Azure API
            body = str.encode(json.dumps(data))
            headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
            req = urllib.request.Request(url, body, headers)
            response = urllib.request.urlopen(req)
            result_json = json.loads(response.read())

            # 4. 解析結果
            prediction = result_json['Results']['output1'][0]
            scored_label = prediction.get('Scored Labels', 0)
            scored_prob = prediction.get('Scored Probabilities', 0)

            if scored_label == 1:
                result = "高風險 (High Risk)"
                result_class = "danger"
            else:
                result = "低風險 (Low Risk)"
                result_class = "success"
            
            probability = f"{float(scored_prob) * 100:.2f}%"

        except Exception as e:
            error = f"發生錯誤: {str(e)}"

    # 回傳給 form.html
    return render_template('form.html', result=result, probability=probability, result_class=result_class, error=error)

if __name__ == '__main__':
    app.run(debug=True)
