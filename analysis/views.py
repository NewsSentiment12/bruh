from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import subprocess
from django.conf import settings
import json
import os

@csrf_exempt
def sentiment_analysis(request):
    context = {}
    if request.method == 'POST':
        query = request.POST.get('query')
        num_results = int(request.POST.get('num_results', 5))
        
        # Save query and num_results to a JSON file
        search_params = {
            "query": query,
            "num_results": num_results
        }
        with open('search_params.json', 'w') as f:
            json.dump(search_params, f)
        
        # Run Node.js scraper script
        scraper_result = subprocess.run(['node', 'scraper/index.js'], capture_output=True, text=True)
        
        if scraper_result.returncode != 0:
            context['error'] = "Error in scraping articles."
            return render(request, 'analysis/sentiment.html', context)
        
        # Read the articles output by the scraper
        with open('articles.json', 'r') as f:
            articles = json.load(f)
        
        if not articles:
            context['error'] = "No articles found."
            return render(request, 'analysis/sentiment.html', context)
        
        # Perform sentiment analysis using the Python script
        sentiment_result = subprocess.run(['python', 'analysis/analyze.py'], capture_output=True, text=True)
        
        if sentiment_result.returncode != 0:
            context['error'] = "Error in sentiment analysis."
            return render(request, 'analysis/sentiment.html', context)
        
        # Read the sentiment analysis output
        with open('sentiment_results.json', 'r') as f:
            sentiment_data = json.load(f)
        
        context['articles'] = articles
        context['sentiment'] = sentiment_data
    
    return render(request, 'analysis/sentiment.html', context)
