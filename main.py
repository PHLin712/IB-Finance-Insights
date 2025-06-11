import requests
from bs4 import BeautifulSoup
import datetime
from jinja2 import Environment, FileSystemLoader

# Goldman Sachs
def fetch_goldman():
    url = "https://www.goldmansachs.com/feeds/insights.json"
    base_url = "https://www.goldmansachs.com"
    try:
        data = requests.get(url).json()
    except Exception as e:
        print("Goldman Sachs 下載失敗：", e)
        return []
    result = []
    for item in data:
        title = item.get("title")
        publish_date = None
        if item.get("cmsPageProps", {}).get("publishDate"):
            publish_date = item["cmsPageProps"]["publishDate"][:10]
        url_path = item.get("path")
        full_url = base_url + url_path if url_path else None
        topic = ""
        if "cmsPageProps" in item and "primaryTopic" in item["cmsPageProps"] and item["cmsPageProps"]["primaryTopic"]:
            topic = item["cmsPageProps"]["primaryTopic"][0].get("title")
        if publish_date and title and full_url:
            result.append({
                "title": title,
                "publish_date": publish_date,
                "topic": topic,
                "bank": "Goldman Sachs",
                "url": full_url
            })
    return result

# JP Morgan
def fetch_jpm():
    url = "https://www.jpmorgan.com/services/json/v1/dynamic-grid.service/parent=jpmorgan/global/US/en/insights&comp=root/content-parsys/dynamic_grid&page=p1.json"
    base_url = "https://www.jpmorgan.com"
    try:
        data = requests.get(url).json()
    except Exception as e:
        print("JP Morgan 下載失敗：", e)
        return []
    items = data["items"]
    result = []
    for item in items:
        title = item.get("title")
        publish_date = item.get("date")
        try:
            publish_date_fmt = datetime.datetime.strptime(publish_date, '%B %d, %Y').strftime('%Y-%m-%d')
        except:
            publish_date_fmt = publish_date
        topic = item.get("eyebrow")
        url_path = item.get("link")
        full_url = base_url + url_path if url_path else None
        if title and publish_date_fmt and full_url:
            result.append({
                "title": title,
                "publish_date": publish_date_fmt,
                "topic": topic,
                "bank": "JP Morgan",
                "url": full_url
            })
    return result

# Morgan Stanley
def fetch_morgan_stanley():
    url = "https://www.morganstanley.com/im/en-us/individual-investor/insights.html"
    try:
        html = requests.get(url).text
    except Exception as e:
        print("Morgan Stanley 下載失敗：", e)
        return []
    soup = BeautifulSoup(html, "html.parser")
    result = []
    for card in soup.find_all("div", class_="borderBottom"):
        title = None
        url = None
        h4 = card.find("h4", class_="media-heading")
        if h4:
            a = h4.find("a", href=True)
            if a:
                title = a.get_text(strip=True)
                url = a['href']
                if url.startswith("/"):
                    url = "https://www.morganstanley.com" + url
        date = None
        date_container = card.find("span", class_="pressCenterDate")
        if date_container:
            date_span = date_container.find("span")
            if date_span:
                date = date_span.get_text(strip=True).replace("•", "").strip()
        if date:
            try:
                publish_date_fmt = datetime.datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')
            except:
                publish_date_fmt = date
        else:
            publish_date_fmt = None
        if title and url and publish_date_fmt:
            result.append({
                "title": title,
                "publish_date": publish_date_fmt,
                "topic": None,
                "bank": "Morgan Stanley",
                "url": url
            })
    return result

if __name__ == "__main__":
    all_reports = []
    all_reports.extend(fetch_goldman())
    all_reports.extend(fetch_jpm())
    all_reports.extend(fetch_morgan_stanley())
    print(f"\n三家合併後共 {len(all_reports)} 筆")

    all_reports_sorted = sorted(all_reports, key=lambda x: x["publish_date"], reverse=True)

    # 路徑寫成 '.'
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_out = template.render(reports=all_reports_sorted)

    # 直接輸出到 repo root
    with open("全球投行報告總覽.html", "w", encoding="utf-8") as f:
        f.write(html_out)

    print("已產生『全球投行報告總覽.html』，用瀏覽器打開即可！")
