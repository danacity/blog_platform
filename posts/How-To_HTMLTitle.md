---
title: How-to change the HTML Title
date: 2025-02-20T14:30:00+01:00
draft: false
excerpt: How to edit the HTML title from (FastHTML Page)
tags: 
Diataxis:
  - How-To
---
## How-to change the HTML Title 
The default Title for your site/app with be:  
![Default Html Title](/public/images/20250216034414.png)
To Personalize your title you need to add Title('Your new title") as the 1st element returned in your index function like this:
```python
@rt
def index():
    posts = read_posts()
    return Title('Efels Blog'), Container(   
        header_content(),
        Div(
            navigation_panel(posts),
            blog_grid(posts),
            cls="flex items-start"))
```
I know it seems like a no brainer but I waisted more time than I would have liked trying to add the title as part of the headers before I found other people talking about it on discord,