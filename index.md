---
layout: default
title: Homepage
---

<h1>Sélection d'articles</h1>

<ul>
  {% assign pinned = site.posts | where: "pinned", true %}	

  {% for post in pinned %}
    <li class="pinned">
      <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
      {{ post.excerpt }}
    </li>
  {% endfor %}

  {% assign unpinned = site.posts | where: "pinned", nil %}	
  {% for post in unpinned %}
    <li>
      <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
      {{ post.excerpt }}
    </li>
  {% endfor %}
  
</ul>

