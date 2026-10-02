#vn-vi for Vietnam


from ddgs import DDGS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

query = "Gía vàng hôm nay"

# query = f"{query} ({news_domains})"
results = DDGS().news(query, max_results=5, safesearch = "off", region="vn-vi")

print(results)
from newspaper import Article



def similar_compare_with_tfidf(query: str, results: list[dict]) -> list[dict]:
    # Gộp title và body của từng kết quả thành một đoạn văn bản (document)
    documents = [item['title'] + " " + item['body'] for item in results]

    # Đưa query và danh sách documents vào chung một tập hợp (corpus)
    corpus = [query] + documents

    # 1. Khởi tạo và tính toán ma trận TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # 2. Tách vector của query (vị trí đầu tiên [0]) và vector của các kết quả ([1:])
    query_vector = tfidf_matrix[0:1]
    doc_vectors = tfidf_matrix[1:]

    # 3. Tính điểm tương đồng (Cosine Similarity) giữa query và từng kết quả
    similarity_scores = cosine_similarity(query_vector, doc_vectors).flatten()

    # 4. Sắp xếp và in kết quả theo độ liên quan từ cao đến thấp
    ranked_indices = similarity_scores.argsort()[::-1]

    print("Kết quả sắp xếp theo độ liên quan (TF-IDF):")
    output_mapping = []
    for idx in ranked_indices:
        score = similarity_scores[idx]
        # print(f"- Điểm: {score:.4f} | Tiêu đề: {results[idx]['title']}")
        output_mapping.append({
            "url": results[idx]["url"],
            "score": float(score)
        })
    return output_mapping

def extract_from_newspaper(url: str) -> str:
    article = Article(url, language="vi")
    article.download()
    article.parse()
    return article.text

search_results = similar_compare_with_tfidf(query, results)

top_results = search_results[:2]
# print(top_results)

output_text = []
for item in top_results:
    result = extract_from_newspaper(item["url"])
    output_text.append({
        "url": item["url"],
        "content": result
    })
    
print(output_text)