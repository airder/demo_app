from django.shortcuts import render, redirect
from .forms import InputForm
from .models import Customer
from sklearn.externals import joblib
import numpy as np

# モデルの呼び出しはグローバル変数のところで書くことがベター
loaded_model = joblib.load('/home/airder/airder.pythonanywhere.com/demo_app/demo_model.pkl')

def index(request):
    return render(request, 'demo_app/index.html', {})
    # {}はhtml側に渡す変数

def input_form(request):
    if request.method == "POST":
        form = InputForm(request.POST)
        if form.is_valid(): #有効な値が入力されていれれば
            form.save() #入力値を保存
            return redirect('result') #そしてresult.htmlへ遷移する
    else:
        form = InputForm()
        return render(request, 'demo_app/input_form.html', {'form':form})

def result(request):
    #DBからデータを取得
    _data = Customer.objects.order_by('id').reverse().values_list\
    ('limit_balance', 'gender', 'education', 'marriage', 'age', 'pay_0', 'pay_2', 'pay_3', 'pay_4', 'pay_5', 'pay_6', 'bill_amt_1', 'pay_amt_1', 'pay_amt_2', 'pay_amt_3', 'pay_amt_4', 'pay_amt_5', 'pay_amt_6')
    x = np.array([_data[0]]) #行列にするために[]で囲ってあげる
    #print(x) #コマンドプロンプト上での確認用
    #print(type(x)) #コマンドプロンプト上での確認用
    #print(x.shape) #コマンドプロンプト上での確認用

    # 推論
    y = loaded_model.predict(x)
    y_proba = loaded_model.predict_proba(x)
    _y_proba = y_proba*100
    # print(y) #コマンドプロンプト上での確認用
    # print(y_proba) #コマンドプロンプト上での確認用

    # yとy_probaの結果に基づくコメントの設定
    if y[0] ==0:
        if y_proba[0][y[0]] > 0.75:
            comment = '高い確率での負け組'
        else:
            comment = '低い確率での負け組'
    else:
        if y_proba[0][y[0]] > 0.75:
            comment = '高い確率での勝ち組'
        else:
            comment = '低い確率での勝ち組'

    # 推論結果の保存
    customer = Customer.objects.order_by('id').reverse()[0]
    customer.result = y[0]
    customer.proba = _y_proba[0][y[0]]
    customer.comment = comment
    customer.save()

    return render(request, 'demo_app/result.html', {'y':y[0], 'y_proba':round(_y_proba[0][y[0]], 2), 'comment':comment})

def history(request):
    if request.method == 'POST':
        d_id = request.POST
        d_customer = Customer.objects.filter(id =d_id['d_id'])
        d_customer.delete()
        customers = Customer.objects.all()
        return render(request, 'demo_app/history.html', {'customers':customers})
    else:
        customers = Customer.objects.all()
        return render(request, 'demo_app/history.html', {'customers':customers})
