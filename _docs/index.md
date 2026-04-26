# Documentation

Browse in-depth articles and guides on various topics.

| Date | Title |
|------|-------|
{% assign docs = site.pages %} {% for d in docs %}{% if d.path contains "_docs" and d.title %}| {{ d.date | date: "%Y-%m-%d" }} | [{{ d.title }}]({{ d.url | relative_url }}) |{% endif %}{% endfor %}
