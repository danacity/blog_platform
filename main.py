from fasthtml.common import *
from monsterui.all import *
from datetime import datetime, date
from pathlib import Path
import yaml
#from fasthtml.components import Uk_theme_switcher

def social_meta(platform, post=None, type="website"):
   blog_url = "www.blog.efels.com"
   default_image = "/public/images/blog-default.jpg"
   
   if post is None:  # Homepage case
       return [
           Meta(property="og:title", content="Dan's Blog"),
           Meta(property="og:description", content="Personal blog about software development and tech"),
           Meta(property="og:image", content=f"https://{blog_url}{default_image}"),
           Meta(property="og:url", content=f"https://{blog_url}"),
           Meta(property="og:type", content=type),
           Meta(name="twitter:card", content="summary"),
           Meta(name="twitter:title", content="Dan's Blog"),
           Meta(name="twitter:description", content="Personal blog about software development and tech"),
           Meta(name="twitter:image", content=f"https://{blog_url}{default_image}"),
           Meta(name="twitter:creator", content="@efels_com"),
           Meta(name="twitter:site", content="@efels_com")
       ]

   image_path = f"/public/images/{post['slug']}.jpg" if post else default_image
   full_image_url = f"https://{blog_url}{image_path}"

   return [
       Meta(property="og:title", content=post["title"]),
       Meta(property="og:description", content=post.get("excerpt", "")),
       Meta(property="og:image", content=full_image_url),
       Meta(property="og:url", content=f"https://{blog_url}/posts/{post['slug']}"),
       Meta(property="og:type", content="article"),
       Meta(name="twitter:card", content="summary"),
       Meta(name="twitter:title", content=post["title"]),
       Meta(name="twitter:description", content=post.get("excerpt", "")),
       Meta(name="twitter:image", content=full_image_url),
       Meta(name="twitter:creator", content="@efels_com")
   ]

# For global headers (site-wide)
og_headers = social_meta(None)
hdrs = Theme.blue.headers() + [MarkdownJS(), HighlightJS()] + og_headers
app, rt = fast_app(hdrs=hdrs, live=True)

def social_links():
    links = [('github', 'https://github.com/danacity'),
             ('mail', 'mailto:Dan@efels.com'),
             ('linkedin', 'https://www.linkedin.com/in/daniel-r-armstrong/'),
             ('twitter', 'https://x.com/efels_com')]  
    return Div(
                *[A(UkIcon(icon, height=16, width=16), href=url, cls="hover:text-primary transition-colors",
                target="_blank" if not url.startswith('mailto:') else None) for icon, url in links],
                cls="flex gap-3 mt-0 mb-1 text-muted-foreground"
                )

def search_bar():
    return A(Input(placeholder='search'))

def gallery_link():
    return A(
        Button(UkIcon('grid', height=16, width=16, stroke_width=2), "My Gallery",
              cls='flex items-center gap-1'),
        href="https://www.gallery.efels.com/", 
        cls=[AT.primary + " hover:bg-secondary hover:text-primary"]
    )

# def theme_switcher():
#     return Div(
#                 A(Button(UkIcon('palette', height=16, width=16, stroke_width=2), "Appearance", cls='flex items-center gap-1'),cls=[AT.primary, "hover:bg-secondary hover:text-primary"]),
#                 DropDownNavContainer(Div(Uk_theme_switcher(), cls="space-y-8 p-8 min-w-[350px] min-h-[150px] bg-background rounded-lg"))
#             )
def theme_switcher():
    return Div(A(Button(UkIcon('palette', height=16, width=16, stroke_width=2), 
                        "Appearance", cls='flex items-center gap-1'), cls=[AT.primary, "hover:bg-secondary hover:text-primary"]),
                DropDownNavContainer(ThemePicker(radii=False, shadows=False, font=False)))

def hamburger_button():
    return Button("☰", cls="hover:bg-primary rounded-lg p-2", 
                 hx_on_click="htmx.toggleClass('#nav-panel', 'hidden')")

def home_button():
    return A(UkIcon('home', height=30, width=30, stroke_width=2), 
            cls=AT.primary + "hover:bg-primary hover:text-secondary rounded-lg p-2", 
            href="/")

def vertical_divider():
    return Div(cls="w-px h-6 bg-primary/30 mx-1")

def header_content():
    return NavContainer(
        DivLAligned(
            Div(hamburger_button(), vertical_divider(), home_button(), cls="flex items-center"),
            Div(H1("Daniel Armstrong", cls=[TextT.primary, "text-2xl font-bold"]), social_links(), cls="flex flex-col")
        ),
        DivRAligned(
            Div(search_bar(),gallery_link(),theme_switcher(),cls="flex flex-col md:flex-row items-end gap-2"),
            cls="gap-5"
        ),
        cls="bg-card border-b border-10 border-primary/50 shadow-lg sticky top-0 rounded-lg z-50 flex items-center justify-between"  # Added flex, items-center, and justify-between
    )

def navigation_panel(posts):
    return NavContainer(
        #NavHeaderLi("Blog Posts", cls=TextT.primary),
        NavHeaderLi("Blog Posts"),
        *[Li(A(post["title"], 
              hx_get=f"/posts/{post['slug']}", 
              hx_target="#main-content",  
              hx_push_url="true", 
              cls="hover:bg-accent")) for post in posts],
        uk_nav=True,
        cls=f"{NavT.secondary} border-r border-primary/50 hidden w-64 mt-4",  # Removed mt-4
        id="nav-panel"
    )

def read_posts():
   posts = []
   posts_dir = Path('posts')
   for file_path in posts_dir.glob('*.md'):
       with open(file_path, 'r') as file:
           content = file.read()
           parts = content.split('---')
           if len(parts) > 2:
               post = yaml.safe_load(parts[1])
               post['slug'] = file_path.stem
               post['content'] = parts[2].strip()
               
               if 'excerpt' not in post:
                   lines = post['content'].split('\n')
                   for line in lines:
                       if line.strip() and not line.strip().startswith('!['):
                           post['excerpt'] = line.strip()
                           break
               
               if 'date' in post:
                   if isinstance(post['date'], str):
                       post['date'] = datetime.fromisoformat(post['date'])
                   elif isinstance(post['date'], date):
                       post['date'] = datetime.combine(post['date'], datetime.min.time())
               
               if not post.get("draft", False):
                   posts.append(post)
   
   return sorted(posts, key=lambda x: x.get('date', datetime.min), reverse=True)

def BlogCard(post):
    def TagList(items, prefix=""): 
        return Div(*[Span(f"{prefix}{item}", 
                         cls="text-[10px] mr-1 px-1.5 bg-primary/20 rounded-full") 
                    for item in items], 
                   cls="flex flex-wrap") if items else ""
                   
    return Card(
        DivLAligned(Div(cls="flex flex-col md:flex-row w-full gap-4")(
                    A(Img(src=f"/public/images/{post['slug']}.jpg"), cls="w-full max-w-48"),
                    P(post["excerpt"], cls="text-muted-foreground"))),
        header=H4(post["title"], cls="text-primary font-bold"),
        footer=Div(
            Span(post["date"].strftime("%b %d, %Y"), cls="text-muted-foreground"),
            Div(
                TagList(post.get('tags', []), "#"),
                TagList(post.get('Diataxis', []), "📖 "),
                cls="flex mx-2"
            ),
            Button("Read More",
                   hx_get=f"/posts/{post['slug']}", 
                   hx_push_url="true",
                   hx_target="#main-content",
                   hx_swap="outerHTML", 
                   cls="bg-primary text-primary-foreground hover:bg-primary/70"),
            cls="flex items-center justify-between"
        ))

@rt('/posts/{slug}')
def get_post(slug: str, request=None):
    with open(f'posts/{slug}.md', 'r') as file:
        content = file.read()
    frontmatter = yaml.safe_load(content.split('---')[1])
    frontmatter['slug'] = slug
    post_content = content.split('---')[2]

    content = Div(
        *social_meta("twitter", frontmatter),  # Add meta tags for the post
        *social_meta("og", frontmatter),
        H1(frontmatter["title"], cls="text-4xl font-bold mb-2"),
        P(frontmatter['date'].strftime("%B %d, %Y"), cls="text-muted-foreground mb-4"),
        Div(render_md(post_content), cls="prose max-w-none"),
        cls="w-full px-8 py-4",
        id="main-content"
    )

    return content if request.headers.get('HX-Request') else Container(header_content(), content)

# def blog_grid(posts):
#     return Grid(*[BlogCard(p) for p in posts],
#                 cols_sm=1, cols_md=1, cols_lg=2, cols_xl=3, 
#                 id="main-content",
#                 cls=[NavT.secondary, 'gap-4 mt-4 ml-4'])

def blog_grid(posts, active_tag=None, active_diataxis=None):
    unique_tags = sorted(set(tag for post in posts if post.get('tags') for tag in post['tags']))
    unique_diataxis = sorted(set(d for post in posts if post.get('Diataxis') for d in post['Diataxis']))
    
    def get_button_class(is_active):
        base_class = "px-2 py-1 rounded-lg text-xs "
        return base_class + ("bg-primary text-primary-foreground" if is_active else "bg-primary/20 hover:bg-primary hover:text-primary-foreground")
    
    return Div(
        Div(
            Button("All", hx_get="/filter", hx_target="#main-content",cls=get_button_class(not active_tag and not active_diataxis)),
            vertical_divider(),
            Div(
                Span("Tags:", cls="text-sm font-bold mr-2"),
                *[Button(tag, hx_get=f"/filter?tag={tag}", hx_target="#main-content", cls=get_button_class(tag == active_tag)
                ) for tag in unique_tags],
                cls="flex items-center gap-2"
            ),
            vertical_divider(),
            Div(
                Span("Diataxis:", cls="text-sm font-bold mr-2"),
                *[Button(d, hx_get=f"/filter?diataxis={d}", hx_target="#main-content",cls=get_button_class(d == active_diataxis)) for d in unique_diataxis],
                cls="flex items-center gap-2"
            ),
            cls="flex items-center mb-4"
        ),
        Grid(
            *[BlogCard(p) for p in posts],
            cols_sm=1, cols_md=1, cols_lg=2, cols_xl=3,
            cls="gap-4"
        ),
        id="main-content"
    )

@rt('/filter')
def filter_posts(tag: str = None, diataxis: str = None):
    posts = read_posts()
    
    if tag:
        filtered_posts = [p for p in posts if p.get('tags') and tag in p['tags']]
        return blog_grid(filtered_posts, active_tag=tag)
    elif diataxis:
        filtered_posts = [p for p in posts if p.get('Diataxis') and diataxis in p['Diataxis']]
        return blog_grid(filtered_posts, active_diataxis=diataxis)
    
    return blog_grid(posts)

@rt
def index():
    posts = read_posts()
    return Title('Efels Blog'), Container(
        *social_meta(None),     
        header_content(),
        Div(
            navigation_panel(posts),
            blog_grid(posts),
            cls="flex items-start"
        )
    )

if __name__ == "__main__":
   serve()
