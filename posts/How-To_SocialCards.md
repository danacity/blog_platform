---
title: How-to add Social (Twitter) Cards
date: 2025-02-16T10:30:00+01:00
draft: false
excerpt: How to add Social Cards to your FastHTML blog
tags:
  - FastHTML
Diataxis:
  - How-To
---
# Adding Social Cards to Your Website
## So what is a Social Card
Social cards (also known as social media preview cards) are visual previews that automatically appear when you share a link on social media platforms. They transform plain URLs into rich visual content that includes: 
- Page title 
- Description 
- Featured image 
- Website URL 
When implemented correctly, social cards make your content more engaging and increase click-through rates on social media platforms. 

Jeremy shared the following link for Twitter on Discord
[About Twitter Cards | Docs | Twitter Developer Platform](https://developer.x.com/en/docs/x-for-websites/cards/overview/abouts-cards)

## Implementation by Platform  
### LinkedIn 
LinkedIn uses Open Graph (OG) meta tags to generate social cards. Add these meta tags to your HTML `<head>` section:

```html
<meta property="og:title" content="Your Page Title" /> 
<meta property="og:description" content="A brief description of your page." /> 
<meta property="og:image" content="https://example.com/image.jpg" /> 
<meta property="og:url" content="https://example.com/page" /> 
<meta property="og:type" content="website" />
```
 
 you can use to validate your link:   https://www.linkedin.com/post-inspector/inspect/
### Twitter
Twitter on the other hand has specific meta tags:
```html
<meta name="twitter:card" content="summary" /> 
<meta name="twitter:title" content="Your Page Title" /> 
<meta name="twitter:description" content="Your page description" /> 
<meta name="twitter:image" content="https://example.com/image.jpg" />
<meta name="twitter:creator" content="@yourusername" />
```

I couldn't get the twitter validation tool to work, so I ended up just using the creation of a new post, if it works, You put in the link and boom your image, title, description, just show up, like magic. 
![[Pasted image 20250221103601.png]]

### FastHTML Function
The key is how you actually do it here is how I did:

```python
def social_meta(platform, post=None, type="website"):
   blog_url = "www.blog.efels.com"
   default_image = "/public/images/blog-default.jpg"
   if post is None:  # Homepage case
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
```

you will also want to add it to your index function
```python
@rt
def index():
    posts = read_posts()
    return Title('Efels Blog'), Container(
        *social_meta(None),    
        header_content(),
        Div(
            navigation_panel(posts),
            blog_grid(posts),
            cls="flex items-start"))
```