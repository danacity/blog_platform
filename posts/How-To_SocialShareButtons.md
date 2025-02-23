---
title: How-to add Social Sharing Buttons
date: 2025-02-16T10:30:00+01:00
draft: false
excerpt: If you want people to share you work, make it easy give them a button. 
tags:
  - FastHTML
Diataxis:
  - How-To
---

## Sharing is Caring 
There is really nothing fancy about adding sharing buttons, but in case you want to save a little time when creating your own here is my version: 
![Social Share Buttons Gif](/public/images/shareButtons.gif) 

```python
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
```
I choose to create share buttons for twitter/Linkedin/and blueSky, but since MonserUI(UKIcon-Lucide) doesn't have a butterfly I choose the flower. I also found the bluesky links to not work for every page, so it might be worth modifying this in the future, if you want a better icon this might help: https://www.pietschsoft.com/post/2024/11/22/how-to-add-share-on-bluesky-action-intent-button-to-your-website

To add them at the top of my blog posts I added them to my get_post function:
```python
@rt('/posts/{slug}')
def get_post(slug: str, request=None):
    with open(f'posts/{slug}.md', 'r') as file:
        content = file.read()
    frontmatter = yaml.safe_load(content.split('---')[1])
    frontmatter['slug'] = slug
    post_content = content.split('---')[2]

    content = Div(
        *social_meta("twitter", frontmatter), 
        H1(frontmatter["title"], cls="text-4xl font-bold mb-2"),
        P(frontmatter['date'].strftime("%B %d, %Y"), cls="text-muted-foreground mb-4"),
        ShareButtons(slug, frontmatter["title"]),  
        Div(render_md(post_content), cls="prose max-w-none"),
        cls="w-full px-8 py-4",
        id="main-content"
    )

    return content if request.headers.get('HX-Request') else Container(header_content(), content)
```

If you want to get a little fancy you might want to look at [How-To add Social card](How-To_SocialCards.md) Which add a little more styling when someone shares your posts.  

![Social Share Gif](/public/images/social_share.gif)

