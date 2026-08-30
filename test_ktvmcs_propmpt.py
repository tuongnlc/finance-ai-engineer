import os
from dotenv import load_dotenv
from ai_engineer.applications.topic_summary.application.pdf_generator import PdfSummarizationGenerator
from ai_engineer.shared.llm.create_llm import create_gemini_llm

load_dotenv()
llm_api_key = os.getenv("GCP_PROJECT_6")

# messages = [
#     {
#         "role": "system",
#         "content": "[PERSONA] Bạn là một chuyên gia tài chính chuyên phân tích và trích xuất thông tin kinh tế vĩ mô & chính sách từ các bài báo để phân tích sự ảnh hưởng tới thị trường chứng khoán. \n"
#                    "[TASK]Nhiệm vụ của bạn là phân tích đoạn văn bản được cung cấp và trả về kết quả dưới định dạng JSON duy nhất, tuân thủ tuyệt đối cấu trúc yêu cầu.\n"
#                    "\n"
#                    "Hãy tuân thủ các quy tắc sau:\n"
#                    "Bước 1: Chọn ra các chủ đề liên quan nhất từ danh sách cho phép bên dưới, việc chọn topic phải liên quan tới thị trường chứng khoán (tối đa 3 chủ đề)."
#                    "Bước 2: Sau đó sử dụng từng chủ đề đó làm key cho một JSON, và viết một đoạn tóm tắt ngắn gọn cho chủ đề (khoảng 100 từ).\n"
#                    "Bước 3: Sau đó tiến hành sentiment_analysis cho phần nội dung tóm tắt đó. Nhận một trong 3 giá trị: \"Tích cực\", \"Tiêu cực\", \"Trung lập\".\n"
#                    "Bước 4: Sau đó trích xuất thông tư, chính sách (circular_and_policy) đi kèm nếu có.\n"
#                    "\n"
#                    "[CONTEXT] Danh sách các topic cho phép:\n"
#                    "- Chính sách tiền tệ. Nếu bài viết đề cập tới thay đổi các chính sách tiền tệ với con số cụ thể đi kèm\n"
#                    "- Mặt bằng lãi suất. Nếu bài viết có đề cập tới thay đổi lãi suất kèm con số cụ thể\n"
#                    "- Thanh khoản hệ thống ngân hàng\n"
#                    "- Chính sách tài khóa và Đầu tư công\n"
#                    "- Tăng trưởng kinh tế\n"
#                    "- Yếu tố địa chính trị & Năng lượng\n"
#                    "- Biến động thị trường toàn cầu\n"
#                    "- Thanh khoản & Thị trường tài chính\n"
#                    "- Thất nghiệp\n"
#                    "- Lạm phát và Tỷ giá\n"
#                    "- Khối ngoại và Cán cân thanh toán.\n"
#                    "\n"
#                    " [FORMAT] Đầu ra bắt buộc phải là một đối tượng JSON hợp lệ, không kèm theo bất kỳ văn bản giải thích hay Markdown nào ngoài khối JSON. Theo sát example_output phía trên {{format_instructions}}\n"
#                    "--- START OF EXAMPLE ---\n"
#                    "[EXAMPLE INPUT]\n"
#                    "Công ty Cổ phần Đầu tư và Phát triển Cảng Đình Vũ (MCK: DVP, sàn HoSE) vừa có thông báo về ngày 10/9/2026 là ngày đăng ký cuối cùng để chi trả cổ tức đợt 2 năm 2025. Theo đó, Cảng Đình Vũ sẽ chi trả cổ tức cho cổ đông bằng tiền mặt với tỷ lệ 30%, tức cổ đông sở hữu 1 cổ phiếu sẽ được nhận 3.000 đồng. Với 40 triệu cổ phiếu đang lưu hành, Cảng Đình Vũ sẽ phải chi khoảng 120 tỷ đồng cho đợt trả cổ tức lần này. Trong một diễn biến khác, mới đây Cảng Đình Vũ đã công bố Nghị quyết về việc miễn nhiệm chức vụ Chủ tịch HĐQT nhiệm kỳ 2023 - 2028 đối với ông Vũ Tuấn Dương kể từ ngày 16/8/2026 do có đơn xin từ nhiệm. Doanh nghiệp quyết định bổ nhiệm ông Lê Hồng Quân đảm nhiệm chức vụ Chủ tịch HĐQT nhiệm kỳ 2023 - 2028.\n"
#                    "\n"
#                    "[EXAMPLE OUTPUT]\n"
#                    "{{\n"
#                    "    \"Chính sách tiền tệ\": {{\n"
#                    "    \"summary\": \" Ngân hàng Nhà nước ban hành Thông tư 25/2026 (có hiệu lực từ 01/07/2026) sửa đổi Thông tư 22/2019 nhằm tháo gỡ áp lực thanh khoản hệ thống. Điểm nhấn là việc nới tỷ lệ vốn ngắn hạn cho vay trung và dài hạn tối đa lên mức 40% (tăng so với mức 30% trước đó). Đồng thời, thông tư bổ sung 20% tiền gửi có kỳ hạn của Kho bạc Nhà nước vào mẫu số tính tỷ lệ dư nợ cho vay trên tổng tiền gửi. Chính sách này giúp giảm chi phí mở rộng bảng cân đối kế toán cho các ngân hàng, tạo dư địa hạ lãi suất huy động và cho vay, qua đó hỗ trợ dòng vốn cho bất động sản, hạ tầng và đầu tư công."
#                    "    \"sentiment_analysis\": \"Tích cực\"\n"
#                    "    \"circular_and_policy\": [\"Thông tư 25/2026\"]\n"
#                    "    }}\n"
#                    "}}\n"
#                    "--- END OF EXAMPLE ---\n"
#     },
#     {
#         "role": "user",
#         "content": "Hãy phân tích đoạn văn bản sau:\n\n{text_content}"
#     }
# ]

# # Để tạo ChatPromptTemplate từ messages trên:
# from langchain_core.prompts import ChatPromptTemplate
# chat_prompt = ChatPromptTemplate.from_messages(messages)

# from ai_engineer.shared.llm.create_llm import create_gemini_llm
# llm = create_gemini_llm(
#     api_key=llm_api_key,
#     model_name="gemini-3.5-flash-lite",
#     temperature=0,
# )


# content = "Theo dữ liệu từ Muavangbac.vn, quỹ bạc lớn nhất thế giới iShares Silver Trust (SLV) bất ngờ quay đầu bán ròng gần 44 tấn bạc trong ngày 26/6, đưa tổng lượng nắm giữ xuống dưới mốc 15.000 tấn. Việc SLV giảm lượng nắm giữ diễn ra trong bối cảnh giá bạc có phiên hồi phục mạnh, tăng 2,25% lên quanh mức 59 USD/ounce. Theo Kitco News, biên độ dao động lớn trong phiên cho thấy lực mua bắt đáy và hoạt động đóng vị thế bán khống (short-covering) đã hỗ trợ bạc phục hồi sau chuỗi giảm mạnh trước đó. Khác với vàng, bạc vừa mang đặc tính của một kim loại quý vừa là nguyên liệu phục vụ sản xuất công nghiệp, do đó thường biến động mạnh hơn khi thị trường điều chỉnh theo kỳ vọng chính sách tiền tệ. Nhịp tăng lần này của bạc chủ yếu đến từ yếu tố kỹ thuật, đồng USD suy yếu và hoạt động mua bù trạng thái bán trước đó, thay vì xuất hiện một động lực tăng giá mới mang tính bền vững. Bên cạnh đó, các yếu tố vĩ mô cũng phần nào hỗ trợ giá bạc. Chỉ số USD suy giảm, trong khi lợi suất trái phiếu kho bạc Mỹ kỳ hạn 10 năm lùi về quanh 4,4% đã giúp giảm áp lực lên nhóm kim loại quý. Ở chiều ngược lại, giá dầu WTI giảm về 69,23 USD/thùng và Brent còn 71,99 USD/thùng, phản ánh kỳ vọng áp lực lạm phát đang hạ nhiệt. Dù vậy, ông Christopher Lewis - chuyên gia phân tích kim loại quý tại FX Empire, xu hướng tăng bền vững của bạc vẫn chưa được xác nhận. Ông cho rằng chừng nào đồng USD còn duy trì sức mạnh trên thị trường quốc tế, bạc sẽ tiếp tục gặp khó khăn trong việc hình thành một xu hướng tăng rõ ràng. Vị chuyên gia này cũng cảnh báo nếu áp lực bán quay trở lại, khả năng bạc lùi về vùng 50 USD/ounce có thể xảy ra. Hiện tại, nhiều nhà đầu tư vẫn xem các nhịp hồi phục của bạc là cơ hội chốt lời hoặc bán ra, do thị trường chưa hội tụ đủ yếu tố để mở ra một chu kỳ tăng mới. Xét về kỹ thuật, ông Lewis đánh giá vùng 67,54 USD/ounce là ngưỡng kháng cự then chốt. Nếu vượt qua mốc này, triển vọng ngắn hạn của bạc sẽ cải thiện đáng kể. Tuy nhiên, trong bối cảnh hiện nay, tâm lý thận trọng vẫn đang chi phối giao dịch khi thị trường tiếp tục theo dõi diễn biến đồng USD, lãi suất và triển vọng kinh tế toàn cầu. Ở góc độ vĩ mô, chuyên gia FX Empire nhận định tác động của lạm phát lên giá hàng hóa đang dần suy yếu. Nếu xu hướng này tiếp diễn, bạc và các nhóm nguyên liệu khác có thể tiếp tục chịu áp lực điều chỉnh trong thời gian tới"
# chain = chat_prompt | llm
# result = chain.invoke({"text_content": content})
# print(result.content[0].get("text"))

content = [{'person_mention': ['adam button', 'kevin warsh', 'marc chandler', 'james stanley', 'adrian day', 'rich checkan'], 'summary': 'Quỹ ETF vàng lớn nhất thế giới SPDR Gold Trust đã bán ròng gần 5 tấn vàng trong tuần, đưa lượng nắm giữ xuống 1.042,4 tấn trong bối cảnh giá vàng thế giới điều chỉnh giảm hơn 3% xuống quanh 4.455 USD/ounce. Động lực từ phát biểu của Chủ tịch Fed làm dấy lên kỳ vọng tăng lãi suất, cùng sức mạnh của đồng USD, tạo áp lực ngắn hạn lên kim loại quý. Tuy nhiên, giới phân tích cho rằng đây chỉ là nhịp điều chỉnh lành mạnh, trong khi các yếu tố dài hạn như nợ công Mỹ và áp lực lạm phát vẫn hỗ trợ xu hướng tăng.', 'sentiment_analysis': 'Tiêu cực', 'circular_and_policy': []}, {'person_mention': ['kevin warsh', 'tai wong'], 'summary': 'Giá vàng thế giới và trong nước đồng loạt giảm mạnh trong phiên giao dịch cuối tuần sau khi Chủ tịch Cục Dự trữ Liên bang Mỹ (Fed) phát tín hiệu ưu tiên kiểm soát lạm phát và có khả năng nâng lãi suất trong thời gian tới. Thị trường gia tăng kỳ vọng Fed tăng lãi suất với xác suất đạt 58% vào tháng 9 và 89% vào tháng 12. Áp lực từ chính sách tiền tệ thắt chặt của Mỹ đã đẩy giá vàng thế giới sụt giảm và kéo theo sự sụt giảm của giá vàng miếng và vàng nhẫn trong nước.', 'sentiment_analysis': 'Tiêu cực', 'circular_and_policy': []}, {'person_mention': ['christian borjon valencia', 'kevin warsh'], 'summary': 'Giá bạc trong nước và quốc tế ghi nhận đà giảm mạnh sau khi chạm mức cao nhất trong vòng hai tháng, với giá bạc giao ngay trên thị trường quốc tế rơi xuống dưới mốc 67 USD/ounce. Nguyên nhân chính được chỉ ra là do những phát biểu mang quan điểm thắt chặt chính sách tiền tệ từ Chủ tịch Fed Kevin Warsh tại hội nghị Jackson Hole, làm tăng lợi suất trái phiếu kho bạc Mỹ và gây áp lực giảm giá lên các tài sản không sinh lời như kim loại quý. Diễn biến này làm gia tăng áp lực điều chỉnh và nhà đầu tư cần theo dõi kỹ các vùng hỗ trợ quan trọng.', 'sentiment_analysis': 'Tiêu cực', 'circular_and_policy': []}, {'person_mention': ['vũ thị chân phương', 'greg vadala', 'john welling'], 'summary': 'Chủ tịch Ủy ban Chứng khoán Nhà nước Vũ Thị Chân Phương đã có buổi làm việc quan trọng với lãnh đạo S&P Dow Jones Indices tại New York nhằm thảo luận về tiến trình phát triển và cải cách thị trường chứng khoán Việt Nam. Hai bên tập trung trao đổi về các giải pháp nâng cao khả năng tiếp cận thị trường cho nhà đầu tư quốc tế, bao gồm việc vận hành hệ thống công nghệ thông tin mới, hoàn thiện cơ chế thanh toán bù trừ và triển khai mô hình đối tác bù trừ trung tâm CCP. S&P DJI đánh giá cao những nỗ lực cải cách của Việt Nam, qua đó củng cố kỳ vọng sớm được nâng hạng trong thời gian tới.', 'sentiment_analysis': 'Tích cực', 'circular_and_policy': []}, {'person_mention': ['neil macgregor'], 'summary': 'Trong giai đoạn 2026-2030, nhu cầu vốn trung và dài hạn của Việt Nam tăng mạnh để phát triển các dự án hạ tầng chiến lược như Cảng hàng không quốc tế Gia Bình và 4 dự án đường sắt lớn theo hình thức PPP với tổng vốn hàng trăm nghìn tỷ đồng. Dòng vốn đầu tư nước ngoài (FDI) và các giao dịch M&A, góp vốn mua cổ phần tiếp tục tăng trưởng mạnh mẽ, cho thấy sức hút của thị trường nhưng cũng đặt ra yêu cầu cao hơn về tính minh bạch pháp lý và năng lực triển khai dự án.', 'sentiment_analysis': 'Tích cực', 'circular_and_policy': ['Danh mục quốc gia các dự án kêu gọi đầu tư nước ngoài giai đoạn 2026-2030']}, {'person_mention': ['kevin warsh', 'jeffrey roach', 'fawad razaqzada'], 'summary': 'Phát biểu mang tính diều hâu của Chủ tịch Cục Dự trữ Liên bang Mỹ (Fed) Kevin Warsh cùng số liệu việc làm được điều chỉnh đã củng cố kỳ vọng Fed sẽ duy trì chính sách tiền tệ thắt chặt và có khả năng tăng lãi suất. Xác suất dự báo Fed tăng lãi suất trong tháng 9 đã tăng từ 35,9% lên 57,5%, khiến đồng USD tăng giá mạnh và lợi suất trái phiếu kho bạc Mỹ kỳ hạn 2 năm tăng 11,8 điểm cơ bản lên 4,348%. Diễn biến này tạo áp lực bán lớn lên thị trường vàng toàn cầu cũng như trong nước, khiến kim loại quý suy giảm sau chuỗi ngày tăng nóng.', 'sentiment_analysis': 'Tiêu cực', 'circular_and_policy': []}]

pdf_generator = PdfSummarizationGenerator(
    font_path="/Users/tuongnguyen/Desktop/projects/finance_ai_platform/finance-ai-engineer/ai_engineer/applications/topic_summary/orchestration/resources/Arial Unicode.ttf",
    report_date="2026-08-28",
    report_type = " Kinh tế vĩ mô & Chính sách",
    output_pdf_path="test.pdf"
)

pdf_generator.run(content)