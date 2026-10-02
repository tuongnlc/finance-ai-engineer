from newspaper import Article

url = "https://www.vietnam.vn/gia-vang-hom-nay-2-10-2026-vang-mieng-sjc-nhan-tron-9999-btmc-va-vang-the-gioi"
article = Article(url, language="vi")
article.download()
article.parse()
print(article.text)
# print(article.summary)
print(len(article.text))