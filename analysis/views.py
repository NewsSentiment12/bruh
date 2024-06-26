from django.shortcuts import render
import pandas as pd

def sentiment_view(request):
    df = pd.read_csv('../data/sentiments.csv')
    context = {'data': df.to_dict(orient='records')}
    return render(request, 'analysis/sentiment.html', context)
