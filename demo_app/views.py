from django.shortcuts import render

def index(request):
    return render(request, 'demo_app/index.html', {})
    # {}はhtml側に渡す変数
