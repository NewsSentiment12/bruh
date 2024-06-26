const fs = require('fs');
const puppeteer = require('puppeteer');
const Sentiment = require('sentiment');
const sentiment = new Sentiment();

const scrapeArticles = async (query, numResults) => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  const rssUrl = `https://news.google.com/rss/search?q=${query.replace(" ", "%20")}`;

  await page.goto(rssUrl);
  const links = await page.$$eval('item link', links => links.map(link => link.textContent).slice(0, numResults));

  let articles = [];
  for (let link of links) {
    await page.goto(link);
    let text = await page.$eval('*', el => el.innerText);
    articles.push({ url: link, text: text });
  }

  await browser.close();
  return articles;
};

const main = async () => {
  const searchParams = JSON.parse(fs.readFileSync('search_params.json', 'utf8'));
  const articles = await scrapeArticles(searchParams.query, searchParams.num_results);

  fs.writeFileSync('articles.json', JSON.stringify(articles, null, 2));

  let sentimentResults = articles.map(article => {
    let result = sentiment.analyze(article.text);
    return {
      url: article.url,
      polarity: result.score,
      subjectivity: result.comparative
    };
  });

  fs.writeFileSync('sentiment_results.json', JSON.stringify(sentimentResults, null, 2));
};

main();
