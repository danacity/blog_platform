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

def ShareButtons(slug, title):
    base_url = "https://www.blog.efels.com"  # Replace with your actual base URL
    url = f"{base_url}/posts/{slug}"
    
    def ShareAnchor(icon, href, tooltip):
        return A(UkIcon(icon, height=16, width=16), 
                href=href, 
                target="_blank", 
                cls="hover:text-primary transition-colors p-2",
                uk_tooltip=tooltip)
    
    copy_script = """
        navigator.clipboard.writeText(window.location.href);
        alert('Link copied to clipboard!');
    """
    
    return Div(
        ShareAnchor("twitter", f"https://twitter.com/intent/tweet?text={title}&url={url}", "Share on Twitter"),
        ShareAnchor("linkedin", f"https://www.linkedin.com/sharing/share-offsite/?url={url}", "Share on LinkedIn"),
        ShareAnchor("flower", f"https://bsky.app/intent/compose?text={title}&url={url}", "Share on Bluesky"),
        Button(UkIcon("link", height=16, width=16), 
               cls="hover:text-primary transition-colors p-2",
               uk_tooltip="Copy link",
               onclick=copy_script),
        cls="flex items-center gap-2"
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

@rt('/public/{rest_of_path:path}')
def serve_public(rest_of_path: str):
    return FileResponse(f"public/{rest_of_path}")

def mailing_list_signup():
    return Div(
        H3("Subscribe to my Newsletter", cls="text-lg font-bold mb-2 text-primary"),
        P("Get the latest updates directly to your inbox", 
          cls="text-sm text-muted-foreground mb-3"),
        Form(
            Div(
                Input(
                    type="email", 
                    placeholder="Your email address", 
                    required=True,
                    cls="w-full p-2 border border-primary/30 rounded-md mb-2"
                ),
                Button(
                    "Subscribe", 
                    type="submit",
                    cls="w-full bg-primary text-primary-foreground hover:bg-primary/80 p-2 rounded-md"
                ),
                cls="flex flex-col"
            ),
            # Replace with your actual form submission endpoint
            action="/subscribe", 
            method="POST"
        ),
        cls="bg-card p-4 rounded-lg shadow-sm border border-primary/20 mb-4"
    )

# 2. Create a collapsible Calendly widget
def collapsible_calendly():
    toggle_script = """
        const calContainer = document.getElementById('calendly-container');
        const toggleButton = document.getElementById('calendly-toggle');
        if (calContainer.classList.contains('hidden')) {
            calContainer.classList.remove('hidden');
            toggleButton.innerHTML = 'Hide booking calendar';
        } else {
            calContainer.classList.add('hidden');
            toggleButton.innerHTML = 'Schedule a call with me';
        }
    """
    
    return Div(
        Button(
            "Schedule a call with me",
            id="calendly-toggle",
            cls="w-full bg-secondary text-secondary-foreground hover:bg-secondary/80 p-2 rounded-md mb-2",
            onclick=toggle_script
        ),
        Div(
            Div(
                cls="calendly-inline-widget", 
                data_url="https://calendly.com/efels/30min",
                style="min-width:100%;height:600px;"
            ),
            Script(
                src="https://assets.calendly.com/assets/external/widget.js",
                type="text/javascript",
                async_=True
            ),
            cls="hidden",
            id="calendly-container"
        ),
        cls="bg-card p-4 rounded-lg shadow-sm border border-primary/20 mb-4"
    )


# @rt('/posts/{slug}')
# def get_post(slug: str, request=None):
#     with open(f'posts/{slug}.md', 'r') as file:
#         parts = file.read().split('---', 2)
#         if len(parts) != 3:
#             return "Invalid post format"
            
#     frontmatter = yaml.safe_load(parts[1])
#     frontmatter['slug'] = slug
#     post_content = parts[2]
    
#     # Create the main content
#     post_content_div = Div(
#         H1(frontmatter["title"], cls="text-4xl font-bold mb-2"),
#         P(frontmatter['date'].strftime("%B %d, %Y"), cls="text-muted-foreground mb-4"),
#         ShareButtons(slug, frontmatter["title"]),  
#         Div(render_md(post_content), cls="prose max-w-none"),
#         cls="w-full lg:w-3/4 px-8 py-4"
#     )
    
#     # Create the right sidebar with Calendly
#     sidebar = Div(
#         calendly_widget(),
#         cls="hidden lg:block lg:w-1/4 p-4 sticky top-20 self-start"
#     )
    
#     # Combine main content and sidebar
#     content = Div(
#         *social_meta("twitter", frontmatter),
#         Div(
#             post_content_div,
#             sidebar,
#             cls="flex flex-wrap",
#             id="main-content"
#         )
#     )

#     return content if request.headers.get('HX-Request') else Container(header_content(), content)
def more_dropdown():
    return Div(
        Button(
            DivLAligned(
                UkIcon('more-horizontal', height=16, width=16, stroke_width=2),
                "More",
                cls='flex items-center gap-1'
            ),
            cls=[ButtonT.ghost, "hover:bg-secondary hover:text-primary"]
        ),
        DropDownNavContainer(
            Li(A(
                DivLAligned(UkIcon('mail', height=16, width=16), "Subscribe to Newsletter"),
                href="#subscribe-section",
                cls="hover:bg-accent"
            )),
            Li(A(
                DivLAligned(UkIcon('calendar', height=16, width=16), "Book a Meeting"),
                onclick="document.getElementById('calendly-toggle').click(); return false;",
                cls="hover:bg-accent cursor-pointer"
            ))
        )
    )

def header_content():
    return NavContainer(
        DivLAligned(
            Div(hamburger_button(), vertical_divider(), home_button(), cls="flex items-center"),
            Div(H1("Daniel Armstrong", cls=[TextT.primary, "text-2xl font-bold"]), social_links(), cls="flex flex-col")
        ),
        DivRAligned(
            Div(search_bar(), gallery_link(), theme_switcher(), more_dropdown(), cls="flex flex-col md:flex-row items-end gap-2"),
            cls="gap-5"
        ),
        cls="bg-card border-b border-10 border-primary/50 shadow-lg sticky top-0 rounded-lg z-50 flex items-center justify-between"
    )

def page_contents():
    return Div(
        H3("Page Contents", cls="text-lg font-bold mb-2 text-primary"),
        Div(
            NavContainer(
                id="post-toc",
                uk_scrollspy_nav="closest: li; scroll: true; cls: uk-active",
                cls="max-h-[300px] overflow-y-auto uk-nav-default"
            ),
            # This script generates the table of contents with HTMX support
            Script("""
            // Function to initialize the table of contents
            function initializeTableOfContents() {
                // Get all headings from the post content
                const contentDiv = document.querySelector('.prose');
                if (!contentDiv) return; // Exit if no prose content is found
                
                const headings = Array.from(contentDiv.querySelectorAll('h2, h3, h4'));
                const tocContainer = document.getElementById('post-toc');
                
                if (!tocContainer) return; // Exit if TOC container not found
                
                // Clear any existing content
                tocContainer.innerHTML = '';
                
                // Process headings to add IDs if they don't have them
                headings.forEach(heading => {
                    if (!heading.id) {
                        const id = heading.textContent
                            .toLowerCase()
                            .replace(/[^a-z0-9]+/g, '-')
                            .replace(/(^-|-$)/g, '');
                        heading.id = id;
                    }
                });
                
                // Create TOC entries
                headings.forEach(heading => {
                    const level = parseInt(heading.tagName.charAt(1));
                    const listItem = document.createElement('li');
                    const link = document.createElement('a');
                    
                    link.textContent = heading.textContent;
                    link.href = '#' + heading.id;
                    
                    // Add indentation based on heading level
                    listItem.style.paddingLeft = (level - 2) * 12 + 'px';
                    listItem.appendChild(link);
                    tocContainer.appendChild(listItem);
                });
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', initializeTableOfContents);
            
            // Initialize after HTMX content swap
            document.body.addEventListener('htmx:afterSwap', function(event) {
                // Only run if the main content was swapped
                if (event.detail.target.id === 'main-content') {
                    // Small delay to ensure DOM is fully updated
                    setTimeout(initializeTableOfContents, 50);
                }
            });
            """),
            cls="space-y-2"
        ),
        cls="bg-card p-4 rounded-lg shadow-sm border border-primary/20"
    )

def create_filter_container(posts, active_tag=None, active_diataxis=None):
    unique_tags = sorted(set(tag for post in posts if post.get('tags') for tag in post['tags']))
    unique_diataxis = sorted(set(d for post in posts if post.get('Diataxis') for d in post['Diataxis']))
    
    return NavContainer(
        NavHeaderLi("Filters"),
        Div(
            TabContainer(
                Li(A("All", href="#all-tab", id="all-tab-link", cls="uk-active")),
                Li(A("Tags", href="#tags-tab", id="tags-tab-link")),
                Li(A("Diataxis", href="#diataxis-tab", id="diataxis-tab-link")),
                uk_switcher="connect: #filter-tabs-container; animation: uk-animation-fade",
                alt=True,
                cls="uk-tab-small"
            ),
            Div(
                Li(
                    NavContainer(
                        Li(A("All Posts", 
                            hx_get="/filter", 
                            hx_target="#main-content",
                            cls="hover:bg-accent"))
                    ),
                    cls="uk-active"
                ),
                Li(
                    NavContainer(
                        *[Li(A(tag, 
                              hx_get=f"/filter?tag={tag}", 
                              hx_target="#main-content",
                              cls="hover:bg-accent")) for tag in unique_tags]
                    )
                ),
                Li(
                    NavContainer(
                        *[Li(A(d, 
                              hx_get=f"/filter?diataxis={d}", 
                              hx_target="#main-content",
                              cls="hover:bg-accent")) for d in unique_diataxis]
                    )
                ),
                id="filter-tabs-container",
                cls="uk-switcher"
            ),
            cls="mb-4"
        ),
        cls=f"{NavT.secondary} bg-blue-50 dark:bg-blue-900/20 rounded-lg shadow-sm m-2 p-4"
    )

def create_page_contents_container():
    return NavContainer(
        NavHeaderLi("Page Contents"),
        NavContainer(
            id="post-toc",
            uk_scrollspy_nav="closest: li; scroll: true; cls: uk-active",
            cls="uk-nav max-h-[200px] overflow-y-auto"
        ),
        cls=f"{NavT.secondary} bg-green-50 dark:bg-green-900/20 rounded-lg shadow-sm m-2 p-4"
    )

def create_newsletter_container():
    return NavContainer(
        NavHeaderLi("Newsletter"),
        Li(Form(
            Input(
                type="email", 
                placeholder="Your email", 
                required=True,
                cls="w-full p-2 border border-primary/30 rounded-md mb-2"
            ),
            Button(
                "Subscribe", 
                type="submit",
                cls="w-full bg-primary text-primary-foreground hover:bg-primary/80 p-2 rounded-md"
            ),
            action="/subscribe", 
            method="POST",
            cls="space-y-3"
        )),
        cls=f"{NavT.secondary} bg-purple-50 dark:bg-purple-900/20 rounded-lg shadow-sm m-2 p-4"
    )

def create_meeting_container():
    return NavContainer(
        NavHeaderLi("Book a Meeting"),
        Li(
            Button(
                "Schedule a call",
                id="nav-calendly-toggle",
                cls="w-full bg-secondary text-secondary-foreground hover:bg-secondary/80 p-2 rounded-md",
                onclick="const mainToggle = document.getElementById('calendly-toggle'); if(mainToggle) mainToggle.click(); return false;"
            ),
            cls="p-2"
        ),
        cls=f"{NavT.secondary} bg-amber-50 dark:bg-amber-900/20 rounded-lg shadow-sm m-2 p-4"
    )

def create_posts_container(posts):
    return NavContainer(
        NavHeaderLi("Latest Posts"),
        *[Li(A(post["title"], 
              hx_get=f"/posts/{post['slug']}", 
              hx_target="#main-content",  
              hx_push_url="true", 
              cls="hover:bg-accent")) for post in posts[:5]],
        cls=f"{NavT.secondary} bg-gray-50 dark:bg-gray-800/40 rounded-lg shadow-sm m-2 p-4"
    )

def create_posts_container(posts):
    return NavContainer(
        NavHeaderLi("Latest Posts"),
        *[Li(A(post["title"], 
              hx_get=f"/posts/{post['slug']}", 
              hx_target="#main-content",  
              hx_push_url="true", 
              cls="hover:bg-accent")) for post in posts[:5]],
        cls=f"{NavT.secondary} bg-gray-50 dark:bg-gray-800/40 rounded-lg shadow-sm m-2 p-4"
    )

def navigation_panel(posts, active_tag=None, active_diataxis=None):
    return Div(
        create_filter_container(posts, active_tag, active_diataxis),
        create_page_contents_container(),
        create_newsletter_container(),
        create_meeting_container(),
        create_posts_container(posts),
        cls="border-r border-primary/50 overflow-y-auto max-h-screen",
        style="width: 30rem;",  # Using inline style to set width
        id="nav-panel"
    )
# 3. Update the get_post function to include the enhanced sidebar
@rt('/posts/{slug}')
def get_post(slug: str, request=None):
    with open(f'posts/{slug}.md', 'r') as file:
        parts = file.read().split('---', 2)
        if len(parts) != 3:
            return "Invalid post format"
            
    frontmatter = yaml.safe_load(parts[1])
    frontmatter['slug'] = slug
    post_content = parts[2]
    
    # Create the main content
    post_content_div = Div(
        H1(frontmatter["title"], cls="text-4xl font-bold mb-2"),
        P(frontmatter['date'].strftime("%B %d, %Y"), cls="text-muted-foreground mb-4"),
        ShareButtons(slug, frontmatter["title"]),  
        Div(render_md(post_content), cls="prose max-w-none"),
        cls="w-full lg:w-3/4 px-8 py-4"
    )
    
    # Create the right sidebar (without the calendly widget)
    sidebar = Div(
        mailing_list_signup(),
        page_contents(),
        cls="hidden lg:block lg:w-1/4 p-4 sticky top-20 self-start"
    )
    
    # Combine main content and sidebar
    content = Div(
        *social_meta("twitter", frontmatter),
        Div(
            post_content_div,
            sidebar,
            cls="flex flex-wrap",
            id="main-content"
        )
    )

    return content if request.headers.get('HX-Request') else Container(header_content(), content)

# 4. Add a route for handling newsletter subscriptions
@rt('/subscribe', methods=['POST'])
async def handle_subscription(request):
    # Get form data using the request object
    form_data = await request.form()
    email = form_data.get('email', '')
    
    # For now, just return a success message
    return Div(
        H2("Thank you for subscribing!"),
        P(f"We've added {email} to our newsletter."),
        Button("Return Home", hx_get="/", hx_target="body"),
        cls="p-8 text-center"
    )

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
