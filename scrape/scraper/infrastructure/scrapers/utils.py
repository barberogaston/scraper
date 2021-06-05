def normalize_html_string(html: str) -> str:
    tokens = ['\n',
              '\t',
              '<b>',
              '</b>',
              '<span>',
              '</span>',
              '<h1>',
              '</h1>',
              '<i>',
              '</i>',
              '<br>']
    for token in tokens:
        html = html.replace(token, '')
    return html
