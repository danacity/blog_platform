from fasthtml.common import *
from monsterui.all import *
from datetime import datetime, date
from pathlib import Path
import yaml
from fasthtml.components import Uk_theme_switcher

blog_url = "www.blog.efels.com"
default_image = "/public/images/blog-default.jpg"

# def social_meta(platform, post=None, type="website"):
#     image_path = default_image if post is None else f"/public/images/{post['slug']}.jpg"

#     if post is None:  # Global headers
#         return [
#             Meta(property="og:title", content="Dan's Blog"),
#             Meta(property="og:image", content=f"https://{blog_url}{image_path}"),
#             Meta(property="og:url", content=f"https://{blog_url}"),
#             Meta(property="og:type", content=type),
#             Meta(name="twitter:card", content="summary"),
#             Meta(name="twitter:creator", content="@efels_com"),
#             Meta(name="twitter:site", content="@efels_com"),
#             Meta(name="twitter:domain", content=blog_url)
#         ]
    
#     return [
#         *([Meta(property="og:type", content="article")] if platform == "og" else []),
#         Meta(**{"property" if platform == "og" else "name": f"{platform}:title"}, content=post["title"]),
#         Meta(**{"property" if platform == "og" else "name": f"{platform}:description"}, content=post.get("excerpt", "")),
#         Meta(**{"property" if platform == "og" else "name": f"{platform}:image"}, content=f"https://{blog_url}{image_path}"),
#         Meta(**{"property" if platform == "og" else "name": f"{platform}:url"}, content=f"https://{blog_url}/posts/{post['slug']}")
#     ]
def social_meta(platform, post=None, type="website"):
    blog_url = "www.blog.efels.com"  # Move this to top of file with other constants
    default_image = "/public/images/blog-default.jpg"
    
    # Build full image URL
    image_path = default_image if post is None else f"/public/images/{post['slug']}.jpg"
    full_image_url = f"https://{blog_url}{image_path}"

    if post is None:  # Global headers
        return [
            Meta(property="og:title", content="Dan's Blog"),
            Meta(property="og:image", content=full_image_url),
            Meta(property="og:url", content=f"https://{blog_url}"),
            Meta(property="og:type", content=type),
            Meta(name="twitter:card", content="summary"),
            Meta(name="twitter:creator", content="@efels_com"),
            Meta(name="twitter:site", content="@efels_com"),
            Meta(name="twitter:domain", content=blog_url)
        ]
    
    # Post-specific metadata
    return [
        *([Meta(property="og:type", content="article")] if platform == "og" else []),
        Meta(**{"property" if platform == "og" else "name": f"{platform}:title"}, content=post["title"]),
        Meta(**{"property" if platform == "og" else "name": f"{platform}:description"}, content=post.get("excerpt", "")),
        Meta(**{"property" if platform == "og" else "name": f"{platform}:image"}, content=full_image_url),
        Meta(**{"property" if platform == "og" else "name": f"{platform}:url"}, content=f"https://{blog_url}/posts/{post['slug']}")
    ]

# For global headers (site-wide)
#og_headers = social_meta(None)
hdrs = Theme.blue.headers() + [MarkdownJS(), HighlightJS()] #+ og_headers
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

def theme_switcher():
    return Div(
                A(Button(UkIcon('palette', height=16, width=16, stroke_width=2), "Appearance", cls='flex items-center gap-1'),cls=[AT.primary, "hover:bg-secondary hover:text-primary"]),
                DropDownNavContainer(Div(Uk_theme_switcher(), cls="space-y-8 p-8 min-w-[350px] min-h-[150px] bg-background rounded-lg"))
            )

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
    return Card(
        DivLAligned(Div(cls="flex flex-col md:flex-row w-full gap-4")(
                    A(Img(src=f"/public/images/{post['slug']}.jpg"), cls="w-full max-w-48"),
                    P(post["excerpt"], cls="text-muted-foreground"))),
        header = H4(post["title"], cls="text-primary font-bold"),
        footer = DivFullySpaced(
            Span(post["date"].strftime("%b %d, %Y"), cls="text-muted-foreground"),
            Button("Read More",
                   hx_get=f"/posts/{post['slug']}", 
                   hx_push_url="true",
                   hx_target="#main-content",
                   hx_swap="outerHTML", 
                   cls="bg-primary text-primary-foreground hover:bg-primary/70")
        ))

@rt('/posts/{slug}')
def get_post(slug: str):
    with open(f'posts/{slug}.md', 'r') as file:
        content = file.read()
    post_content = content.split('---')[2]
    frontmatter = yaml.safe_load(content.split('---')[1])
    frontmatter['slug'] = slug  # Make sure slug is in frontmatter
    
    return Title(frontmatter["title"]), Div(
        *social_meta("twitter", frontmatter),  # Pass complete frontmatter
        *social_meta("og", frontmatter),       # Pass complete frontmatter
        H1(frontmatter["title"], cls="text-4xl font-bold mb-2"),
        P(frontmatter['date'].strftime("%B %d, %Y"), cls="text-muted-foreground mb-4"),
        Div(render_md(post_content), cls="prose max-w-none"),
        cls="w-full px-8 py-4",
        id="main-content"
    )

def blog_grid(posts):
    return Grid(*[BlogCard(p) for p in posts],
                cols_sm=1, cols_md=1, cols_lg=2, cols_xl=3, 
                id="main-content",
                cls=[NavT.secondary, 'gap-4 mt-4 ml-4'])

@rt
def index():
    posts = read_posts()
    return Title('Efels Blog'), Container(
        *social_meta("twitter"),  # Add global social meta tags
        *social_meta("og"),      # Add global social meta tags
        header_content(),
        Div(
            navigation_panel(posts),
            blog_grid(posts),
            cls="flex items-start"
        )
    )

if __name__ == "__main__":
   serve()
