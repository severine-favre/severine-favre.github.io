---
layout: default
title: Homepage
---

<h1>Sélection d'articles</h1>

<ul>
  {% assign pinned = site.posts | where_exp:"item", "item.pinned == true" %}	

  {% for post in pinned %}
    <li>
      <h2><a href="{{ post.url }}">{{ post.title }} 📌</a></h2>
      {{ post.excerpt }}
    </li>
  {% endfor %}

  {% for post in unpinned %}
    <li>
      <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
      {{ post.excerpt }}
    </li>
  {% endfor %}
  
</ul>

