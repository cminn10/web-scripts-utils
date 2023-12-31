from jinja2 import Template
from bs4 import BeautifulSoup
import requests
import re
from config import TAG_MAPPING, REPO_URL, LOFTER_REPO_BASE as BASE
from utils.db_utils import Blog_db_utils

db = Blog_db_utils()


def html_to_markdown(html_string):
    markdown = re.sub(r'<\/?p>', '', html_string)
    markdown = re.sub(r'<br/?>', r'\\n', markdown)
    # replace all " with /"
    markdown = re.sub(r'\"', r'\\"', markdown)
    return markdown


def get_work_ids(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    work_lst = soup.select("#main > ol > li")
    work_ids = [work.get('id').split('_')[-1] for work in work_lst]
    return work_ids


def query_result(work_id):
    url = f'https://archiveofourown.org/works/{work_id}?view_adult=true'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.select_one("#workskin > div:nth-child(1) > h2").get_text().strip()
    date = soup.select_one("#main > div.wrapper > dl > dd.stats > dl > dd.published").get_text().strip()
    fandom_lst = soup.select("#main > div.wrapper > dl > dd.fandom.tags > ul > li > a")
    fandoms = [fandom.get_text().strip() for fandom in fandom_lst]
    tag_lst = soup.select("#main > div.wrapper > dl > dd.relationship.tags > ul > li > a")
    tags = [tag.get_text().strip() for tag in tag_lst]
    tags.extend(fandoms)
    tags = [TAG_MAPPING[tag] if tag in TAG_MAPPING else tag for tag in tags]
    summary_div = soup.select("#workskin > div:nth-child(1) > div.summary.module > blockquote > p")
    summary = ''.join([str(p) for p in summary_div])
    # summary = r'\n\n'.join([html_to_markdown(str(p_element)) for p_element in summary_div])
    note1_div = soup.select("#workskin > div:nth-child(1) > div.notes.module > blockquote > p")
    note1 = ''.join([str(p) for p in note1_div])
    # note1 = r'\n\n'.join([html_to_markdown(str(note)) for note in note1_div])
    note2_div = soup.select("#work_endnotes > blockquote > p")
    note2 = ''.join([str(p) for p in note2_div])
    # note2 = r'\n\n'.join([html_to_markdown(str(note)) for note in note2_div])
    body_div = soup.select("#chapters > div > p")
    body = ''.join([str(p_element) for p_element in body_div])

    return {
        "title": title,
        "date": date,
        # "fandoms": fandoms,
        "tags": tags,
        "summary": summary,
        "note1": note1,
        "note2": note2,
        "body": body,
    }


def query_result_lofter(work_id):
    url = f'https://{BASE}.lofter.com/post/{work_id}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_div = soup.select_one(
        'body > div > div.g-mn > div > div.m-postdtl > div > div > div.ct > div > h2 > a')
    title = title_div.get_text().strip() if title_div else None
    date = soup.select_one(
        'body > div > div.g-mn > div > div.m-postdtl > div > div > div.info.box > a.date').get_text().strip()
    tag_els = soup.select('body > div > div.g-mn > div > div.m-postdtl > div > div > div.info.box > a.tag')
    tag_lst = [tag_el.get_text().strip().replace('#', '') for tag_el in tag_els]
    tags = [tag for tag in tag_lst if len(tag) <= 8]
    body_div = soup.select('body > div > div.g-mn > div > div.m-postdtl > div > div > div.ct > div > div > p')
    body = [str(p_element) for p_element in body_div]
    body = ''.join([e for e in body if '<a' not in e])
    return {
        "title": title,
        "date": date,
        "tags": tags,
        "body": body,
    }


def render_documents(title, date, tags, body, summary=None, note1=None, note2=None):
    with open('./source/template.md', 'r') as f:
        template_content = f.read()
    template = Template(template_content)
    rendered_content = template.render(title=title, tags=tags, date=date, body=body, summary=summary, note1=note1,
                                       note2=note2)
    filename = title.replace('/', '_')
    with open(f'./data/{filename}.md', 'w') as f:
        f.write(rendered_content)


def sync_db(blog):
    db.connect()

    last_blog = db.execute_query('SELECT * FROM blog ORDER BY id DESC LIMIT 1')
    curr_id = last_blog[0]['id'] + 1 if last_blog else 1

    db.execute_update(f'''
        INSERT INTO blog (user_id, id, title, content, summary, note, end_note, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1, curr_id, blog.get('title', ''), blog.get('body', ''), blog.get('summary', ''),
        blog.get('note1', ''), blog.get('note2', ''), blog.get('date', '')))

    existing_tags = db.execute_query('SELECT * FROM tag ORDER BY id DESC')
    curr_tag_id = existing_tags[0]['id'] + 1 if existing_tags else 1
    for tag in blog['tags']:
        if tag in [t['name'] for t in existing_tags]:
            tag_id = next(t['id'] for t in existing_tags if t['name'] == tag)
            db.execute_update(f'INSERT INTO blog_tag (blog_id, tag_id) VALUES ({curr_id}, {tag_id})')
        else:
            db.execute_update(f'INSERT INTO tag (id, name) VALUES(?, ?)', (curr_tag_id, tag))
            db.execute_update(f'INSERT INTO blog_tag (blog_id, tag_id) VALUES ({curr_id}, {curr_tag_id})')
            curr_tag_id += 1

    db.close()
