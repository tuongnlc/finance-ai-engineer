from xhtml2pdf import pisa


class PdfSummarizationGenerator:
    def __init__(self, font_path: str, report_date: str, report_type: str, output_pdf_path: str):
        self.font_path = font_path
        self.report_date = report_date
        self.report_type = report_type
        self.output_pdf_path = output_pdf_path

    @staticmethod
    def _escape_html(text):
        return (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;"))

    @staticmethod
    def _title_case(s):
        if not s:
            return s
        words = s.split(" ")
        result = []
        for w in words:
            if len(w) == 0:
                result.append(w)
            else:
                result.append(w[0].upper() + w[1:])
        return " ".join(result)

    @staticmethod
    def _group_by_company(items):
        grouped = {}
        for item in items:
            company_val = item.get("stocks_mention", "")
            if isinstance(company_val, list):
                company = ", ".join(str(c) for c in company_val).upper()
            else:
                company = str(company_val).upper()

            mention_val = item.get("person_mention", "")
            if isinstance(mention_val, list):
                mention_person = ", ".join(str(p) for p in mention_val)
            else:
                mention_person = str(mention_val)

            if company not in grouped:
                grouped[company] = []

            meta_keys = ("stocks_mention", "person_mention")
            for key, value in item.items():
                if key in meta_keys:
                    continue
                if value:
                    if isinstance(value, dict):
                        summary = value.get("summary", "")
                        sac_thai = value.get("sentiment_analysis", "")
                    else:
                        summary = str(value)
                        sac_thai = ""
                    grouped[company].append((key, summary, sac_thai, mention_person))
        return grouped

    @staticmethod
    def _sentiment_style(sac_thai):
        s = (sac_thai or "").strip().lower()
        if "tích cực" in s or s == "tich cuc":
            return "background-color: #e6f4ea; color: #137333; border: 1px solid #ace0af;"
        if "tiêu cực" in s or s == "tieu cuc":
            return "background-color: #fce8e6; color: #a50e0e; border: 1px solid #f5b0ab;"
        return "background-color: #f1f3f4; color: #5f6368; border: 1px solid #dadce0;"

    def _build_css(self):
        return """
            @font-face {
                font-family: 'ArialUnicode';
                src: url('Arial Unicode.ttf');
            }

            body {
                font-family: 'ArialUnicode', sans-serif;
                font-size: 11pt;
                color: #333333;
                line-height: 1.6;
                margin: 40px;
            }

            .header {
                margin-bottom: 20px;
                border-bottom: 2px solid #1e3c72;
                padding-bottom: 10px;
            }

            h1 {
                color: #1e3c72;
                font-size: 20pt;
                margin: 0 0 5px 0;
            }

            .date {
                color: #666666;
                font-size: 10pt;
            }

            .company-block {
                margin-top: 24px;
                margin-bottom: 4px;
                page-break-inside: avoid;
            }

            .company-name {
                color: #1e3c72;
                font-size: 16pt;
                border-bottom: 1px solid #cfd8e3;
                padding-bottom: 4px;
                margin-bottom: 6px;
            }

            h2 {
                color: #2a5298;
                font-size: 13pt;
                margin-top: 16px;
                margin-bottom: 8px;
            }

            .sentiment-badge {
                display: inline-block;
                font-size: 9pt;
                padding: 2px 8px;
                border-radius: 3px;
                font-weight: normal;
                margin-left: 6px;
                vertical-align: middle;
            }

            p {
                margin: 0 0 15px 0;
                text-align: justify;
            }
            """

    def _build_header(self, date_str, rtype):
        return (
            f'<div class="header">\n'
            f'  <h1>{self._escape_html(rtype)}</h1>\n'
            f'  <div class="date">Ngày phát hành: {self._escape_html(date_str)}</div>\n'
            f'</div>'
        )

    def _build_sentiment_badge(self, sac_thai):
        if not sac_thai:
            return ""
        return (
            f'<span class="sentiment-badge" style="{self._sentiment_style(sac_thai)}">'
            f'{self._escape_html(sac_thai)}</span>'
        )

    def _build_topic_block(self, topic_name, topic_content, sac_thai):
        badge_html = self._build_sentiment_badge(sac_thai)
        return (
            f'<h2 class="topic-title">{self._escape_html(self._title_case(topic_name))} {badge_html}</h2>\n'
            f'<p>{self._escape_html(topic_content)}</p>'
        )

    def _build_separator(self):
        return '<p style="text-align: center; letter-spacing: 8px; color: #888; margin: 40px 0 20px 0;">- - - -</p>'

    def _build_business_body(self, items):
        grouped = self._group_by_company(items)
        company_list = list(grouped.items())

        body_parts = []
        for idx, (company, topics) in enumerate(company_list):
            company_html = (
                f'<div class="company-block">\n'
                f'  <h1 class="company-name">Công ty: {self._escape_html(company)}</h1>\n'
            )
            mention_person = topics[0][3] if topics else ""
            if mention_person:
                company_html += (
                    f'  <p style="font-style: italic; color: #555; font-size: 10pt; margin-top: 2px;">'
                    f'Nhân sự liên quan: {self._escape_html(mention_person)}</p>\n'
                )
            company_html += f'</div>'
            body_parts.append(company_html)

            for topic_name, topic_content, sac_thai, _ in topics:
                body_parts.append(self._build_topic_block(topic_name, topic_content, sac_thai))

            if idx < len(company_list) - 1:
                body_parts.append(self._build_separator())

        return chr(10).join(body_parts)

    @staticmethod
    def _get_policy_info(value_dict):
        if not isinstance(value_dict, dict):
            return ""
        cp_val = value_dict.get("circular_and_policy")
        if cp_val:
            if isinstance(cp_val, list):
                return ", ".join(str(x) for x in cp_val if x)
            return str(cp_val)
        for k in value_dict:
            if "thông tư" in k.lower() or "chính sách" in k.lower() or "chính sach" in k.lower():
                v = value_dict.get(k)
                if v:
                    if isinstance(v, list):
                        return ", ".join(str(x) for x in v if x)
                    return str(v)
        return ""

    def _build_policy_line(self, policy_info):
        if not policy_info:
            return ""
        return (
            f'<p style="font-size: 10pt; color: #555; margin-top: -8px; margin-bottom: 15px;">'
            f'<strong>Thông tư, chính sách:</strong> {self._escape_html(policy_info)}</p>'
        )

    def _build_macro_or_market_body(self, items):
        body_parts = []
        meta_keys = ("stocks_mention", "person_mention")
        for idx, item in enumerate(items):
            mention_val = item.get("person_mention", "")
            if isinstance(mention_val, list):
                mention_person = ", ".join(str(p) for p in mention_val if p)
            else:
                mention_person = str(mention_val or "")

            for key, value in item.items():
                if key in meta_keys:
                    continue
                if not value:
                    continue
                if isinstance(value, dict):
                    topic_name = key
                    summary = value.get("summary", "")
                    sac_thai = value.get("sentiment_analysis", "")
                    policy_info = self._get_policy_info(value)
                else:
                    topic_name = key
                    summary = str(value)
                    sac_thai = ""
                    policy_info = ""
                if summary:
                    body_parts.append(self._build_topic_block(topic_name, summary, sac_thai))
                    if mention_person:
                        body_parts.append(
                            f'<p style="font-size: 10pt; color: #555; margin-top: -10px; margin-bottom: 12px;">'
                            f'<strong>Người liên quan:</strong> {self._escape_html(mention_person)}</p>'
                        )
                    policy_line = self._build_policy_line(policy_info)
                    if policy_line:
                        body_parts.append(policy_line)

            if idx < len(items) - 1:
                body_parts.append(self._build_separator())

        return chr(10).join(body_parts)

    def _select_body_builder(self, rtype):
        rtype_norm = (rtype or "").strip().lower()
        if "kinh tế vĩ mô" in rtype_norm or "chính sách" in rtype_norm:
            return self._build_macro_or_market_body
        if "thị trường" in rtype_norm or "giao dịch" in rtype_norm: #Note: macro and market share the same body builder
            return self._build_macro_or_market_body
        return self._build_business_body

    def build_html(self, date_str, rtype, items):
        css = self._build_css()
        header = self._build_header(date_str, rtype)
        body_builder = self._select_body_builder(rtype)
        body = body_builder(items)

        return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    {css}
                </style>
            </head>
            <body>
                {header}

                {body}

            </body>
            </html>
            """

    def link_callback(self, uri, basepath=None):
        if uri == 'Arial Unicode.ttf':
            return self.font_path
        return uri

    def convert_html_to_pdf(self, html_str, output_pdf):
        with open(output_pdf, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_str,
                dest=pdf_file,
                link_callback=self.link_callback
            )

        if pisa_status.err:
            print("Có lỗi xảy ra trong quá trình chuyển đổi!")
        else:
            print(f"Đã tạo file PDF tiếng Việt thành công: {output_pdf}")

    def run(self, content):
        html_content = self.build_html(self.report_date, self.report_type, content)
        self.convert_html_to_pdf(html_content, self.output_pdf_path)
