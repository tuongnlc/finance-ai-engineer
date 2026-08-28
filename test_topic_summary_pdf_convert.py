from xhtml2pdf import pisa
import os

json_1 = {
  "sac_thai": "Trung lập",
  "topic_chinh": {
    "Huy động vốn & Trái phiếu": "Công ty TNHH Parkland 53 vừa phát hành thành công lô trái phiếu mã P5332601 trị giá 7.000 tỷ đồng vào ngày 30/06/2026 với kỳ hạn 12 tháng, lãi suất cố định 10%/năm, do Chứng khoán Kỹ thương (TCBS) tư vấn. Đây là lô trái phiếu có tài sản bảo đảm đầu tiên của doanh nghiệp nhằm phục vụ nhu cầu vốn lớn.",
    "Chiến lược mới": "Parkland 53 là chủ đầu tư dự án Lumière Riverside tại TP.HCM và tham gia đầu tư dự án khu đô thị phức hợp Hạ Long Xanh tại Quảng Ninh thông qua hình thức hợp tác kinh doanh (BCC) với Bất động sản Hưng Long.",
    "Thông tin tài chính đáng chú ý": "Tính đến tháng 1/2026, Parkland 53 có vốn điều lệ tăng lên hơn 3.478 tỷ đồng. Theo Saigon Ratings, doanh nghiệp duy trì mức nợ vay cao so với vốn chủ sở hữu, năng lực trả nợ còn ở mức thấp, đồng thời dòng tiền và kết quả kinh doanh phụ thuộc lớn vào tiến độ dự án Hạ Long Xanh cũng như hiệu quả hợp tác chiến lược với Masterise."
  }
}

json_2 = {
  "sac_thai": "Tích cực",
  "topic_chinh": {
    "Giao dịch cổ phiếu trên thị trường": "Phiên 17/6 ghi nhận cổ phiếu Vingroup (VIC) bị khối ngoại bán ròng mạnh 11,5 triệu đơn vị, tương đương hơn 2.300 tỷ đồng thông qua kênh thỏa thuận. Tuy nhiên, lực bán này được nhà đầu tư trong nước cân trọn, giúp bộ đôi VIC và VHM 'rút chân' thành công khỏi mức giảm sâu 3-4% trong phiên và đóng cửa chỉ giảm nhẹ chưa đầy 2 điểm, qua đó nâng đỡ toàn bộ thị trường chung.",
    "Chiến lược mới": "Vinhomes quyết định ngưng hoàn toàn việc mở rộng quỹ đất dự án mới tại Việt Nam để tập trung tối ưu hóa chất lượng trên quỹ đất khổng lồ sẵn có khoảng 29.500 ha, đủ phát triển liên tục trong 5-7 năm tới. Song song đó, Vingroup tiếp tục củng cố ba trụ cột chính, mở rộng sang ba lĩnh vực mới gồm hạ tầng, năng lượng xanh và văn hóa, đồng thời giao mục tiêu tăng trưởng cao cho các đơn vị trong hệ sinh thái như VinFast và Vinpearl.",
    "Dự báo tài chính & Tăng trưởng": "Vingroup đặt mục tiêu kinh doanh kỷ lục trong năm 2026 với doanh thu thuần đạt 485.000 tỷ đồng, tăng 46% so với năm trước và lợi nhuận sau thuế dự kiến đạt 35.000 tỷ đồng, cao gấp 3 lần cùng kỳ. Để phục vụ chiến lược tăng trưởng mạnh mẽ và mở rộng quy mô, tập đoàn sẽ triển khai nhiều hình thức huy động vốn thông qua các công cụ tài chính linh hoạt cả trong và ngoài nước."
  }
}

date_ = "28/08/2026"
report_type = "Báo cáo thông tin doanh nghiệp"

content = [
    {
        "Công ty": "Parkland 53",
        "Sác thái": "Trung lập",
        "Huy động vốn & Trái phiếu": json_1["topic_chinh"]["Huy động vốn & Trái phiếu"]
    },
    {
        "Công ty": "Parkland 53",
        "Sác thái": "Trung lập",
        "Chiến lược mới": json_1["topic_chinh"]["Chiến lược mới"]
    },
    {
        "Công ty": "Parkland 53",
        "Sác thái": "Trung lập",
        "Thông tin tài chính đáng chú ý": json_1["topic_chinh"]["Thông tin tài chính đáng chú ý"]
    },
    {
        "Công ty": "Vingroup",
        "Sác thái": "Tiêu cực",
        "Giao dịch cổ phiếu trên thị trường": json_2["topic_chinh"]["Giao dịch cổ phiếu trên thị trường"]
    },
    {
        "Công ty": "Vingroup",
        "Sác thái": "Tích cực",
        "Chiến lược mới": json_2["topic_chinh"]["Chiến lược mới"]
    },
    {
        "Công ty": "Vingroup",
        "Sác thái": "Tích cực",
        "Dự báo tài chính & Tăng trưởng": json_2["topic_chinh"]["Dự báo tài chính & Tăng trưởng"]
    },
]

FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"


def _escape_html(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def _group_by_company(items):
    grouped = {}
    for item in items:
        company = item.get("Công ty", "")
        sac_thai = item.get("Sác thái", "")
        if company not in grouped:
            grouped[company] = []
        topic_name = None
        topic_content = None
        for key, value in item.items():
            if key in ("Công ty", "Sác thái"):
                continue
            topic_name = key
            topic_content = value
            break
        if topic_name is not None:
            grouped[company].append((topic_name, topic_content, sac_thai))
    return grouped


def _sentiment_style(sac_thai):
    s = (sac_thai or "").strip().lower()
    if "tích cực" in s or s == "tich cuc":
        return "background-color: #e6f4ea; color: #137333; border: 1px solid #ace0af;"
    if "tiêu cực" in s or s == "tieu cuc":
        return "background-color: #fce8e6; color: #a50e0e; border: 1px solid #f5b0ab;"
    return "background-color: #f1f3f4; color: #5f6368; border: 1px solid #dadce0;"


def build_html(date_str, rtype, items):
    grouped = _group_by_company(items)

    body_parts = []
    for company, topics in grouped.items():
        body_parts.append(
            f'<div class="company-block">\n'
            f'  <h1 class="company-name">{_escape_html(company)}</h1>\n'
            f'</div>'
        )
        for topic_name, topic_content, sac_thai in topics:
            badge_html = ""
            if sac_thai:
                badge_html = (
                    f'<span class="sentiment-badge" style="{_sentiment_style(sac_thai)}">'
                    f'{_escape_html(sac_thai)}</span>'
                )
            body_parts.append(
                f'<h2 class="topic-title">{_escape_html(topic_name)} {badge_html}</h2>\n'
                f'<p>{_escape_html(topic_content)}</p>'
            )

    companies_list = ", ".join(grouped.keys())

    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @font-face {{
            font-family: 'ArialUnicode';
            src: url('Arial Unicode.ttf');
        }}

        body {{
            font-family: 'ArialUnicode', sans-serif;
            font-size: 11pt;
            color: #333333;
            line-height: 1.6;
            margin: 40px;
        }}

        .header {{
            margin-bottom: 20px;
            border-bottom: 2px solid #1e3c72;
            padding-bottom: 10px;
        }}

        h1 {{
            color: #1e3c72;
            font-size: 20pt;
            margin: 0 0 5px 0;
        }}

        .date {{
            color: #666666;
            font-size: 10pt;
        }}

        .company-block {{
            margin-top: 24px;
            margin-bottom: 4px;
            page-break-inside: avoid;
        }}

        .company-name {{
            color: #1e3c72;
            font-size: 16pt;
            border-bottom: 1px solid #cfd8e3;
            padding-bottom: 4px;
            margin-bottom: 6px;
        }}

        h2 {{
            color: #2a5298;
            font-size: 13pt;
            margin-top: 16px;
            margin-bottom: 8px;
        }}

        .sentiment-badge {{
            display: inline-block;
            font-size: 9pt;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: normal;
            margin-left: 6px;
            vertical-align: middle;
        }}

        p {{
            margin: 0 0 15px 0;
            text-align: justify;
        }}

        .footer {{
            margin-top: 30px;
            font-size: 9pt;
            color: #888888;
            text-align: center;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{_escape_html(rtype)}</h1>
        <div class="date">Ngày phát hành: {_escape_html(date_str)}</div>
    </div>

    {chr(10).join(body_parts)}

    <div class="footer">
        Tài liệu nội dung phân tích và tổng hợp doanh nghiệp {_escape_html(companies_list)}.
    </div>

</body>
</html>
"""


html_content = build_html(date_, report_type, content)

def link_callback(uri, rel):
    if uri == 'Arial Unicode.ttf':
        return FONT_PATH
    return uri

def convert_html_to_pdf(html_str, output_pdf):
    with open(output_pdf, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(
            html_str,
            dest=pdf_file,
            link_callback=link_callback
        )
    
    if pisa_status.err:
        print("Có lỗi xảy ra trong quá trình chuyển đổi!")
    else:
        print(f"Đã tạo file PDF tiếng Việt thành công: {output_pdf}")

if __name__ == "__main__":
    convert_html_to_pdf(html_content, "bao_cao_chuan_tieng_viet.pdf")